import json
from pathlib import Path
from typing import Any, Dict, List

from rag_pipeline import run_pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "data" / "evaluation_results.json"


TEST_QUERIES = [
    "高校3年生でInstagramを活用し、観察への意欲を高めたいです。どのような授業実践が参考になりますか？",
    "中学3年生でFaceTimeを使った理科の授業実践を知りたいです。",
    "観察結果を共有する活動を取り入れたいです。参考になるICT活用事例はありますか？",
    "小学校5年生でタブレットを使い、観察への意欲を高めたいです。",
    "Excelを使って実験データを整理する授業実践を教えてください。",
]


def save_json(data: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def summarize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    graph = result["retrieved_graph"]

    return {
        "user_query": result["user_query"],
        "raw_conditions": result["raw_conditions"],
        "grounded_conditions": result["grounded_conditions"],
        "retrieval_summary": {
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "paths": len(graph["paths"]),
            "coverage": graph["coverage"],
            "retrieval_groups": graph["retrieval_groups"],
        },
        "generated_answer": result["generated_answer"],
    }


def main():
    evaluation_results = []

    for i, query in enumerate(TEST_QUERIES, start=1):
        print("\n" + "=" * 70)
        print(f"Test Query {i}")
        print(query)

        try:
            result = run_pipeline(user_query=query)
            summary = summarize_result(result)
            summary["status"] = "success"
            evaluation_results.append(summary)

            print("status: success")
            print("raw_conditions:", summary["raw_conditions"])
            print("grounded_conditions:", summary["grounded_conditions"])
            print("coverage:", summary["retrieval_summary"]["coverage"])
            print("nodes:", summary["retrieval_summary"]["nodes"])
            print("edges:", summary["retrieval_summary"]["edges"])
            print("paths:", summary["retrieval_summary"]["paths"])

        except Exception as e:
            evaluation_results.append({
                "user_query": query,
                "status": "error",
                "error": str(e),
            })

            print("status: error")
            print(e)

    save_json(evaluation_results, OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("=== Evaluation Completed ===")
    print(f"保存先: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()