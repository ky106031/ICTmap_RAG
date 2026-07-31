from typing import Any, TypedDict

from document_answer import generate_document_answer
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

DEFAULT_TOP_K = 5
DEFAULT_MAX_CONTEXT_CHARS = 12000


# ============================================================
# 戻り値の型定義
# ============================================================

class DocumentRAGResult(TypedDict):
    query: str
    paper_ids: list[str]
    answer: str
    context: str
    retrieved_chunks: list[RetrievedChunk]
    sources: list[dict[str, object]]


# ============================================================
# 入力検証
# ============================================================

def normalize_query(
    query: str,
) -> str:
    """
    質問文を検証し、前後の空白を除去する。
    """
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError(
            "ユーザーの質問が空です。"
        )

    return normalized_query


def normalize_paper_ids(
    paper_ids: list[str],
) -> list[str]:
    """
    論文IDの空文字と重複を除去する。
    """
    normalized_ids: list[str] = []

    for paper_id in paper_ids:
        normalized_id = paper_id.strip()

        if (
            normalized_id
            and normalized_id not in normalized_ids
        ):
            normalized_ids.append(normalized_id)

    if not normalized_ids:
        raise ValueError(
            "検索対象のpaper_idsが指定されていません。"
        )

    return normalized_ids


def validate_pipeline_parameters(
    top_k: int,
    max_context_chars: int,
) -> None:
    """
    Pipelineの数値パラメータを検証する。
    """
    if top_k <= 0:
        raise ValueError(
            "top_kは1以上を指定してください。"
        )

    if max_context_chars <= 0:
        raise ValueError(
            "max_context_charsは1以上を指定してください。"
        )


# ============================================================
# Document RAG Pipeline
# ============================================================

def run_document_rag(
    query: str,
    paper_ids: list[str],
    top_k: int = DEFAULT_TOP_K,
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
) -> DocumentRAGResult:
    """
    Document RAGの一連の処理を実行する。

    処理:
        1. ユーザー質問と論文IDを検証
        2. 指定論文内から関連チャンクを検索
        3. 検索結果を回答生成用コンテキストに整形
        4. Geminiで回答を生成
        5. 回答・検索結果・参照情報をまとめて返す

    Args:
        query:
            ユーザーの質問
        paper_ids:
            検索対象とする論文ID
        top_k:
            取得する関連チャンク数
        max_context_chars:
            回答生成に使用するコンテキストの最大文字数

    Returns:
        Document RAGの実行結果
    """
    normalized_query = normalize_query(
        query=query
    )

    normalized_paper_ids = normalize_paper_ids(
        paper_ids=paper_ids
    )

    validate_pipeline_parameters(
        top_k=top_k,
        max_context_chars=max_context_chars,
    )

    # 1. 関連チャンクを検索
    retrieved_chunks = retrieve_document_chunks(
        query=normalized_query,
        paper_ids=normalized_paper_ids,
        top_k=top_k,
    )

    # 2. 回答生成用コンテキストを作成
    context = build_document_context(
        retrieved_chunks=retrieved_chunks,
        max_context_chars=max_context_chars,
    )

    # 3. 回答を生成
    answer = generate_document_answer(
        query=normalized_query,
        context=context,
    )

    # 4. UI表示用の参照情報を作成
    sources = build_document_sources(
        retrieved_chunks=retrieved_chunks
    )

    return {
        "query": normalized_query,
        "paper_ids": normalized_paper_ids,
        "answer": answer,
        "context": context,
        "retrieved_chunks": retrieved_chunks,
        "sources": sources,
    }


# ============================================================
# 結果表示用
# ============================================================

def print_document_rag_result(
    result: DocumentRAGResult,
    show_context: bool = False,
    show_chunks: bool = False,
) -> None:
    """
    Document RAGの実行結果をターミナルに表示する。

    Args:
        result:
            run_document_rag()の戻り値
        show_context:
            LLMへ渡したコンテキストを表示するか
        show_chunks:
            検索チャンク本文を表示するか
    """
    print("=== Document RAG Result ===")
    print()
    print(f"query: {result['query']}")
    print(f"paper_ids: {result['paper_ids']}")
    print()

    print("=== Answer ===")
    print()
    print(result["answer"])

    print()
    print("=" * 70)
    print("=== Sources ===")

    for source in result["sources"]:
        print(
            f"[{source['rank']}] "
            f"paper_id={source['paper_id']}, "
            f"source_file={source['source_file']}, "
            f"chunk_id={source['chunk_id']}, "
            f"chunk_index={source['chunk_index']}, "
            f"distance={float(source['distance']):.6f}"
        )

    if show_context:
        print()
        print("=" * 70)
        print("=== Context ===")
        print()
        print(result["context"])

    if show_chunks:
        print()
        print("=" * 70)
        print("=== Retrieved Chunks ===")

        for rank, chunk in enumerate(
            result["retrieved_chunks"],
            start=1,
        ):
            print()
            print("-" * 70)
            print(f"[{rank}] {chunk['chunk_id']}")
            print(f"distance: {chunk['distance']:.6f}")
            print(f"metadata: {chunk['metadata']}")
            print()
            print(chunk["text"])


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    Document RAG Pipeline単体の動作確認。
    """
    query = (
        "この実践では、生徒は具体的に"
        "どのような活動をしましたか？"
    )

    paper_ids = ["P_0001"]

    result = run_document_rag(
        query=query,
        paper_ids=paper_ids,
        top_k=5,
    )

    print_document_rag_result(
        result=result,
        show_context=False,
        show_chunks=False,
    )


if __name__ == "__main__":
    main()