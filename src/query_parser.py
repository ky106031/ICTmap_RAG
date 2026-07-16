import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field as PydanticField


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PARSE_MODEL = os.getenv("GEMINI_PARSE_MODEL", "gemini-2.5-flash")


class QueryConditions(BaseModel):
    Grade: Optional[str] = PydanticField(
        default=None,
        description="学年。例: 小学5年生, 中学3年生, 高校3年生"
    )
    Field: Optional[str] = PydanticField(
        default=None,
        description="理科の領域。例: 物理, 化学, 生物, 地学"
    )
    Unit: Optional[str] = PydanticField(
        default=None,
        description="理科の単元名。例: 生態系とその保全, オームの法則"
    )
    ICT_Hardware: Optional[str] = PydanticField(
        default=None,
        description="ICT機器・端末。例: iPad, タブレット, PC"
    )
    ICT_Software: Optional[str] = PydanticField(
        default=None,
        description="ICTソフトウェア・アプリ。例: Instagram, Excel, FaceTime"
    )
    ICT_Artifact: Optional[str] = PydanticField(
        default=None,
        description="ICTによって作成される成果物。例: 動画, グラフ, 写真"
    )
    ICT_Function: Optional[str] = PydanticField(
        default=None,
        description="ICTが持つ機能。例: 写真撮影, 共有, グラフ化"
    )
    Educational_Opportunity: Optional[str] = PydanticField(
        default=None,
        description="ICTによって可能になる学習活動・教育機会。例: 観察結果を共有する活動"
    )
    Educational_Effect: Optional[str] = PydanticField(
        default=None,
        description="期待する教育効果。例: 観察への意欲を高めたい, 理解を深めたい"
    )


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY が .env に設定されていません。")

    return genai.Client(api_key=GEMINI_API_KEY)


def build_parse_prompt(user_query: str) -> str:
    return f"""
あなたは理科教育ICT活用GraphRAGシステムの検索条件抽出器です。

ユーザー質問から、検索に使う条件だけを抽出してください。

# 抽出ルール
- 明示されている条件だけ抽出してください。
- 推測で補完しないでください。
- 該当しない項目は null にしてください。
- 「小学5年生」「中学3年生」「高校3年生」などは Grade に入れてください。
- 「物理」「化学」「生物」「地学」などは Field に入れてください。
- 「生態系とその保全」「オームの法則」などは Unit に入れてください。
- 「iPad」「タブレット」「PC」などは ICT_Hardware に入れてください。
- 「Instagram」「Excel」「FaceTime」などは ICT_Software に入れてください。
- 「写真」「動画」「グラフ」など、ICTで作られる成果物は ICT_Artifact に入れてください。
- 「写真撮影」「共有」「グラフ化」など、ICTの機能は ICT_Function に入れてください。
- 「共有したい」「発表したい」「比較したい」などの学習活動は Educational_Opportunity に入れてください。
- 「観察への意欲を高めたい」「理解を深めたい」などの目的・効果は Educational_Effect に入れてください。

# ユーザー質問
{user_query}
""".strip()


def parse_query(user_query: str) -> Dict[str, Any]:
    client = get_gemini_client()
    prompt = build_parse_prompt(user_query)

    response = client.models.generate_content(
        model=PARSE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QueryConditions,
            temperature=0,
        ),
    )

    if response.parsed is not None:
        parsed: QueryConditions = response.parsed
        return parsed.model_dump()

    raise ValueError(f"構造化出力の解析に失敗しました。response.text: {response.text}")


def main():
    user_query = (
        "高校3年生でInstagramを活用し、観察への意欲を高めたいです。"
        "どのような授業実践が参考になりますか？"
    )

    raw_conditions = parse_query(user_query)

    print("=== User Query ===")
    print(user_query)

    print("\n=== Parsed Conditions ===")
    print(raw_conditions)


if __name__ == "__main__":
    main()