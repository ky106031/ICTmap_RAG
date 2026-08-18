import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from gemini_client import create_gemini_client


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

NODE_EMBEDDINGS_PATH = (
    BASE_DIR
    / "data"
    / "node_embeddings.json"
)

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


# ============================================================
# ノードEmbedding読み込み
# ============================================================

def load_node_embeddings() -> List[Dict[str, Any]]:
    """
    事前に作成済みのKnowledge GraphノードEmbeddingを読み込む。
    """
    with open(
        NODE_EMBEDDINGS_PATH,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


# ============================================================
# Embedding生成
# ============================================================

def generate_embedding(
    client,
    text: str,
) -> List[float]:
    """
    Gemini Embedding APIを用いて入力テキストをベクトル化する。

    Geminiクライアントはgemini_client.pyで
    共通管理しているため、一時的なAPIエラーには
    Retry設定が適用される。
    """
    normalized_text = text.strip()

    if not normalized_text:
        raise ValueError(
            "Embedding対象のテキストが空です。"
        )

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=normalized_text,
    )

    if not result.embeddings:
        raise RuntimeError(
            "Gemini APIからEmbeddingが返されませんでした。"
        )

    embedding = result.embeddings[0].values

    if not embedding:
        raise RuntimeError(
            "Embeddingの値が空です。"
        )

    return embedding


# ============================================================
# コサイン類似度
# ============================================================

def cosine_similarity(
    vec1: List[float],
    vec2: List[float],
) -> float:
    """
    2つのベクトル間のコサイン類似度を計算する。
    """
    v1 = np.array(
        vec1
    )

    v2 = np.array(
        vec2
    )

    denominator = (
        np.linalg.norm(v1)
        * np.linalg.norm(v2)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(v1, v2)
        / denominator
    )


# ============================================================
# 類似ノード検索
# ============================================================

def search_similar_nodes(
    query_text: str,
    target_label: str,
    top_k: int,
) -> List[str]:
    """
    指定ラベル内から、
    入力条件とEmbedding類似度が高いノードを取得する。
    """
    client = create_gemini_client()

    node_embeddings = (
        load_node_embeddings()
    )

    query_embedding = (
        generate_embedding(
            client=client,
            text=query_text,
        )
    )

    candidates: list[
        dict[str, Any]
    ] = []

    for node in node_embeddings:

        if (
            node.get("label")
            != target_label
        ):
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

    return [
        candidate["name"]
        for candidate
        in candidates[:top_k]
    ]


# ============================================================
# Grounding
# ============================================================

def ground_conditions(
    raw_conditions: Dict[str, Any],
    top_k: int = 3,
) -> Dict[str, List[str]]:
    """
    query_parser.pyで抽出された検索条件を、
    Knowledge Graph上の実在ノードへ接地する。
    """
    grounded_conditions: Dict[
        str,
        List[str],
    ] = {}

    for label, value in (
        raw_conditions.items()
    ):

        if value is None:
            continue

        if (
            isinstance(value, str)
            and value.strip() == ""
        ):
            continue

        label_top_k = (
            GROUNDING_TOP_K.get(
                label,
                top_k,
            )
        )

        candidates = (
            search_similar_nodes(
                query_text=str(value),
                target_label=label,
                top_k=label_top_k,
            )
        )

        if candidates:
            grounded_conditions[
                label
            ] = candidates

    return grounded_conditions


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    node_grounding.py単体の動作確認。
    """
    raw_conditions = {
        "Grade": "小学5年生",
        "Field": None,
        "Unit": None,
        "ICT_Hardware": "タブレット",
        "ICT_Software": "Instagram",
        "ICT_Artifact": None,
        "ICT_Function": None,
        "Educational_Opportunity": None,
        "Educational_Effect": (
            "観察への意欲を高めたい"
        ),
    }

    grounded_conditions = (
        ground_conditions(
            raw_conditions
        )
    )

    print(
        "=== Raw Conditions ==="
    )
    print(
        raw_conditions
    )

    print()
    print(
        "=== Grounded Conditions ==="
    )

    for (
        label,
        values,
    ) in grounded_conditions.items():

        print(
            f"{label}: {values}"
        )


if __name__ == "__main__":
    main()