import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

GENERATION_MODEL = "gemini-3.5-flash"

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_OUTPUT_TOKENS = 4096


# ============================================================
# Geminiクライアント
# ============================================================

def create_gemini_client() -> genai.Client:
    """
    .envからGEMINI_API_KEYを読み込み、
    Gemini APIクライアントを作成する。
    """
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEYが設定されていません。\n"
            "プロジェクトルートの.envを確認してください。"
        )

    return genai.Client(api_key=api_key)


# ============================================================
# 入力検証
# ============================================================

def validate_answer_inputs(
    query: str,
    context: str,
) -> tuple[str, str]:
    """
    ユーザー質問と検索コンテキストを検証する。

    Returns:
        前後の空白を除去したqueryとcontext
    """
    normalized_query = query.strip()
    normalized_context = context.strip()

    if not normalized_query:
        raise ValueError(
            "ユーザーの質問が空です。"
        )

    if not normalized_context:
        raise ValueError(
            "回答生成に使用するコンテキストが空です。"
        )

    return normalized_query, normalized_context


# ============================================================
# プロンプト
# ============================================================

def build_document_answer_prompt(
    query: str,
    context: str,
) -> str:
    """
    Document RAG回答生成用のプロンプトを作成する。

    論文本文に関する事実確認だけでなく、
    論文を参考にした授業への応用・改善提案にも対応する。

    Args:
        query:
            ユーザーの質問
        context:
            document_context_builder.pyで作成した
            論文本文の検索コンテキスト

    Returns:
        Geminiへ渡すプロンプト
    """
    normalized_query, normalized_context = validate_answer_inputs(
        query=query,
        context=context,
    )

    return f"""
あなたは、ICTを活用した理科教育実践について、
論文本文を根拠として教師の授業づくりを支援するアシスタントです。

ユーザーの質問には、大きく次の2種類があります。

・論文に書かれている事実を確認する質問
・論文の実践を参考に、別学年、別単元、別環境などへ
  応用する方法や授業案を検討する質問

質問の意図を読み取り、以下のルールに従って回答してください。

==================================================
【基本ルール】
==================================================

1. 論文に書かれている事実を説明する場合は、
   与えられた論文本文の情報だけを根拠にしてください。

2. 論文本文に存在しない内容を、
   論文に書かれている事実であるかのように表現してはいけません。

3. ユーザーが、次のような応用・改善・相談を求めている場合は、
   論文本文を参考資料として用いながら、
   教育的に妥当と考えられる提案を行ってください。

   ・別学年への応用
   ・別単元への応用
   ・異なる授業時間や人数への調整
   ・異なるICT機器やソフトウェアへの置き換え
   ・授業計画や授業展開への助言
   ・ユーザーが考えている授業案への意見
   ・実践を取り入れる際の工夫や留意点

4. 応用や改善を提案する場合は、
   論文本文に書かれている内容と、
   あなたが論文を踏まえて考えた提案を明確に区別してください。

5. 応用案については、
   論文の実践をそのまま転用するのではなく、
   ユーザーが示した学年、単元、目的、授業環境に合わせて
   調整してください。

6. ユーザーの条件が不足していても、
   合理的な仮定を明示した上で、可能な範囲の案を提示してください。
   回答に必要な重要条件が大きく不足している場合は、
   最後に確認したい点を1つだけ示してください。

7. 論文本文から確認できないことを断定してはいけません。
   不確かな点は、
   「論文本文からは確認できません」
   「ここからは論文を踏まえた提案です」
   などと明示してください。

8. 検索距離、チャンクID、内部処理、Embeddingなどの
   システム内部情報は回答本文に含めないでください。

9. 回答は日本語で作成してください。

==================================================
【回答方法】
==================================================

質問が論文内容の確認である場合は、
質問に直接関係する内容を優先し、
簡潔かつ具体的に回答してください。

複数の活動や手順がある場合は、
順序や関係が分かるように整理してください。

質問が授業への応用や相談である場合は、
原則として次の構成で回答してください。

回答全体は、原則として800～1500字程度にまとめてください。
ユーザーが詳細な授業案を求めた場合のみ、
必要に応じて長くしてください。

【この実践から参考にできる点】

論文本文から確認できる、
応用の根拠となる実践内容を簡潔に説明してください。

【授業への応用案】

ユーザーが示した条件に合わせて、
具体的な授業の流れ、活動、ICTの使い方などを提案してください。

【実施時の留意点】

学年差、既習事項、授業時間、ICT環境、安全面、
発達段階など、実施時に考慮すべき点を説明してください。

ただし、質問内容によっては、
この見出しを無理にすべて使用する必要はありません。

==================================================
【ユーザーの質問】
==================================================

{normalized_query}

==================================================
【論文本文から検索された情報】
==================================================

{normalized_context}

==================================================
【回答】
==================================================
""".strip()


# ============================================================
# 回答生成
# ============================================================

def generate_document_answer(
    query: str,
    context: str,
    model: str = GENERATION_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
) -> str:
    """
    検索コンテキストに基づいて回答を生成する。

    Args:
        query:
            ユーザーの質問
        context:
            論文本文から作成した検索コンテキスト
        model:
            回答生成に使用するGeminiモデル
        temperature:
            出力のランダム性
        max_output_tokens:
            最大出力トークン数

    Returns:
        生成された回答文
    """
    if not 0.0 <= temperature <= 2.0:
        raise ValueError(
            "temperatureは0.0以上2.0以下で指定してください。"
        )

    if max_output_tokens <= 0:
        raise ValueError(
            "max_output_tokensは1以上を指定してください。"
        )

    prompt = build_document_answer_prompt(
        query=query,
        context=context,
    )

    client = create_gemini_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
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
    Retriever、Context Builder、Answer Generatorを
    接続した動作確認。
    """
    from document_context_builder import (
        build_document_context,
    )
    from document_retriever import (
        retrieve_document_chunks,
    )

    query = (
        "この実践では、生徒は具体的に"
        "どのような活動をしましたか？"
    )

    paper_ids = ["P_0001"]

    retrieved_chunks = retrieve_document_chunks(
        query=query,
        paper_ids=paper_ids,
        top_k=5,
    )

    context = build_document_context(
        retrieved_chunks=retrieved_chunks
    )

    answer = generate_document_answer(
        query=query,
        context=context,
    )

    print("=== Document Answer ===")
    print()
    print(answer)


if __name__ == "__main__":
    main()