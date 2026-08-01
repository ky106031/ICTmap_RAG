import json
from pathlib import Path
from typing import Any, Dict

from query_parser import parse_query
from node_grounding import ground_conditions
from graph_retriever import retrieve_graph
from graph_context_builder import (
    build_practice_candidates,
    build_practice_context,
    save_text,
)
from generate_answer import (
    build_prompt,
    get_gemini_client,
    GENERATE_MODEL,
)


BASE_DIR = Path(__file__).resolve().parents[1]

RETRIEVED_GRAPH_PATH = (
    BASE_DIR
    / "data"
    / "retrieved_graph.json"
)

GRAPH_CONTEXT_PATH = (
    BASE_DIR
    / "data"
    / "graph_context.txt"
)

GENERATED_ANSWER_PATH = (
    BASE_DIR
    / "data"
    / "generated_answer.txt"
)


# ============================================================
# ファイル保存
# ============================================================

def save_json(
    data: Dict[str, Any],
    path: Path,
) -> None:
    """
    辞書をJSONファイルへ保存する。
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# 回答生成
# ============================================================

def generate_answer_from_context(
    user_query: str,
    graph_context: str,
) -> str:
    """
    Graph Contextをもとに回答を生成する。
    """
    prompt = build_prompt(
        user_query=user_query,
        graph_context=graph_context,
    )

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GENERATE_MODEL,
        contents=prompt,
    )

    answer = response.text

    if not answer:
        raise RuntimeError(
            "Gemini APIから回答が返されませんでした。"
        )

    return answer.strip()


# ============================================================
# GraphRAG Pipeline
# ============================================================

def run_pipeline(
    user_query: str,
) -> Dict[str, Any]:
    """
    GraphRAGの一連の処理を実行する。

    Returns:
        回答に加え、会話管理用の
        practice_candidatesも返す。
    """
    normalized_query = user_query.strip()

    if not normalized_query:
        raise ValueError(
            "ユーザーの質問が空です。"
        )

    # 1. 質問から検索条件を抽出
    raw_conditions = parse_query(
        normalized_query
    )

    # 2. 検索条件をグラフ上の値へ接地
    grounded_conditions = ground_conditions(
        raw_conditions
    )

    # 3. Knowledge Graphを検索
    retrieved_graph = retrieve_graph(
        grounded_conditions=grounded_conditions,
        row_limit=300,
    )

    retrieved_graph_output = {
        "user_query": normalized_query,
        "raw_conditions": raw_conditions,
        "grounded_conditions": (
            grounded_conditions
        ),
        "retrieved_graph": retrieved_graph,
    }

    # デバッグ用に検索結果を保存
    save_json(
        retrieved_graph_output,
        RETRIEVED_GRAPH_PATH,
    )

    # 4. LLM回答用のGraph Contextを生成
    graph_context = build_practice_context(
        retrieved_graph_output
    )

    save_text(
        graph_context,
        GRAPH_CONTEXT_PATH,
    )

    # 5. 会話管理用の実践候補を生成
    practice_candidates = (
        build_practice_candidates(
            retrieved_graph_output
        )
    )

    # 6. 回答を生成
    generated_answer = (
        generate_answer_from_context(
            user_query=normalized_query,
            graph_context=graph_context,
        )
    )

    save_text(
        generated_answer,
        GENERATED_ANSWER_PATH,
    )

    return {
        "user_query": normalized_query,
        "raw_conditions": raw_conditions,
        "grounded_conditions": (
            grounded_conditions
        ),
        "retrieved_graph": retrieved_graph,
        "graph_context": graph_context,
        "practice_candidates": (
            practice_candidates
        ),
        "generated_answer": generated_answer,
    }


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    GraphRAG Pipelineの動作確認。
    """
    user_query = (
        "高校3年生でInstagramを活用し、"
        "観察への意欲を高めたいです。"
        "どのような授業実践が参考になりますか？"
    )

    result = run_pipeline(
        user_query=user_query
    )

    print(
        "=== GraphRAG Pipeline Completed ==="
    )

    print(
        f"retrieved_graph: "
        f"{RETRIEVED_GRAPH_PATH}"
    )

    print(
        f"graph_context: "
        f"{GRAPH_CONTEXT_PATH}"
    )

    print(
        f"generated_answer: "
        f"{GENERATED_ANSWER_PATH}"
    )

    print()
    print("=== User Query ===")
    print(result["user_query"])

    print()
    print("=== Parsed Raw Conditions ===")
    print(result["raw_conditions"])

    print()
    print("=== Grounded Conditions ===")
    print(result["grounded_conditions"])

    print()
    print("=== Retrieval Summary ===")

    graph = result["retrieved_graph"]

    print(
        f"nodes: "
        f"{len(graph.get('nodes', []))}"
    )

    print(
        f"edges: "
        f"{len(graph.get('edges', []))}"
    )

    print(
        f"paths: "
        f"{len(graph.get('paths', []))}"
    )

    print(
        f"coverage: "
        f"{graph.get('coverage', {})}"
    )

    print()
    print("=== Practice Candidates ===")

    for candidate in result[
        "practice_candidates"
    ]:
        print(candidate)

    print()
    print("=== Generated Answer ===")
    print(result["generated_answer"])


if __name__ == "__main__":
    main()