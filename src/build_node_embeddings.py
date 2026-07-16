from pathlib import Path
import json
import os
import re
import time
from typing import Dict, List

from dotenv import load_dotenv
from neo4j import GraphDatabase

from utils.gemini_client import get_gemini_client


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "data" / "node_embeddings.json"

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "ictmap")

EMBEDDING_MODEL = "gemini-embedding-001"

# 無料枠は100 requests/minuteだったため、余裕を持って90に制限
MAX_REQUESTS_PER_MINUTE = 90
REQUEST_INTERVAL_SECONDS = 60 / MAX_REQUESTS_PER_MINUTE

TARGET_LABELS = [
    "Grade",
    "Field",
    "Unit",
    "ICT_Hardware",
    "ICT_Software",
    "ICT_Artifact",
    "ICT_Function",
    "Educational_Opportunity",
    "Educational_Effect",
]


def safe_identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(value)):
        raise ValueError(f"Invalid Neo4j identifier: {value}")
    return value


def fetch_nodes_from_neo4j() -> List[Dict[str, str]]:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    )

    nodes = []

    with driver.session(database=NEO4J_DATABASE) as session:
        for label in TARGET_LABELS:
            safe_label = safe_identifier(label)

            query = f"""
            MATCH (n:{safe_label})
            WHERE n.name IS NOT NULL AND n.name <> ""
            RETURN DISTINCT n.name AS name
            ORDER BY name
            """

            result = session.run(query)

            for record in result:
                nodes.append({
                    "label": label,
                    "name": record["name"],
                    "text": record["name"],
                })

    driver.close()
    return nodes


def load_existing_embeddings() -> Dict[str, Dict]:
    if not OUTPUT_PATH.exists():
        return {}

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing = {}
    for item in data:
        key = f'{item["label"]}::{item["name"]}'
        existing[key] = item

    return existing


def save_embeddings(embedded_nodes: List[Dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_nodes, f, ensure_ascii=False, indent=2)


def generate_embedding(client, text: str) -> List[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def wait_for_rate_limit(last_request_time: float) -> float:
    elapsed = time.time() - last_request_time

    if elapsed < REQUEST_INTERVAL_SECONDS:
        time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)

    return time.time()


def main():
    client = get_gemini_client()

    nodes = fetch_nodes_from_neo4j()
    existing = load_existing_embeddings()

    embedded_nodes = list(existing.values())

    print(f"対象ノード数: {len(nodes)}")
    print(f"既存Embedding数: {len(existing)}")
    print(f"新規作成予定数: {len(nodes) - len(existing)}")
    print(f"レート制限: 最大 {MAX_REQUESTS_PER_MINUTE} requests/minute")
    print("-" * 60)

    last_request_time = 0.0

    for i, node in enumerate(nodes, start=1):
        key = f'{node["label"]}::{node["name"]}'

        if key in existing:
            print(f"[{i}/{len(nodes)}] SKIP {node['label']}: {node['name']}")
            continue

        print(f"[{i}/{len(nodes)}] EMBED {node['label']}: {node['name']}")

        last_request_time = wait_for_rate_limit(last_request_time)
        embedding = generate_embedding(client, node["text"])

        embedded_node = {
            "label": node["label"],
            "name": node["name"],
            "text": node["text"],
            "embedding": embedding,
        }

        embedded_nodes.append(embedded_node)

        # 途中で止まっても再開できるように毎回保存
        save_embeddings(embedded_nodes)

    # 保存順を整える
    label_order = {label: idx for idx, label in enumerate(TARGET_LABELS)}
    embedded_nodes.sort(
        key=lambda x: (
            label_order.get(x["label"], 999),
            x["name"],
        )
    )

    save_embeddings(embedded_nodes)

    print("-" * 60)
    print(f"保存完了: {OUTPUT_PATH}")
    print(f"保存Embedding数: {len(embedded_nodes)}")


if __name__ == "__main__":
    main()