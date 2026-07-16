import os
import time
from pathlib import Path
from typing import List, Dict, Any

import chromadb
import pymupdf4llm
from dotenv import load_dotenv
from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
PAPERS_DIR = BASE_DIR / "data" / "papers"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

CHROMA_COLLECTION_NAME = "paper_chunks"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

EMBEDDING_INTERVAL_SECONDS = 1.0


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY が .env に設定されていません。")

    return genai.Client(api_key=GEMINI_API_KEY)


def get_chroma_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME
    )

    return collection


def get_pdf_files() -> List[Path]:
    if not PAPERS_DIR.exists():
        raise FileNotFoundError(f"PDFフォルダが存在しません: {PAPERS_DIR}")

    return sorted(PAPERS_DIR.glob("*.pdf"))


def get_paper_id(pdf_path: Path) -> str:
    return pdf_path.stem


def pdf_to_markdown(pdf_path: Path) -> str:
    markdown_text = pymupdf4llm.to_markdown(str(pdf_path))
    return markdown_text


def split_text(markdown_text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",
            "\n# ",
            "\n\n",
            "\n",
            "。",
            "、",
            " ",
            "",
        ],
    )

    chunks = splitter.split_text(markdown_text)

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def generate_embedding(client, text: str) -> List[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return result.embeddings[0].values


def build_chunk_records(
    paper_id: str,
    source_file: str,
    chunks: List[str],
) -> List[Dict[str, Any]]:
    records = []

    for index, text in enumerate(chunks):
        chunk_id = f"{paper_id}_{index:04d}"

        records.append(
            {
                "id": chunk_id,
                "text": text,
                "metadata": {
                    "paper_id": paper_id,
                    "source_file": source_file,
                    "chunk_index": index,
                },
            }
        )

    return records


def index_pdf(
    pdf_path: Path,
    collection,
    gemini_client,
) -> int:
    paper_id = get_paper_id(pdf_path)

    print("=" * 70)
    print(f"PDF処理開始: {pdf_path.name}")
    print(f"paper_id: {paper_id}")

    markdown_text = pdf_to_markdown(pdf_path)
    chunks = split_text(markdown_text)

    print(f"チャンク数: {len(chunks)}")

    records = build_chunk_records(
        paper_id=paper_id,
        source_file=pdf_path.name,
        chunks=chunks,
    )

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for i, record in enumerate(records, start=1):
        print(f"  [{i}/{len(records)}] Embedding生成: {record['id']}")

        embedding = generate_embedding(
            client=gemini_client,
            text=record["text"],
        )

        ids.append(record["id"])
        documents.append(record["text"])
        metadatas.append(record["metadata"])
        embeddings.append(embedding)

        time.sleep(EMBEDDING_INTERVAL_SECONDS)

    if ids:
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    print(f"Chroma登録完了: {paper_id}")
    return len(ids)


def main():
    pdf_files = get_pdf_files()

    if not pdf_files:
        print(f"PDFが見つかりません: {PAPERS_DIR}")
        return

    gemini_client = get_gemini_client()
    collection = get_chroma_collection()

    total_chunks = 0

    print("=== Document Indexing Start ===")
    print(f"PDFフォルダ: {PAPERS_DIR}")
    print(f"Chroma保存先: {CHROMA_DIR}")
    print(f"対象PDF数: {len(pdf_files)}")

    for pdf_path in pdf_files:
        indexed_count = index_pdf(
            pdf_path=pdf_path,
            collection=collection,
            gemini_client=gemini_client,
        )

        total_chunks += indexed_count

    print("\n=== Document Indexing Completed ===")
    print(f"登録チャンク数: {total_chunks}")
    print(f"Chroma Collection: {CHROMA_COLLECTION_NAME}")


if __name__ == "__main__":
    main()