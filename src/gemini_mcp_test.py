import os
from google import genai


def main():
    api_key = os.getenv("GEMINI_API_KEY")
    mcp_url = os.getenv("MCP_URL")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    if not mcp_url:
        raise RuntimeError("MCP_URL is not set")

    client = genai.Client(api_key=api_key)

    print("Gemini: connected")
    print(f"MCP: {mcp_url}")
    print("Sending request...\n")

    interaction = client.interactions.create(
        model="gemini-3.7-flash",
        input=(
            "Use the connected Wiki MCP to answer this question. "
            "What information is available in the Tier 3 wiki? "
            "Use the MCP tools rather than guessing."
        ),
        tools=[
            {
                "type": "mcp_server",
                "name": "wiki_mcp",
                "url": mcp_url,
            }
        ],
    )

    print("=== GEMINI RESPONSE ===")
    print(interaction.output_text)


if __name__ == "__main__":
    main()