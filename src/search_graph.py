import json
from pathlib import Path
from typing import Any, Dict

from node_grounding import ground_conditions
from graph_retriever import retrieve_graph


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "data" / "retrieved_graph.json"


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    raw_conditions = {
        "Grade": "高校3年生",
        "Field": None,
        "Unit": None,
        "ICT_Hardware": None,
        "ICT_Software": "Instagram",
        "ICT_Artifact": None,
        "ICT_Function": None,
        "Educational_Opportunity": None,
        "Educational_Effect": "観察への意欲を高めたい",
    }

    grounded_conditions = ground_conditions(raw_conditions, top_k=3)

    retrieved_graph = retrieve_graph(
        grounded_conditions=grounded_conditions,
        row_limit=300,
    )

    output = {
        "raw_conditions": raw_conditions,
        "grounded_conditions": grounded_conditions,
        "retrieved_graph": retrieved_graph,
    }

    save_json(output, OUTPUT_PATH)

    print("=== GraphRAG Retrieval Completed ===")
    print(f"保存先: {OUTPUT_PATH}")
    print(f"検索条件: {grounded_conditions}")
    print(f"nodes: {len(retrieved_graph['nodes'])}")
    print(f"edges: {len(retrieved_graph['edges'])}")
    print(f"paths: {len(retrieved_graph['paths'])}")
    print(f"coverage: {retrieved_graph['coverage']}")
    print(f"retrieval_groups: {retrieved_graph['retrieval_groups']}")


if __name__ == "__main__":
    main()