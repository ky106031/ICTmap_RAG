from utils.gemini_client import get_gemini_client


def main():
    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="こんにちは。簡単に自己紹介してください。",
    )

    print(response.text)


if __name__ == "__main__":
    main()