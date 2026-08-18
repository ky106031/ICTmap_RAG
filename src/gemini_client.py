import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]


# ============================================================
# Retry対象のHTTPステータスコード
# ============================================================

RETRYABLE_STATUS_CODES = [
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
]


# ============================================================
# Retry設定
# ============================================================

RETRY_ATTEMPTS = 4
RETRY_INITIAL_DELAY = 0.5
RETRY_EXP_BASE = 2.0
RETRY_MAX_DELAY = 4.0
RETRY_JITTER = 0.5


# ============================================================
# Geminiクライアント
# ============================================================

def create_gemini_client() -> genai.Client:
    """
    Gemini APIクライアントを作成する。

    GEMINI_API_KEYはプロジェクトルートの.envから読み込む。

    408 / 429 / 5xx系の一時的なAPIエラーについては、
    Google GenAI SDK側で指数バックオフによる再試行を行う。

    Returns:
        Retry設定済みのGemini APIクライアント
    """
    load_dotenv(
        BASE_DIR / ".env"
    )

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEYが設定されていません。\n"
            "プロジェクトルートの.envを確認してください。"
        )

    retry_options = types.HttpRetryOptions(
        attempts=RETRY_ATTEMPTS,
        initial_delay=RETRY_INITIAL_DELAY,
        exp_base=RETRY_EXP_BASE,
        max_delay=RETRY_MAX_DELAY,
        jitter=RETRY_JITTER,
        http_status_codes=RETRYABLE_STATUS_CODES,
    )

    http_options = types.HttpOptions(
        retry_options=retry_options,
    )

    return genai.Client(
        api_key=api_key,
        http_options=http_options,
    )


# ============================================================
# 動作確認
# ============================================================

def main() -> None:
    """
    Geminiクライアント単体の動作確認。
    """
    client = create_gemini_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            "「Gemini client OK」とだけ"
            "返してください。"
        ),
    )

    if not response.text:
        raise RuntimeError(
            "Gemini APIから応答が返されませんでした。"
        )

    print(
        response.text.strip()
    )


if __name__ == "__main__":
    main()