import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

GENERATION_MODEL = "gemini-2.5-flash"

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_OUTPUT_TOKENS = 2048


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
あなたは、ICTを活用した理科教育実践に関する
論文本文をもとに回答するアシスタントです。

以下のルールを必ず守ってください。

1. 回答は、与えられた論文本文の情報だけを根拠にしてください。
2. 論文本文に書かれていない内容を推測してはいけません。
3. 質問に直接関係する内容を優先し、簡潔かつ具体的に答えてください。
4. 複数の活動や手順がある場合は、順序や関係が分かるように整理してください。
5. 論文本文だけでは答えられない場合は、
   「提示された論文本文からは確認できません」
   と明示してください。
6. 検索距離、チャンクID、内部処理、Embeddingなどの
   システム内部情報は回答本文に含めないでください。
7. 回答は日本語で作成してください。

【ユーザーの質問】
{normalized_query}

【論文本文から検索された情報】
{normalized_context}

【回答】
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