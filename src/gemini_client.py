import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parents[1]

RETRYABLE_STATUS_CODES = [
    408,
    429,
    500,
    502,
    503,
    504,
]


def create_gemini_client() -> genai.Client:
    """
    Gemini APIクライアントを作成する。

    408 / 429 / 5xx などの一時的なAPIエラーについては、
    SDK側で指数バックオフによる自動再試行を行う。
    """
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEYが設定されていません。\n"
            "プロジェクトルートの.envを確認してください。"
        )

    retry_options = types.HttpRetryOptions(
        # 初回リクエストを含めて最大5回試行
        attempts=5,

        # 最初のretryまで0.5秒
        initial_delay=0.5,

        # 0.5 → 1.0 → 2.0 → 4.0 ... と増加
        exp_base=2.0,

        # 発表中に長時間待たせないため最大4秒
        max_delay=4.0,

        # retryタイミングを少しランダム化
        jitter=0.5,

        # 一時的な障害のみretry
        http_status_codes=RETRYABLE_STATUS_CODES,
    )

    http_options = types.HttpOptions(
        retry_options=retry_options,
    )

    return genai.Client(
        api_key=api_key,
        http_options=http_options,
    )
    