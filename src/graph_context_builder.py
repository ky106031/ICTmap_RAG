import json
from pathlib import Path
from typing import Any, Dict, List


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_PATH = BASE_DIR / "data" / "retrieved_graph.json"
OUTPUT_PATH = BASE_DIR / "data" / "graph_context.txt"


# ============================================================
# ファイル操作
# ============================================================

def load_json(path: Path) -> Dict[str, Any]:
    """
    JSONファイルを読み込む。
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_text(text: str, path: Path) -> None:
    """
    テキストをファイルへ保存する。
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ============================================================
# ノード・エッジ操作
# ============================================================

def has_label(
    node: Dict[str, Any],
    label: str,
) -> bool:
    """
    ノードが指定ラベルを持つか確認する。
    """
    return label in node.get("labels", [])


def get_primary_label(
    node: Dict[str, Any],
) -> str:
    """
    ノードの代表ラベルを取得する。
    """
    labels = node.get("labels", [])

    return labels[0] if labels else "Unknown"


def get_node_name(
    node: Dict[str, Any],
) -> str:
    """
    ノードの表示名を取得する。
    """
    props = node.get("properties", {})

    return str(
        props.get("title")
        or props.get("name")
        or props.get("practice_id")
        or props.get("paper_id")
        or ""
    )


def add_unique(
    target: List[str],
    value: str,
) -> None:
    """
    値が未登録の場合だけリストへ追加する。
    """
    if value and value not in target:
        target.append(value)


def format_node(
    node: Dict[str, Any],
) -> str:
    """
    ノードを関係パス表示用の文字列へ変換する。
    """
    label = get_primary_label(node)
    name = get_node_name(node)

    return f'{label}「{name}」'


def format_edge(
    edge: Dict[str, Any],
) -> str:
    """
    エッジの種類を取得する。
    """
    return str(
        edge.get("type", "UNKNOWN_EDGE")
    )


def build_path_text(
    path: Dict[str, Any],
    node_by_id: Dict[str, Dict[str, Any]],
    edge_by_id: Dict[str, Dict[str, Any]],
) -> str:
    """
    GraphRAGのパスを、人間が読める文字列へ変換する。
    """
    node_ids = path.get("node_ids", [])
    edge_ids = path.get("edge_ids", [])

    parts: List[str] = []

    for index, node_id in enumerate(node_ids):
        node = node_by_id.get(node_id)

        if node is None:
            continue

        if index == 0:
            parts.append(
                format_node(node)
            )
            continue

        edge_id = (
            edge_ids[index - 1]
            if index - 1 < len(edge_ids)
            else None
        )

        edge = (
            edge_by_id.get(edge_id)
            if edge_id
            else None
        )

        if edge:
            parts.append(
                f" --{format_edge(edge)}--> "
                f"{format_node(node)}"
            )
        else:
            parts.append(
                f" --> {format_node(node)}"
            )

    return "".join(parts)


# ============================================================
# 実践情報の集約
# ============================================================

def collect_practices(
    data: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    """
    GraphRAGの検索結果を授業実践単位に集約する。

    Returns:
        practice_idをキーとした実践情報
    """
    retrieved_graph = data["retrieved_graph"]

    nodes = retrieved_graph.get("nodes", [])
    edges = retrieved_graph.get("edges", [])
    paths = retrieved_graph.get("paths", [])

    node_by_id = {
        node["id"]: node
        for node in nodes
        if "id" in node
    }

    edge_by_id = {
        edge["id"]: edge
        for edge in edges
        if "id" in edge
    }

    practices: Dict[str, Dict[str, Any]] = {}

    for path in paths:
        path_nodes = [
            node_by_id[node_id]
            for node_id in path.get("node_ids", [])
            if node_id in node_by_id
        ]

        practice_node = next(
            (
                node
                for node in path_nodes
                if has_label(node, "Practice")
            ),
            None,
        )

        if practice_node is None:
            continue

        practice_props = practice_node.get(
            "properties",
            {},
        )

        practice_id = str(
            practice_props.get("practice_id", "")
        ).strip()

        if not practice_id:
            continue

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

        for condition in path.get(
            "matched_conditions",
            [],
        ):
            if condition:
                item["matched_conditions"].add(
                    str(condition)
                )

        relation_path_text = build_path_text(
            path=path,
            node_by_id=node_by_id,
            edge_by_id=edge_by_id,
        )

        add_unique(
            item["relation_paths"],
            relation_path_text,
        )

        for node in path_nodes:
            name = get_node_name(node)

            if has_label(node, "Paper"):
                item["paper"] = node

            elif has_label(node, "Grade"):
                add_unique(
                    item["grades"],
                    name,
                )

            elif has_label(node, "Field"):
                add_unique(
                    item["fields"],
                    name,
                )

            elif has_label(node, "Unit"):
                add_unique(
                    item["units"],
                    name,
                )

            elif has_label(node, "ICT_Hardware"):
                add_unique(
                    item["hardware"],
                    name,
                )

            elif has_label(node, "ICT_Software"):
                add_unique(
                    item["software"],
                    name,
                )

            elif has_label(node, "ICT_Artifact"):
                add_unique(
                    item["artifacts"],
                    name,
                )

            elif has_label(node, "ICT_Function"):
                add_unique(
                    item["functions"],
                    name,
                )

            elif has_label(
                node,
                "Educational_Opportunity",
            ):
                add_unique(
                    item["opportunities"],
                    name,
                )

            elif has_label(
                node,
                "Educational_Effect",
            ):
                add_unique(
                    item["effects"],
                    name,
                )

    return practices


# ============================================================
# 会話管理用の実践候補
# ============================================================

def build_practice_candidates(
    data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    GraphRAGの検索結果から、会話管理用の実践候補を作る。

    各候補にはDocument RAGへ接続するための
    paper_idを含める。
    """
    practices = collect_practices(data)

    candidates: List[Dict[str, Any]] = []

    for index, (
        practice_id,
        item,
    ) in enumerate(
        practices.items(),
        start=1,
    ):
        practice = item["practice"]
        paper = item["paper"]

        practice_props = practice.get(
            "properties",
            {},
        )

        paper_props = (
            paper.get("properties", {})
            if paper
            else {}
        )

        candidate = {
            "index": index,
            "label": f"実践{index}",
            "practice_id": practice_id,
            "paper_id": str(
                paper_props.get("paper_id", "")
            ).strip(),
            "title": str(
                paper_props.get("title", "")
            ).strip(),
            "author": str(
                paper_props.get("author", "")
            ).strip(),
            "year": str(
                paper_props.get("year", "")
            ).strip(),
            "grade": str(
                practice_props.get("grade", "")
            ).strip(),
            "field": str(
                practice_props.get("field", "")
            ).strip(),
            "unit": str(
                practice_props.get("unit", "")
            ).strip(),
            "matched_conditions": sorted(
                item["matched_conditions"]
            ),
            "hardware": list(
                item["hardware"]
            ),
            "software": list(
                item["software"]
            ),
            "effects": list(
                item["effects"]
            ),
        }

        candidates.append(candidate)

    return candidates


# ============================================================
# Graph Context
# ============================================================

def build_practice_context(
    data: Dict[str, Any],
) -> str:
    """
    GraphRAGの検索結果から、
    回答生成用のコンテキストを作成する。
    """
    retrieved_graph = data["retrieved_graph"]

    practices = collect_practices(data)

    lines: List[str] = []

    lines.append("【検索条件】")

    for label, values in data.get(
        "grounded_conditions",
        {},
    ).items():
        display_values = [
            str(value)
            for value in values
        ]

        lines.append(
            f"- {label}: "
            f"{', '.join(display_values)}"
        )

    coverage = retrieved_graph.get(
        "coverage",
        {},
    )

    lines.append("")
    lines.append("【検索条件の回収状況】")

    lines.append(
        "- 要求条件: "
        + ", ".join(
            coverage.get(
                "requested_conditions",
                [],
            )
        )
    )

    lines.append(
        "- 回収条件: "
        + ", ".join(
            coverage.get(
                "covered_conditions",
                [],
            )
        )
    )

    lines.append(
        "- 未回収条件: "
        + ", ".join(
            coverage.get(
                "uncovered_conditions",
                [],
            )
        )
    )

    for index, (
        practice_id,
        item,
    ) in enumerate(
        practices.items(),
        start=1,
    ):
        practice = item["practice"]
        paper = item["paper"]

        practice_props = practice.get(
            "properties",
            {},
        )

        paper_props = (
            paper.get("properties", {})
            if paper
            else {}
        )

        lines.append("")
        lines.append("=" * 60)

        # 回答文と会話管理側の順番を一致させる
        lines.append(
            f"【実践{index}】"
        )

        lines.append(
            f"実践ID: {practice_id}"
        )

        if paper:
            lines.append(
                f"論文: "
                f"{paper_props.get('title', '')}"
            )

            lines.append(
                f"著者: "
                f"{paper_props.get('author', '')}"
            )

            lines.append(
                f"年: "
                f"{paper_props.get('year', '')}"
            )

            lines.append(
                f"論文ID: "
                f"{paper_props.get('paper_id', '')}"
            )

        lines.append(
            f"学年: "
            f"{practice_props.get('grade', '')}"
        )

        lines.append(
            f"領域: "
            f"{practice_props.get('field', '')}"
        )

        lines.append(
            f"単元: "
            f"{practice_props.get('unit', '')}"
        )

        lines.append("")
        lines.append("一致した検索条件:")

        for condition in sorted(
            item["matched_conditions"]
        ):
            lines.append(
                f"- {condition}"
            )

        lines.append("")
        lines.append("ノード概要:")

        lines.append("ICTハードウェア:")

        for value in item["hardware"]:
            lines.append(
                f"- {value}"
            )

        lines.append("ICTソフトウェア:")

        for value in item["software"]:
            lines.append(
                f"- {value}"
            )

        if item["artifacts"]:
            lines.append("ICT成果物:")

            for value in item["artifacts"]:
                lines.append(
                    f"- {value}"
                )

        lines.append("ICT機能:")

        for value in item["functions"]:
            lines.append(
                f"- {value}"
            )

        lines.append("教育機会:")

        for value in item["opportunities"]:
            lines.append(
                f"- {value}"
            )

        lines.append("教育効果:")

        for value in item["effects"]:
            lines.append(
                f"- {value}"
            )

        lines.append("")
        lines.append("関係パス:")

        for path_index, relation_path in enumerate(
            item["relation_paths"],
            start=1,
        ):
            lines.append(
                f"{path_index}. {relation_path}"
            )

    return "\n".join(lines)


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    graph_context_builder.py単体の動作確認。
    """
    data = load_json(INPUT_PATH)

    context_text = build_practice_context(
        data
    )

    practice_candidates = (
        build_practice_candidates(data)
    )

    save_text(
        context_text,
        OUTPUT_PATH,
    )

    print(
        "=== Graph Context Build Completed ==="
    )
    print(f"入力: {INPUT_PATH}")
    print(f"出力: {OUTPUT_PATH}")

    print()
    print("=== Practice Candidates ===")

    for candidate in practice_candidates:
        print(candidate)

    print()
    print("=== Graph Context Preview ===")
    print(context_text[:1500])


if __name__ == "__main__":
    main()