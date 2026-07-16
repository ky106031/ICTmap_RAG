import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from dotenv import load_dotenv
from google import genai


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

CHROMA_COLLECTION_NAME = "paper_chunks"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY が .env に設定されていません。")

    return genai.Client(api_key=GEMINI_API_KEY)


def get_chroma_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)


def generate_embedding(client, text: str) -> List[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return result.embeddings[0].values


def retrieve_document_chunks(
    query: str,
    paper_ids: Optional[List[str]] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    client = get_gemini_client()
    collection = get_chroma_collection()

    query_embedding = generate_embedding(client, query)

    where = None
    if paper_ids:
        if len(paper_ids) == 1:
            where = {"paper_id": paper_ids[0]}
        else:
            where = {"paper_id": {"$in": paper_ids}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        retrieved_chunks.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": distance,
            }
        )

    return retrieved_chunks


def main():
    query = "この実践では、生徒は具体的にどのような活動をしましたか？"

    paper_ids = ["P_0001"]

    chunks = retrieve_document_chunks(
        query=query,
        paper_ids=paper_ids,
        top_k=5,
    )

    print("=== Document Retrieval Results ===")
    print(f"query: {query}")
    print(f"paper_ids: {paper_ids}")
    print(f"retrieved_chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 70)
        print(f"[{i}] chunk_id: {chunk['chunk_id']}")
        print(f"distance: {chunk['distance']}")
        print(f"metadata: {chunk['metadata']}")
        print("text:")
        print(chunk["text"][:800])


if __name__ == "__main__":
    main()