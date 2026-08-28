import os
from google import genai


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents="Reply with exactly: Gemini connection successful."
    )

    print(response.text)


if __name__ == "__main__":
    main()