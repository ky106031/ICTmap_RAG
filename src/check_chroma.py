from pathlib import Path

import chromadb


BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
CHROMA_COLLECTION_NAME = "paper_chunks"


def main():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)

    count = collection.count()

    print("=== Chroma Check ===")
    print(f"Chroma保存先: {CHROMA_DIR}")
    print(f"Collection: {CHROMA_COLLECTION_NAME}")
    print(f"登録チャンク数: {count}")

    print("\n=== Peek ===")
    peek = collection.peek(limit=5)

    ids = peek.get("ids", [])
    documents = peek.get("documents", [])
    metadatas = peek.get("metadatas", [])

    for i, chunk_id in enumerate(ids):
        print("\n" + "=" * 70)
        print(f"chunk_id: {chunk_id}")
        print(f"metadata: {metadatas[i]}")
        print("text:")
        print(documents[i][:500])


if __name__ == "__main__":
    main()