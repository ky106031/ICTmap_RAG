import json
import os
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
from dotenv import load_dotenv
from google import genai


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
NODE_EMBEDDINGS_PATH = BASE_DIR / "data" / "node_embeddings.json"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "gemini-embedding-001"


GROUNDING_TOP_K = {
    "Grade": 1,
    "Field": 1,
    "Unit": 3,
    "ICT_Hardware": 3,
    "ICT_Software": 1,
    "ICT_Artifact": 3,
    "ICT_Function": 3,
    "Educational_Opportunity": 3,
    "Educational_Effect": 3,
}


def load_node_embeddings() -> List[Dict[str, Any]]:
    with open(NODE_EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY が .env に設定されていません。")

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_embedding(client, text: str) -> List[float]:
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    return result.embeddings[0].values


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    denominator = np.linalg.norm(v1) * np.linalg.norm(v2)

    if denominator == 0:
        return 0.0

    return float(np.dot(v1, v2) / denominator)


def search_similar_nodes(
    query_text: str,
    target_label: str,
    top_k: int,
) -> List[str]:
    client = get_gemini_client()
    node_embeddings = load_node_embeddings()

    query_embedding = generate_embedding(client, query_text)

    candidates = []

    for node in node_embeddings:
        if node.get("label") != target_label:
            continue

        score = cosine_similarity(
            query_embedding,
            node["embedding"],
        )

        candidates.append(
            {
                "name": node["name"],
                "score": score,
            }
        )

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True,
    )

    return [candidate["name"] for candidate in candidates[:top_k]]


def ground_conditions(
    raw_conditions: Dict[str, Any],
    top_k: int = 3,
) -> Dict[str, List[str]]:
    grounded_conditions = {}

    for label, value in raw_conditions.items():
        if value is None:
            continue

        if isinstance(value, str) and value.strip() == "":
            continue

        label_top_k = GROUNDING_TOP_K.get(label, top_k)

        candidates = search_similar_nodes(
            query_text=value,
            target_label=label,
            top_k=label_top_k,
        )

        if candidates:
            grounded_conditions[label] = candidates

    return grounded_conditions


def main():
    raw_conditions = {
        "Grade": "小学5年生",
        "Field": None,
        "Unit": None,
        "ICT_Hardware": "タブレット",
        "ICT_Software": "Instagram",
        "ICT_Artifact": None,
        "ICT_Function": None,
        "Educational_Opportunity": None,
        "Educational_Effect": "観察への意欲を高めたい",
    }

    grounded_conditions = ground_conditions(raw_conditions)

    print("=== Raw Conditions ===")
    print(raw_conditions)

    print("\n=== Grounded Conditions ===")
    for label, values in grounded_conditions.items():
        print(f"{label}: {values}")


if __name__ == "__main__":
    main()