from pathlib import Path
from typing import Any, TypedDict

import chromadb
from google import genai
from google.genai import types

from gemini_client import create_gemini_client


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = (
    BASE_DIR
    / "data"
    / "chroma_db"
)

CHROMA_COLLECTION_NAME = (
    "paper_chunks_cleaned_v1"
)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768

# 1論文あたりの取得チャンク数
DEFAULT_TOP_K = 3


# ============================================================
# 型定義
# ============================================================

class RetrievedChunk(TypedDict):
    chunk_id: str
    distance: float
    metadata: dict[str, Any]
    text: str


# ============================================================
# Chroma
# ============================================================

def get_chroma_collection() -> chromadb.Collection:

    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Chromaの保存先が見つかりません: "
            f"{CHROMA_DIR}"
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
            f"コレクション名: {CHROMA_COLLECTION_NAME}"
        ) from error

    if collection.count() == 0:

        raise RuntimeError(
            f"{CHROMA_COLLECTION_NAME} に"
            "チャンクが登録されていません。"
        )

    return collection


# ============================================================
# Embedding
# ============================================================

def embed_query(
    client: genai.Client,
    query: str,
) -> list[float]:

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
            output_dimensionality=(
                EMBEDDING_DIMENSION
            ),
        ),
    )

    if not response.embeddings:
        raise RuntimeError(
            "Gemini APIから質問Embeddingが"
            "返されませんでした。"
        )

    embedding = response.embeddings[0].values

    if not embedding:
        raise RuntimeError(
            "質問Embeddingが空です。"
        )

    return embedding


# ============================================================
# paper_id
# ============================================================

def normalize_paper_ids(
    paper_ids: list[str],
) -> list[str]:

    normalized_ids: list[str] = []

    for paper_id in paper_ids:

        normalized_id = paper_id.strip()

        if (
            normalized_id
            and normalized_id not in normalized_ids
        ):
            normalized_ids.append(
                normalized_id
            )

    if not normalized_ids:
        raise ValueError(
            "検索対象のpaper_idsが"
            "指定されていません。"
        )

    return normalized_ids


def count_target_chunks(
    collection: chromadb.Collection,
    paper_id: str,
) -> int:

    result = collection.get(
        where={
            "paper_id": paper_id
        },
        include=[],
    )

    return len(
        result.get(
            "ids",
            [],
        )
    )


# ============================================================
# 検索結果整形
# ============================================================

def format_single_query_results(
    query_results: dict[str, Any],
) -> list[RetrievedChunk]:

    ids = (
        query_results.get("ids")
        or [[]]
    )[0]

    documents = (
        query_results.get("documents")
        or [[]]
    )[0]

    metadatas = (
        query_results.get("metadatas")
        or [[]]
    )[0]

    distances = (
        query_results.get("distances")
        or [[]]
    )[0]

    chunks: list[RetrievedChunk] = []

    for (
        chunk_id,
        text,
        metadata,
        distance,
    ) in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):

        chunks.append(
            {
                "chunk_id": str(
                    chunk_id
                ),
                "distance": float(
                    distance
                ),
                "metadata": dict(
                    metadata or {}
                ),
                "text": str(
                    text
                ),
            }
        )

    return chunks


# ============================================================
# Document Retrieval
# ============================================================

def retrieve_document_chunks(
    query: str,
    paper_ids: list[str],
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    """
    各論文からtop_k件ずつ関連チャンクを取得する。

    複数論文を指定した場合でも、
    特定の論文だけに検索結果が偏らないようにする。
    """

    if top_k <= 0:
        raise ValueError(
            "top_kは1以上を指定してください。"
        )

    normalized_ids = normalize_paper_ids(
        paper_ids
    )

    collection = get_chroma_collection()

    client = create_gemini_client()

    # Embedding APIは質問1件につき1回のみ
    query_embedding = embed_query(
        client=client,
        query=query,
    )

    all_chunks: list[RetrievedChunk] = []

    for paper_id in normalized_ids:

        chunk_count = count_target_chunks(
            collection=collection,
            paper_id=paper_id,
        )

        if chunk_count == 0:
            continue

        actual_top_k = min(
            top_k,
            chunk_count,
        )

        query_results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=actual_top_k,
            where={
                "paper_id": paper_id
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        chunks = format_single_query_results(
            query_results
        )

        all_chunks.extend(
            chunks
        )

    if not all_chunks:

        raise ValueError(
            "指定された論文に対応する"
            "検索チャンクが見つかりませんでした。"
        )

    return all_chunks


# ============================================================
# 動作確認
# ============================================================

def main() -> None:

    query = (
        "2つの実践の共通点と違いを教えてください。"
    )

    paper_ids = [
        "P_0001",
        "P_0002",
    ]

    results = retrieve_document_chunks(
        query=query,
        paper_ids=paper_ids,
        top_k=3,
    )

    for index, chunk in enumerate(
        results,
        start=1,
    ):

        print()
        print("=" * 70)
        print(index)
        print(chunk["metadata"])
        print(chunk["distance"])
        print(chunk["text"][:300])


if __name__ == "__main__":
    main()