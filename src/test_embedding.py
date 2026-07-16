from utils.gemini_client import get_gemini_client


def main():
    client = get_gemini_client()

    text = "タブレット端末"

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )

    embedding = result.embeddings[0].values

    print("入力テキスト:", text)
    print("ベクトル次元数:", len(embedding))
    print("先頭10要素:", embedding[:10])


if __name__ == "__main__":
    main()