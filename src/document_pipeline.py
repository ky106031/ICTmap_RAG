from typing import TypedDict

from document_answer import (
    generate_document_answer,
)
from document_context_builder import (
    build_document_context,
    build_document_sources,
)
from document_retriever import (
    RetrievedChunk,
    retrieve_document_chunks,
)


# ============================================================
# 基本設定
# ============================================================

DEFAULT_TOP_K = 3
DEFAULT_MAX_CONTEXT_CHARS = 16000


# ============================================================
# 戻り値
# ============================================================

class DocumentRAGResult(TypedDict):
    query: str
    paper_ids: list[str]
    answer: str
    context: str
    retrieved_chunks: list[RetrievedChunk]
    sources: list[dict[str, object]]


# ============================================================
# Validation
# ============================================================

def normalize_query(
    query: str,
) -> str:

    query = query.strip()

    if not query:
        raise ValueError(
            "ユーザーの質問が空です。"
        )

    return query


def normalize_paper_ids(
    paper_ids: list[str],
) -> list[str]:

    result: list[str] = []

    for paper_id in paper_ids:

        value = paper_id.strip()

        if (
            value
            and value not in result
        ):
            result.append(
                value
            )

    if not result:
        raise ValueError(
            "検索対象のpaper_idsが"
            "指定されていません。"
        )

    return result


# ============================================================
# Pipeline
# ============================================================

def run_document_rag(
    query: str,
    paper_ids: list[str],
    top_k: int = DEFAULT_TOP_K,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    paper_labels: dict[str, str] | None = None,
) -> DocumentRAGResult:

    normalized_query = normalize_query(
        query
    )

    normalized_ids = normalize_paper_ids(
        paper_ids
    )

    if top_k <= 0:
        raise ValueError(
            "top_kは1以上を指定してください。"
        )

    if max_context_chars <= 0:
        raise ValueError(
            "max_context_charsは1以上を指定してください。"
        )

    retrieved_chunks = retrieve_document_chunks(
        query=normalized_query,
        paper_ids=normalized_ids,
        top_k=top_k,
    )

    context = build_document_context(
        retrieved_chunks=retrieved_chunks,
        max_context_chars=max_context_chars,
        paper_labels=paper_labels,
    )

    answer = generate_document_answer(
        query=normalized_query,
        context=context,
    )

    sources = build_document_sources(
        retrieved_chunks=retrieved_chunks,
        paper_labels=paper_labels,
    )

    return {
        "query": normalized_query,
        "paper_ids": normalized_ids,
        "answer": answer,
        "context": context,
        "retrieved_chunks": retrieved_chunks,
        "sources": sources,
    }