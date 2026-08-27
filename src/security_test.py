import asyncio
import os
from mcp import Client

async def main():
    url = os.getenv("MCP_URL", "http://127.0.0.1:8001/mcp")

    print("Connecting to:", url)

    async with Client(url) as client:
        print("Connected.\n")

        print("=== SERVER STATUS ===")
        status = await client.call_tool("wiki_status", {})
        print(status)

        print("\n=== TIER 1 TEST ===")
        result = await client.call_tool(
            "get_file_tier_info",
            {"path": "tier1/games-index.md"}
        )
        print(result)

        print("\n=== TIER 2 TEST ===")
        result = await client.call_tool(
            "get_file_tier_info",
            {
                "path": "tier2/dragons-dogma-2-quests/a-beggars-tale.md"
            }
        )
        print(result)

        print("\n=== TIER 3 TEST ===")
        result = await client.call_tool(
            "get_file_tier_info",
            {"path": "tier3/a-favor-for-radovid.md"}
        )
        print(result)

        print("\n=== READ TIER 1 ===")
        result = await client.call_tool(
            "read_wiki_file",
            {"path": "tier1/games-index.md"}
        )
        print(result)

        print("\n=== READ TIER 2 ===")
        result = await client.call_tool(
            "read_wiki_file",
            {
                "path": "tier2/dragons-dogma-2-quests/a-beggars-tale.md"
            }
        )
        print(result)

        print("\n=== READ TIER 3 ===")
        result = await client.call_tool(
            "read_wiki_file",
            {"path": "tier3/a-favor-for-radovid.md"}
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
