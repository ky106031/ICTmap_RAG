from typing import Any, Dict, List


def build_document_context(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return "関連する本文チャンクは見つかりませんでした。"

    lines: List[str] = []

    lines.append("【Document RAG検索結果】")
    lines.append("以下は、対象論文本文から検索された関連チャンクです。")
    lines.append("回答では、この本文情報だけを根拠として使用してください。")

    for i, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata", {})
        paper_id = metadata.get("paper_id", "")
        source_file = metadata.get("source_file", "")
        chunk_index = metadata.get("chunk_index", "")
        distance = chunk.get("distance", "")

        lines.append("")
        lines.append("=" * 60)
        lines.append(f"【チャンク {i}】")
        lines.append(f"paper_id: {paper_id}")
        lines.append(f"source_file: {source_file}")
        lines.append(f"chunk_index: {chunk_index}")
        lines.append(f"distance: {distance}")
        lines.append("")
        lines.append("本文:")
        lines.append(chunk.get("text", ""))

    return "\n".join(lines)


def main():
    from document_retriever import retrieve_document_chunks

    query = "この実践では、生徒は具体的にどのような活動をしましたか？"
    paper_ids = ["P_0001"]

    chunks = retrieve_document_chunks(
        query=query,
        paper_ids=paper_ids,
        top_k=5,
    )

    context = build_document_context(chunks)

    print("=== Document Context ===")
    print(context[:2000])


if __name__ == "__main__":
    main()