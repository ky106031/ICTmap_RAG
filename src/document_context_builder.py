from typing import Iterable

from document_retriever import RetrievedChunk


# ============================================================
# 基本設定
# ============================================================

DEFAULT_MAX_CONTEXT_CHARS = 12000


# ============================================================
# チャンクの検証
# ============================================================

def validate_retrieved_chunks(
    retrieved_chunks: list[RetrievedChunk],
) -> None:
    """
    Retrieverから受け取った検索結果を検証する。

    Args:
        retrieved_chunks:
            document_retriever.pyが返した関連チャンク

    Raises:
        ValueError:
            検索結果が空の場合
    """
    if not retrieved_chunks:
        raise ValueError(
            "検索されたチャンクがありません。"
        )


# ============================================================
# チャンク情報の取得
# ============================================================

def get_chunk_paper_id(
    chunk: RetrievedChunk,
) -> str:
    """
    検索チャンクのmetadataからpaper_idを取得する。
    """
    metadata = chunk.get("metadata", {})

    paper_id = str(
        metadata.get("paper_id", "")
    ).strip()

    return paper_id or "不明"


def get_chunk_index(
    chunk: RetrievedChunk,
) -> str:
    """
    検索チャンクのmetadataからchunk_indexを取得する。
    """
    metadata = chunk.get("metadata", {})

    chunk_index = metadata.get(
        "chunk_index",
        "不明",
    )

    return str(chunk_index)


def get_source_file(
    chunk: RetrievedChunk,
) -> str:
    """
    検索チャンクのmetadataからsource_fileを取得する。
    """
    metadata = chunk.get("metadata", {})

    source_file = str(
        metadata.get("source_file", "")
    ).strip()

    return source_file or "不明"


# ============================================================
# 単一チャンクの整形
# ============================================================

def format_document_chunk(
    chunk: RetrievedChunk,
    rank: int,
) -> str:
    """
    1件の検索チャンクをLLMへ渡す形式に整形する。

    Args:
        chunk:
            検索されたチャンク
        rank:
            検索順位

    Returns:
        整形済みテキスト
    """
    chunk_id = chunk.get(
        "chunk_id",
        "不明",
    )

    distance = chunk.get(
        "distance",
        0.0,
    )

    text = str(
        chunk.get("text", "")
    ).strip()

    paper_id = get_chunk_paper_id(
        chunk=chunk
    )

    chunk_index = get_chunk_index(
        chunk=chunk
    )

    source_file = get_source_file(
        chunk=chunk
    )

    return (
        f"【検索結果 {rank}】\n"
        f"論文ID: {paper_id}\n"
        f"出典ファイル: {source_file}\n"
        f"チャンクID: {chunk_id}\n"
        f"チャンク番号: {chunk_index}\n"
        f"検索距離: {distance:.6f}\n"
        f"\n"
        f"本文:\n"
        f"{text}"
    )


# ============================================================
# 重複除去
# ============================================================

def remove_duplicate_chunks(
    retrieved_chunks: Iterable[RetrievedChunk],
) -> list[RetrievedChunk]:
    """
    chunk_idが重複している検索結果を除去する。

    Args:
        retrieved_chunks:
            検索チャンク

    Returns:
        重複を除去したチャンク
    """
    unique_chunks: list[RetrievedChunk] = []
    seen_chunk_ids: set[str] = set()

    for chunk in retrieved_chunks:
        chunk_id = str(
            chunk.get("chunk_id", "")
        ).strip()

        if not chunk_id:
            continue

        if chunk_id in seen_chunk_ids:
            continue

        seen_chunk_ids.add(chunk_id)
        unique_chunks.append(chunk)

    return unique_chunks


# ============================================================
# Document Context Builder
# ============================================================

def build_document_context(
    retrieved_chunks: list[RetrievedChunk],
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> str:
    """
    検索チャンクをDocument RAG回答生成用の
    コンテキストへ変換する。

    Args:
        retrieved_chunks:
            document_retriever.pyが返した検索結果
        max_context_chars:
            コンテキスト全体の最大文字数

    Returns:
        LLMへ渡すDocument RAG用コンテキスト
    """
    validate_retrieved_chunks(
        retrieved_chunks=retrieved_chunks
    )

    if max_context_chars <= 0:
        raise ValueError(
            "max_context_charsは1以上を指定してください。"
        )

    unique_chunks = remove_duplicate_chunks(
        retrieved_chunks=retrieved_chunks
    )

    if not unique_chunks:
        raise ValueError(
            "有効な検索チャンクがありません。"
        )

    context_parts: list[str] = []

    current_length = 0

    for rank, chunk in enumerate(
        unique_chunks,
        start=1,
    ):
        formatted_chunk = format_document_chunk(
            chunk=chunk,
            rank=rank,
        )

        separator = "\n\n" + "=" * 70 + "\n\n"

        additional_length = len(
            formatted_chunk
        )

        if context_parts:
            additional_length += len(separator)

        if (
            current_length + additional_length
            > max_context_chars
        ):
            break

        if context_parts:
            context_parts.append(separator)

        context_parts.append(formatted_chunk)

        current_length += additional_length

    if not context_parts:
        raise ValueError(
            "コンテキストの最大文字数が小さすぎるため、"
            "チャンクを追加できませんでした。"
        )

    header = (
        "以下は、指定された教育実践に関する"
        "論文本文から検索された情報です。\n"
        "回答は、原則として以下の情報に基づいて"
        "作成してください。\n\n"
    )

    return header + "".join(context_parts)


# ============================================================
# 参照情報の作成
# ============================================================

def build_document_sources(
    retrieved_chunks: list[RetrievedChunk],
) -> list[dict[str, object]]:
    """
    UIや回答末尾に表示するための参照情報を作成する。

    Args:
        retrieved_chunks:
            Retrieverの検索結果

    Returns:
        参照チャンク情報
    """
    unique_chunks = remove_duplicate_chunks(
        retrieved_chunks=retrieved_chunks
    )

    sources: list[dict[str, object]] = []

    for rank, chunk in enumerate(
        unique_chunks,
        start=1,
    ):
        sources.append(
            {
                "rank": rank,
                "paper_id": get_chunk_paper_id(
                    chunk=chunk
                ),
                "source_file": get_source_file(
                    chunk=chunk
                ),
                "chunk_id": chunk.get(
                    "chunk_id",
                    "",
                ),
                "chunk_index": get_chunk_index(
                    chunk=chunk
                ),
                "distance": chunk.get(
                    "distance",
                    0.0,
                ),
            }
        )

    return sources


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    document_retriever.pyと接続した動作確認。
    """
    from document_retriever import (
        retrieve_document_chunks,
    )

    query = (
        "この実践では、生徒は具体的に"
        "どのような活動をしましたか？"
    )

    paper_ids = ["P_0001"]

    retrieved_chunks = retrieve_document_chunks(
        query=query,
        paper_ids=paper_ids,
        top_k=5,
    )

    context = build_document_context(
        retrieved_chunks=retrieved_chunks
    )

    sources = build_document_sources(
        retrieved_chunks=retrieved_chunks
    )

    print("=== Document Context ===")
    print()
    print(context)

    print()
    print("=" * 70)
    print("=== Document Sources ===")

    for source in sources:
        print(source)


if __name__ == "__main__":
    main()