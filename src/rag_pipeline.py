import json
from pathlib import Path
from typing import Any, Dict

from query_parser import parse_query
from node_grounding import ground_conditions
from graph_retriever import retrieve_graph
from graph_context_builder import build_practice_context, save_text
from generate_answer import build_prompt, get_gemini_client, GENERATE_MODEL


BASE_DIR = Path(__file__).resolve().parents[1]

RETRIEVED_GRAPH_PATH = BASE_DIR / "data" / "retrieved_graph.json"
GRAPH_CONTEXT_PATH = BASE_DIR / "data" / "graph_context.txt"
GENERATED_ANSWER_PATH = BASE_DIR / "data" / "generated_answer.txt"


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_answer_from_context(user_query: str, graph_context: str) -> str:
    prompt = build_prompt(
        user_query=user_query,
        graph_context=graph_context,
    )

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GENERATE_MODEL,
        contents=prompt,
    )

    return response.text


def run_pipeline(user_query: str) -> Dict[str, Any]:
    raw_conditions = parse_query(user_query)

    grounded_conditions = ground_conditions(raw_conditions)

    retrieved_graph = retrieve_graph(
        grounded_conditions=grounded_conditions,
        row_limit=300,
    )

    retrieved_graph_output = {
        "user_query": user_query,
        "raw_conditions": raw_conditions,
        "grounded_conditions": grounded_conditions,
        "retrieved_graph": retrieved_graph,
    }

    save_json(retrieved_graph_output, RETRIEVED_GRAPH_PATH)

    graph_context = build_practice_context(retrieved_graph_output)
    save_text(graph_context, GRAPH_CONTEXT_PATH)

    generated_answer = generate_answer_from_context(
        user_query=user_query,
        graph_context=graph_context,
    )

    save_text(generated_answer, GENERATED_ANSWER_PATH)

    return {
        "user_query": user_query,
        "raw_conditions": raw_conditions,
        "grounded_conditions": grounded_conditions,
        "retrieved_graph": retrieved_graph,
        "graph_context": graph_context,
        "generated_answer": generated_answer,
    }


def main():
    user_query = (
        "高校3年生でInstagramを活用し、観察への意欲を高めたいです。"
        "どのような授業実践が参考になりますか？"
    )

    result = run_pipeline(user_query=user_query)

    print("=== GraphRAG Pipeline Completed ===")
    print(f"retrieved_graph: {RETRIEVED_GRAPH_PATH}")
    print(f"graph_context: {GRAPH_CONTEXT_PATH}")
    print(f"generated_answer: {GENERATED_ANSWER_PATH}")

    print("\n=== User Query ===")
    print(result["user_query"])

    print("\n=== Parsed Raw Conditions ===")
    print(result["raw_conditions"])

    print("\n=== Grounded Conditions ===")
    print(result["grounded_conditions"])

    print("\n=== Retrieval Summary ===")
    graph = result["retrieved_graph"]
    print(f"nodes: {len(graph['nodes'])}")
    print(f"edges: {len(graph['edges'])}")
    print(f"paths: {len(graph['paths'])}")
    print(f"coverage: {graph['coverage']}")

    print("\n=== Generated Answer ===")
    print(result["generated_answer"])


if __name__ == "__main__":
    main()