from collections import defaultdict
from typing import Iterable

from document_retriever import RetrievedChunk


# ============================================================
# 基本設定
# ============================================================

DEFAULT_MAX_CONTEXT_CHARS = 16000


# ============================================================
# 検証
# ============================================================

def validate_retrieved_chunks(
    retrieved_chunks: list[RetrievedChunk],
) -> None:

    if not retrieved_chunks:

        raise ValueError(
            "検索されたチャンクがありません。"
        )


# ============================================================
# Metadata
# ============================================================

def get_chunk_paper_id(
    chunk: RetrievedChunk,
) -> str:

    metadata = chunk.get(
        "metadata",
        {},
    )

    value = str(
        metadata.get(
            "paper_id",
            "",
        )
    ).strip()

    return value or "不明"


def get_chunk_index(
    chunk: RetrievedChunk,
) -> str:

    metadata = chunk.get(
        "metadata",
        {},
    )

    return str(
        metadata.get(
            "chunk_index",
            "不明",
        )
    )


def get_source_file(
    chunk: RetrievedChunk,
) -> str:

    metadata = chunk.get(
        "metadata",
        {},
    )

    value = str(
        metadata.get(
            "source_file",
            "",
        )
    ).strip()

    return value or "不明"


# ============================================================
# 重複除去
# ============================================================

def remove_duplicate_chunks(
    retrieved_chunks: Iterable[RetrievedChunk],
) -> list[RetrievedChunk]:

    result: list[RetrievedChunk] = []

    seen: set[str] = set()

    for chunk in retrieved_chunks:

        chunk_id = str(
            chunk.get(
                "chunk_id",
                "",
            )
        ).strip()

        if not chunk_id:
            continue

        if chunk_id in seen:
            continue

        seen.add(
            chunk_id
        )

        result.append(
            chunk
        )

    return result


# ============================================================
# Context
# ============================================================

def build_document_context(
    retrieved_chunks: list[RetrievedChunk],
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    paper_labels: dict[str, str] | None = None,
) -> str:
    """
    複数論文の検索結果を論文ごとに分けて
    Geminiへ渡すContextを作成する。
    """

    validate_retrieved_chunks(
        retrieved_chunks
    )

    unique_chunks = remove_duplicate_chunks(
        retrieved_chunks
    )

    grouped: dict[
        str,
        list[RetrievedChunk],
    ] = defaultdict(list)

    for chunk in unique_chunks:

        paper_id = get_chunk_paper_id(
            chunk
        )

        grouped[
            paper_id
        ].append(
            chunk
        )

    context_parts: list[str] = []

    current_length = 0

    header = (
        "以下は、ユーザーが選択した複数の"
        "教育実践に対応する論文本文から"
        "検索された情報です。\n"
        "各実践の情報を区別しながら、必要に応じて"
        "比較・統合して回答してください。\n\n"
    )

    context_parts.append(
        header
    )

    current_length += len(
        header
    )

    for paper_id, chunks in grouped.items():

        display_name = (
            paper_labels.get(
                paper_id,
                paper_id,
            )
            if paper_labels
            else paper_id
        )

        section_header = (
            "\n"
            + "=" * 70
            + "\n"
            f"【{display_name}】\n"
            + "=" * 70
            + "\n"
        )

        if (
            current_length
            + len(section_header)
            > max_context_chars
        ):
            break

        context_parts.append(
            section_header
        )

        current_length += len(
            section_header
        )

        for rank, chunk in enumerate(
            chunks,
            start=1,
        ):

            text = str(
                chunk.get(
                    "text",
                    "",
                )
            ).strip()

            chunk_text = (
                f"\n【関連箇所 {rank}】\n"
                f"{text}\n"
            )

            if (
                current_length
                + len(chunk_text)
                > max_context_chars
            ):
                break

            context_parts.append(
                chunk_text
            )

            current_length += len(
                chunk_text
            )

    return "".join(
        context_parts
    )


# ============================================================
# Sources
# ============================================================

def build_document_sources(
    retrieved_chunks: list[RetrievedChunk],
    paper_labels: dict[str, str] | None = None,
) -> list[dict[str, object]]:

    unique_chunks = remove_duplicate_chunks(
        retrieved_chunks
    )

    sources: list[
        dict[str, object]
    ] = []

    for rank, chunk in enumerate(
        unique_chunks,
        start=1,
    ):

        paper_id = get_chunk_paper_id(
            chunk
        )

        display_name = (
            paper_labels.get(
                paper_id,
                paper_id,
            )
            if paper_labels
            else paper_id
        )

        sources.append(
            {
                "rank": rank,
                "paper_id": paper_id,
                "practice_label": display_name,
                "source_file": (
                    get_source_file(
                        chunk
                    )
                ),
                "chunk_id": chunk.get(
                    "chunk_id",
                    "",
                ),
                "chunk_index": (
                    get_chunk_index(
                        chunk
                    )
                ),
                "distance": chunk.get(
                    "distance",
                    0.0,
                ),
            }
        )

    return sources