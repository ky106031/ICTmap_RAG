from pathlib import Path

from google.genai import types

from gemini_client import create_gemini_client


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

GENERATION_MODEL = "gemini-2.5-flash"

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_OUTPUT_TOKENS = 4096


# ============================================================
# Validation
# ============================================================

def validate_answer_inputs(
    query: str,
    context: str,
) -> tuple[str, str]:

    query = query.strip()
    context = context.strip()

    if not query:
        raise ValueError(
            "ユーザーの質問が空です。"
        )

    if not context:
        raise ValueError(
            "回答生成に使用するコンテキストが空です。"
        )

    return query, context


# ============================================================
# Prompt
# ============================================================

def build_document_answer_prompt(
    query: str,
    context: str,
) -> str:

    (
        normalized_query,
        normalized_context,
    ) = validate_answer_inputs(
        query,
        context,
    )

    return f"""
あなたは、ICTを活用した理科教育実践について、
研究論文を根拠として教師の授業づくりを支援するアシスタントです。

ユーザーは1件だけでなく、
複数の教育実践を同時に選択して質問することがあります。

==================================================
【基本ルール】
==================================================

1. 論文に書かれている事実を説明する場合は、
   提供された論文本文だけを根拠にしてください。

2. 論文本文に存在しない内容を、
   論文に書かれている事実として表現してはいけません。

3. 複数の実践が与えられている場合は、
   それぞれの実践を区別してください。

4. ユーザーが比較を求めた場合は、
   共通点・相違点を整理してください。

5. ユーザーが複数実践を組み合わせた授業案を求めた場合は、
   各実践から参考にした要素を明確にしながら、
   新しい授業案を提案してください。

6. 新しい授業案や応用案は、
   論文に書かれた事実そのものではありません。
   「ここからは論文を踏まえた提案です」
   などと区別してください。

7. 別学年、別単元、別ICTなどへの応用も可能です。

8. 検索距離、チャンクID、Embedding、
   paper_idなどの内部情報は回答に表示しないでください。

9. 回答は日本語で作成してください。

==================================================
【回答の考え方】
==================================================

単一実践についての質問の場合は、
その実践について直接回答してください。

複数実践についての質問の場合は、
必要に応じて次のような構成を使用してください。

【各実践から参考にできる点】

それぞれの実践について、
論文本文から確認できる内容を整理してください。

【実践間の共通点・相違点】

比較が必要な場合に整理してください。

【授業への応用案】

複数の研究知見を組み合わせて、
ユーザーの条件に合った授業を提案してください。

【実施時の留意点】

学年差、既習事項、授業時間、
ICT環境、安全面などを説明してください。

ただし、質問に応じて不要な見出しは省略してください。

==================================================
【ユーザーの質問】
==================================================

{normalized_query}

==================================================
【選択された実践の論文情報】
==================================================

{normalized_context}

==================================================
【回答】
==================================================
""".strip()


# ============================================================
# Generation
# ============================================================

def generate_document_answer(
    query: str,
    context: str,
    model: str = GENERATION_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
) -> str:

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