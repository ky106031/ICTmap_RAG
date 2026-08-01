import os
from pathlib import Path
from typing import Any, TypedDict

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

# cleaned_textから作成した新しいコレクション
CHROMA_COLLECTION_NAME = "paper_chunks_cleaned_v1"

# document_indexer.pyと同じモデル・次元数を使用
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768

DEFAULT_TOP_K = 5


# ============================================================
# 型定義
# ============================================================

class RetrievedChunk(TypedDict):
    chunk_id: str
    distance: float
    metadata: dict[str, Any]
    text: str


# ============================================================
# Geminiクライアント
# ============================================================

def create_gemini_client() -> genai.Client:
    """
    .envからGEMINI_API_KEYを読み込み、
    Gemini APIクライアントを作成する。
    """
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEYが設定されていません。\n"
            "プロジェクトルートの.envを確認してください。"
        )

    return genai.Client(api_key=api_key)


# ============================================================
# Chromaコレクション
# ============================================================

def get_chroma_collection() -> chromadb.Collection:
    """
    cleaned_text由来のDocument RAG用コレクションを取得する。
    """
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Chromaの保存先が見つかりません: {CHROMA_DIR}\n"
            "先にdocument_indexer.pyを実行してください。"
        )

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    try:
        collection = chroma_client.get_collection(
            name=CHROMA_COLLECTION_NAME
        )
    except Exception as error:
        raise RuntimeError(
            "Document RAG用のChromaコレクションが"
            "見つかりません。\n"
            f"コレクション名: {CHROMA_COLLECTION_NAME}\n"
            "先にdocument_indexer.pyを実行してください。"
        ) from error

    if collection.count() == 0:
        raise RuntimeError(
            f"{CHROMA_COLLECTION_NAME} に"
            "チャンクが登録されていません。"
        )

    return collection


# ============================================================
# 質問Embedding
# ============================================================

def embed_query(
    client: genai.Client,
    query: str,
) -> list[float]:
    """
    検索質問のEmbeddingを生成する。

    インデックス登録時はRETRIEVAL_DOCUMENTを使用しているため、
    検索質問側ではRETRIEVAL_QUERYを使用する。
    """
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError(
            "検索質問が空です。"
        )

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=normalized_query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    if not response.embeddings:
        raise RuntimeError(
            "Gemini APIから質問Embeddingが返されませんでした。"
        )

    query_embedding = response.embeddings[0].values

    if not query_embedding:
        raise RuntimeError(
            "質問Embeddingの値が空です。"
        )

    return query_embedding


# ============================================================
# 論文IDの検証・検索条件
# ============================================================

def normalize_paper_ids(
    paper_ids: list[str],
) -> list[str]:
    """
    paper_idsから空文字や重複を除去する。
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


def build_paper_filter(
    paper_ids: list[str],
) -> dict[str, Any]:
    """
    Chroma検索用のpaper_idフィルタを作成する。
    """
    normalized_ids = normalize_paper_ids(
        paper_ids=paper_ids
    )

    if len(normalized_ids) == 1:
        return {
            "paper_id": normalized_ids[0]
        }

    return {
        "paper_id": {
            "$in": normalized_ids
        }
    }


def count_target_chunks(
    collection: chromadb.Collection,
    paper_ids: list[str],
) -> int:
    """
    指定された論文IDに該当するチャンク数を取得する。
    """
    paper_filter = build_paper_filter(
        paper_ids=paper_ids
    )

    result = collection.get(
        where=paper_filter,
        include=[],
    )

    return len(result.get("ids", []))


# ============================================================
# 検索結果の整形
# ============================================================

def format_query_results(
    query_results: dict[str, Any],
) -> list[RetrievedChunk]:
    """
    Chromaの検索結果を扱いやすい形式へ変換する。
    """
    result_ids = query_results.get("ids") or [[]]
    result_documents = (
        query_results.get("documents") or [[]]
    )
    result_metadatas = (
        query_results.get("metadatas") or [[]]
    )
    result_distances = (
        query_results.get("distances") or [[]]
    )

    ids = result_ids[0]
    documents = result_documents[0]
    metadatas = result_metadatas[0]
    distances = result_distances[0]

    retrieved_chunks: list[RetrievedChunk] = []

    for chunk_id, text, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        normalized_metadata = (
            metadata if metadata is not None else {}
        )

        retrieved_chunks.append(
            {
                "chunk_id": str(chunk_id),
                "distance": float(distance),
                "metadata": dict(normalized_metadata),
                "text": str(text),
            }
        )

    return retrieved_chunks


# ============================================================
# Document Retriever
# ============================================================

def retrieve_document_chunks(
    query: str,
    paper_ids: list[str],
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    """
    指定された論文本文から質問に関連するチャンクを取得する。

    API呼び出しは質問Embedding生成の1回のみ。
    登録済み560チャンクのEmbeddingは再生成しない。

    Args:
        query:
            ユーザーの質問
        paper_ids:
            検索対象とする論文IDのリスト
        top_k:
            取得する関連チャンク数

    Returns:
        関連チャンクのリスト
    """
    if top_k <= 0:
        raise ValueError(
            "top_kは1以上を指定してください。"
        )

    normalized_paper_ids = normalize_paper_ids(
        paper_ids=paper_ids
    )

    collection = get_chroma_collection()

    target_chunk_count = count_target_chunks(
        collection=collection,
        paper_ids=normalized_paper_ids,
    )

    if target_chunk_count == 0:
        raise ValueError(
            "指定されたpaper_idに対応するチャンクが"
            "見つかりませんでした。\n"
            f"paper_ids: {normalized_paper_ids}"
        )

    # 対象論文のチャンク数を超えないようにする
    actual_top_k = min(
        top_k,
        target_chunk_count,
    )

    gemini_client = create_gemini_client()

    # ここで質問文1件だけEmbeddingする
    query_embedding = embed_query(
        client=gemini_client,
        query=query,
    )

    paper_filter = build_paper_filter(
        paper_ids=normalized_paper_ids
    )

    query_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=actual_top_k,
        where=paper_filter,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    return format_query_results(
        query_results=query_results
    )


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    document_retriever.py単体での動作確認。
    """
    query = (
        "この実践では、生徒は具体的に"
        "どのような活動をしましたか？"
    )

    paper_ids = ["P_0001"]

    top_k = 5

    print("=== Document Retrieval Results ===")
    print(f"collection: {CHROMA_COLLECTION_NAME}")
    print(f"query: {query}")
    print(f"paper_ids: {paper_ids}")
    print()

    retrieved_chunks = retrieve_document_chunks(
        query=query,
        paper_ids=paper_ids,
        top_k=top_k,
    )

    print(
        f"retrieved_chunks: "
        f"{len(retrieved_chunks)}"
    )

    for rank, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):
        print()
        print("=" * 70)
        print(
            f"[{rank}] chunk_id: "
            f"{chunk['chunk_id']}"
        )
        print(
            f"distance: "
            f"{chunk['distance']}"
        )
        print(
            f"metadata: "
            f"{chunk['metadata']}"
        )
        print("text:")
        print(chunk["text"])


if __name__ == "__main__":
    main()