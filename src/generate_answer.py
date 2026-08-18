import os
from pathlib import Path

from gemini_client import create_gemini_client


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

CONTEXT_PATH = (
    BASE_DIR
    / "data"
    / "graph_context.txt"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "generated_answer.txt"
)

GENERATE_MODEL = os.getenv(
    "GEMINI_GENERATE_MODEL",
    "gemini-2.5-flash",
)


# ============================================================
# ファイル操作
# ============================================================

def load_text(
    path: Path,
) -> str:
    """
    テキストファイルを読み込む。
    """
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return f.read()


def save_text(
    text: str,
    path: Path,
) -> None:
    """
    テキストをファイルへ保存する。
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)


# ============================================================
# Geminiクライアント
# ============================================================

def get_gemini_client():
    """
    共通のGemini APIクライアントを取得する。

    gemini_client.py側で設定されたRetry処理が適用される。
    """
    return create_gemini_client()


# ============================================================
# プロンプト
# ============================================================

def build_prompt(
    user_query: str,
    graph_context: str,
) -> str:
    """
    GraphRAG回答生成用のプロンプトを作成する。
    """
    return f"""
あなたは小学校・中学校・高等学校の理科教員向けに授業実践を紹介する教育支援AIです。

あなたの役割は、
知識グラフの情報をそのまま説明することではありません。

知識グラフから取得された関係性を根拠として、
教師が授業づくりに活用できる自然な日本語へ翻訳してください。

==================================================
【重要な制約】
==================================================

・GraphRAG検索結果以外の情報は絶対に使用しないこと。
・検索結果に存在しない内容は推測しないこと。
・ICT機能・教育機会・教育効果の対応関係は、
  必ずGraphRAG検索結果の「関係パス」に基づいて説明すること。
・関係パスは回答へそのまま書かず、
  自然な文章へ変換すること。
・論文ID(P_0032など)は回答へ表示しないこと。

==================================================
【回答フォーマット】
==================================================

# 検索結果

検索条件に一致する授業実践が〇件見つかりました。
検索条件との一致度が高い順に紹介します。

--------------------------------------------------

# 実践①

【論文】

著者（発行年）

論文タイトル

【基本情報】

・学年

・領域

・単元

・使用したICT

【この実践が参考になる理由】

GraphRAGの関係性を自然な日本語で説明してください。

単なるノード列挙ではなく、

・ICTのどの機能を利用しているのか

・その機能によってどのような学習活動（教育機会）が可能になるのか

・その活動によってどのような教育効果につながるのか

を教師が理解しやすい文章で説明してください。

複数の教育効果が存在する場合は、

教育効果ごとに段落を分けてください。

例)

○○というICT機能を利用することで、
児童生徒は〜という活動を行うことができます。

この活動を通して、
〜という教育効果が期待できます。

【根拠論文】

・著者

・論文タイトル

・発行年

・URL（存在する場合）

==================================================
【ユーザー質問】
==================================================

{user_query}

==================================================
【GraphRAG検索結果】
==================================================

{graph_context}

==================================================
【回答】
==================================================
""".strip()


# ============================================================
# 回答生成
# ============================================================

def generate_answer(
    user_query: str,
) -> str:
    """
    保存済みGraph Contextから回答を生成する。
    """
    graph_context = load_text(
        CONTEXT_PATH
    )

    prompt = build_prompt(
        user_query=user_query,
        graph_context=graph_context,
    )

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GENERATE_MODEL,
        contents=prompt,
    )

    answer = response.text

    if not answer:
        raise RuntimeError(
            "Gemini APIから回答が返されませんでした。"
        )

    return answer.strip()


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    generate_answer.py単体の動作確認。
    """
    user_query = (
        "高校3年生でInstagramを活用し、"
        "観察への意欲を高めたいです。"
        "どのような授業実践が参考になりますか？"
    )

    answer = generate_answer(
        user_query
    )

    save_text(
        answer,
        OUTPUT_PATH,
    )

    print(
        "=== Answer Generation Completed ==="
    )

    print(
        f"出力: {OUTPUT_PATH}"
    )

    print()
    print(
        answer
    )


if __name__ == "__main__":
    main()