import os
from dotenv import load_dotenv
from google import genai


def get_gemini_client():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY が .env に設定されていません。")

    return genai.Client(api_key=api_key)