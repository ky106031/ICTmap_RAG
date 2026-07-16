import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
CONTEXT_PATH = BASE_DIR / "data" / "graph_context.txt"
OUTPUT_PATH = BASE_DIR / "data" / "generated_answer.txt"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GENERATE_MODEL = os.getenv("GEMINI_GENERATE_MODEL", "gemini-2.5-flash")


def load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY が .env に設定されていません。")

    return genai.Client(api_key=GEMINI_API_KEY)


def build_prompt(user_query: str, graph_context: str) -> str:
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


def generate_answer(user_query: str) -> str:
    graph_context = load_text(CONTEXT_PATH)
    prompt = build_prompt(user_query, graph_context)

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GENERATE_MODEL,
        contents=prompt,
    )

    return response.text


def main():
    user_query = (
        "高校3年生でInstagramを活用し、観察への意欲を高めたいです。"
        "どのような授業実践が参考になりますか？"
    )

    answer = generate_answer(user_query)
    save_text(answer, OUTPUT_PATH)

    print("=== Answer Generation Completed ===")
    print(f"出力: {OUTPUT_PATH}")
    print("")
    print(answer)


if __name__ == "__main__":
    main()