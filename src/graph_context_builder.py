import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "data" / "retrieved_graph.json"
OUTPUT_PATH = BASE_DIR / "data" / "graph_context.txt"


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def has_label(node: Dict[str, Any], label: str) -> bool:
    return label in node.get("labels", [])


def get_primary_label(node: Dict[str, Any]) -> str:
    labels = node.get("labels", [])
    return labels[0] if labels else "Unknown"


def get_node_name(node: Dict[str, Any]) -> str:
    props = node.get("properties", {})
    return (
        props.get("title")
        or props.get("name")
        or props.get("practice_id")
        or props.get("paper_id")
        or ""
    )


def add_unique(target: List[str], value: str) -> None:
    if value and value not in target:
        target.append(value)


def format_node(node: Dict[str, Any]) -> str:
    label = get_primary_label(node)
    name = get_node_name(node)
    return f'{label}「{name}」'


def format_edge(edge: Dict[str, Any]) -> str:
    return edge.get("type", "UNKNOWN_EDGE")


def build_path_text(
    path: Dict[str, Any],
    node_by_id: Dict[str, Dict[str, Any]],
    edge_by_id: Dict[str, Dict[str, Any]],
) -> str:
    node_ids = path.get("node_ids", [])
    edge_ids = path.get("edge_ids", [])

    parts: List[str] = []

    for i, node_id in enumerate(node_ids):
        node = node_by_id.get(node_id)
        if node is None:
            continue

        if i == 0:
            parts.append(format_node(node))
        else:
            edge_id = edge_ids[i - 1] if i - 1 < len(edge_ids) else None
            edge = edge_by_id.get(edge_id) if edge_id else None

            if edge:
                parts.append(f" --{format_edge(edge)}--> {format_node(node)}")
            else:
                parts.append(f" --> {format_node(node)}")

    return "".join(parts)


def build_practice_context(data: Dict[str, Any]) -> str:
    retrieved_graph = data["retrieved_graph"]

    nodes = retrieved_graph["nodes"]
    edges = retrieved_graph["edges"]
    paths = retrieved_graph["paths"]

    node_by_id = {node["id"]: node for node in nodes}
    edge_by_id = {edge["id"]: edge for edge in edges}

    practices: Dict[str, Dict[str, Any]] = {}

    for path in paths:
        path_nodes = [
            node_by_id[node_id]
            for node_id in path.get("node_ids", [])
            if node_id in node_by_id
        ]

        practice_node = next(
            (node for node in path_nodes if has_label(node, "Practice")),
            None,
        )

        if practice_node is None:
            continue

        practice_id = practice_node["properties"].get("practice_id")

        if practice_id not in practices:
            practices[practice_id] = {
                "practice": practice_node,
                "paper": None,
                "grades": [],
                "fields": [],
                "units": [],
                "hardware": [],
                "software": [],
                "artifacts": [],
                "functions": [],
                "opportunities": [],
                "effects": [],
                "matched_conditions": set(),
                "relation_paths": [],
            }

        item = practices[practice_id]

        for condition in path.get("matched_conditions", []):
            item["matched_conditions"].add(condition)

        relation_path_text = build_path_text(
            path=path,
            node_by_id=node_by_id,
            edge_by_id=edge_by_id,
        )
        add_unique(item["relation_paths"], relation_path_text)

        for node in path_nodes:
            name = get_node_name(node)

            if has_label(node, "Paper"):
                item["paper"] = node
            elif has_label(node, "Grade"):
                add_unique(item["grades"], name)
            elif has_label(node, "Field"):
                add_unique(item["fields"], name)
            elif has_label(node, "Unit"):
                add_unique(item["units"], name)
            elif has_label(node, "ICT_Hardware"):
                add_unique(item["hardware"], name)
            elif has_label(node, "ICT_Software"):
                add_unique(item["software"], name)
            elif has_label(node, "ICT_Artifact"):
                add_unique(item["artifacts"], name)
            elif has_label(node, "ICT_Function"):
                add_unique(item["functions"], name)
            elif has_label(node, "Educational_Opportunity"):
                add_unique(item["opportunities"], name)
            elif has_label(node, "Educational_Effect"):
                add_unique(item["effects"], name)

    lines: List[str] = []

    lines.append("【検索条件】")
    for label, values in data.get("grounded_conditions", {}).items():
        lines.append(f"- {label}: {', '.join(values)}")

    coverage = retrieved_graph.get("coverage", {})
    lines.append("")
    lines.append("【検索条件の回収状況】")
    lines.append(f"- 要求条件: {', '.join(coverage.get('requested_conditions', []))}")
    lines.append(f"- 回収条件: {', '.join(coverage.get('covered_conditions', []))}")
    lines.append(f"- 未回収条件: {', '.join(coverage.get('uncovered_conditions', []))}")

    for practice_id, item in practices.items():
        practice = item["practice"]
        paper = item["paper"]

        practice_props = practice.get("properties", {})
        paper_props = paper.get("properties", {}) if paper else {}

        lines.append("")
        lines.append("=" * 60)
        lines.append(f"【授業実践 {practice_id}】")

        if paper:
            lines.append(f"論文: {paper_props.get('title', '')}")
            lines.append(f"著者: {paper_props.get('author', '')}")
            lines.append(f"年: {paper_props.get('year', '')}")
            lines.append(f"論文ID: {paper_props.get('paper_id', '')}")

        lines.append(f"学年: {practice_props.get('grade', '')}")
        lines.append(f"領域: {practice_props.get('field', '')}")
        lines.append(f"単元: {practice_props.get('unit', '')}")

        lines.append("")
        lines.append("一致した検索条件:")
        for condition in sorted(item["matched_conditions"]):
            lines.append(f"- {condition}")

        lines.append("")
        lines.append("ノード概要:")

        lines.append("ICTハードウェア:")
        for value in item["hardware"]:
            lines.append(f"- {value}")

        lines.append("ICTソフトウェア:")
        for value in item["software"]:
            lines.append(f"- {value}")

        if item["artifacts"]:
            lines.append("ICT成果物:")
            for value in item["artifacts"]:
                lines.append(f"- {value}")

        lines.append("ICT機能:")
        for value in item["functions"]:
            lines.append(f"- {value}")

        lines.append("教育機会:")
        for value in item["opportunities"]:
            lines.append(f"- {value}")

        lines.append("教育効果:")
        for value in item["effects"]:
            lines.append(f"- {value}")

        lines.append("")
        lines.append("関係パス:")
        for i, relation_path in enumerate(item["relation_paths"], start=1):
            lines.append(f"{i}. {relation_path}")

    return "\n".join(lines)


def main():
    data = load_json(INPUT_PATH)
    context_text = build_practice_context(data)
    save_text(context_text, OUTPUT_PATH)

    print("=== Graph Context Build Completed ===")
    print(f"入力: {INPUT_PATH}")
    print(f"出力: {OUTPUT_PATH}")
    print("")
    print(context_text[:1500])


if __name__ == "__main__":
    main()