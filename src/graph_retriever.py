import os
from itertools import combinations
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv
from neo4j import GraphDatabase

from graph_schema import CONDITION_LABELS, PATH_PATTERNS


load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "ictmap")


def get_driver():
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    )


def get_active_labels(grounded_conditions: Dict[str, List[str]]) -> List[str]:
    return [label for label in CONDITION_LABELS if grounded_conditions.get(label)]


def build_params(
    grounded_conditions: Dict[str, List[str]],
    active_labels: List[str],
    row_limit: int,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    for label in CONDITION_LABELS:
        params[label] = grounded_conditions.get(label, [])
        params[f"has_{label}"] = label in active_labels

    params["row_limit"] = row_limit
    return params


def build_union_query() -> str:
    union_blocks = []

    for pattern in PATH_PATTERNS:
        block = f"""
        {pattern["cypher"]}
        OPTIONAL MATCH (pr)-[rg:TARGETS_GRADE]->(g:Grade)
        OPTIONAL MATCH (pr)-[rf:TARGETS_FIELD]->(f:Field)
        OPTIONAL MATCH (pr)-[ru:TARGETS_UNIT]->(u:Unit)
        RETURN
            p,
            [r IN [rg, rf, ru] WHERE r IS NOT NULL] AS context_rels,
            paper,
            pr,
            g,
            f,
            u,
            h,
            s,
            a,
            func,
            opp,
            eff,
            "{pattern["path_type"]}" AS path_type
        """
        union_blocks.append(block)

    return "\nUNION\n".join(union_blocks)


def run_subgraph_query(
    session,
    grounded_conditions: Dict[str, List[str]],
    active_labels: List[str],
    row_limit: int = 300,
) -> Dict[str, Any]:
    params = build_params(grounded_conditions, active_labels, row_limit)
    union_query = build_union_query()

    query = f"""
    CALL () {{
        {union_query}
    }}

    WITH
        p,
        context_rels,
        paper,
        pr,
        g,
        f,
        u,
        h,
        s,
        a,
        func,
        opp,
        eff,
        path_type

    WHERE
        ($has_Grade = false OR g.name IN $Grade)
        AND ($has_Field = false OR f.name IN $Field)
        AND ($has_Unit = false OR u.name IN $Unit)
        AND ($has_ICT_Hardware = false OR h.name IN $ICT_Hardware)
        AND ($has_ICT_Software = false OR s.name IN $ICT_Software)
        AND ($has_ICT_Artifact = false OR a.name IN $ICT_Artifact)
        AND ($has_ICT_Function = false OR func.name IN $ICT_Function)
        AND ($has_Educational_Opportunity = false OR opp.name IN $Educational_Opportunity)
        AND ($has_Educational_Effect = false OR eff.name IN $Educational_Effect)

    RETURN
        path_type,
        [n IN nodes(p) |
            {{
                id: elementId(n),
                labels: labels(n),
                properties: properties(n)
            }}
        ] AS path_nodes,
        [r IN relationships(p) |
            {{
                id: elementId(r),
                type: type(r),
                source_id: elementId(startNode(r)),
                target_id: elementId(endNode(r)),
                properties: properties(r)
            }}
        ] AS path_edges,
        [r IN context_rels |
            {{
                id: elementId(r),
                type: type(r),
                source_id: elementId(startNode(r)),
                target_id: elementId(endNode(r)),
                properties: properties(r)
            }}
        ] AS context_edges,
        [r IN context_rels |
            {{
                id: elementId(endNode(r)),
                labels: labels(endNode(r)),
                properties: properties(endNode(r))
            }}
        ] AS context_nodes
    LIMIT $row_limit
    """

    records = session.run(query, params)

    nodes: Dict[str, Dict[str, Any]] = {}
    edges: Dict[str, Dict[str, Any]] = {}
    paths: Dict[Tuple[str, ...], Dict[str, Any]] = {}

    for record in records:
        path_nodes = record["path_nodes"] + record["context_nodes"]
        path_edges = record["path_edges"] + record["context_edges"]

        for node in path_nodes:
            nodes[node["id"]] = node

        for edge in path_edges:
            edges[edge["id"]] = edge

        edge_ids = [edge["id"] for edge in record["path_edges"]]
        path_key = tuple(edge_ids)

        paths[path_key] = {
            "path_type": record["path_type"],
            "node_ids": [node["id"] for node in record["path_nodes"]],
            "edge_ids": edge_ids,
        }

    return {
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
        "paths": list(paths.values()),
    }


def merge_graph(
    base_graph: Dict[str, Any],
    subgraph: Dict[str, Any],
    match_level: int,
    matched_conditions: List[str],
) -> None:
    for node in subgraph["nodes"]:
        base_graph["nodes"][node["id"]] = node

    for edge in subgraph["edges"]:
        base_graph["edges"][edge["id"]] = edge

    for path in subgraph["paths"]:
        path_key = tuple(path["edge_ids"])
        base_graph["paths"][path_key] = {
            **path,
            "match_level": match_level,
            "matched_conditions": matched_conditions,
        }


def retrieve_graph(
    grounded_conditions: Dict[str, List[str]],
    row_limit: int = 300,
) -> Dict[str, Any]:
    active_labels = get_active_labels(grounded_conditions)

    context_graph = {
        "nodes": {},
        "edges": {},
        "paths": {},
    }

    retrieval_groups: List[Dict[str, Any]] = []
    covered_labels = set()

    if not active_labels:
        return {
            "nodes": [],
            "edges": [],
            "paths": [],
            "retrieval_groups": [],
            "coverage": {
                "requested_conditions": [],
                "covered_conditions": [],
                "uncovered_conditions": [],
            },
        }

    driver = get_driver()

    with driver.session(database=NEO4J_DATABASE) as session:
        for size in range(len(active_labels), 0, -1):
            combos = [list(c) for c in combinations(active_labels, size)]

            if covered_labels:
                uncovered = set(active_labels) - covered_labels
                combos = [combo for combo in combos if set(combo) & uncovered]

            for combo_labels in combos:
                subgraph = run_subgraph_query(
                    session=session,
                    grounded_conditions=grounded_conditions,
                    active_labels=combo_labels,
                    row_limit=row_limit,
                )

                if not subgraph["nodes"]:
                    continue

                merge_graph(
                    base_graph=context_graph,
                    subgraph=subgraph,
                    match_level=size,
                    matched_conditions=combo_labels,
                )

                retrieval_groups.append({
                    "match_level": size,
                    "matched_conditions": combo_labels,
                    "node_count": len(subgraph["nodes"]),
                    "edge_count": len(subgraph["edges"]),
                    "path_count": len(subgraph["paths"]),
                })

                covered_labels.update(combo_labels)

            if covered_labels == set(active_labels):
                break

    driver.close()

    return {
        "nodes": list(context_graph["nodes"].values()),
        "edges": list(context_graph["edges"].values()),
        "paths": list(context_graph["paths"].values()),
        "retrieval_groups": retrieval_groups,
        "coverage": {
            "requested_conditions": active_labels,
            "covered_conditions": sorted(list(covered_labels)),
            "uncovered_conditions": sorted(list(set(active_labels) - covered_labels)),
        },
    }