import asyncio
import os

from mcp import Client


MCP_URL = os.getenv(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp",
)


async def main():

    print("=" * 60)
    print("WIKI MCP ACCESS CONTROL TEST")
    print("=" * 60)
    print(f"Server: {MCP_URL}")

    async with Client(MCP_URL) as client:

        print("\n[1] CONNECTION")
        print("Connected to MCP server.")

        tools_result = await client.list_tools()

        print("\n[2] AVAILABLE TOOLS")

        for tool in tools_result.tools:
            print(f"  - {tool.name}")

        print("\n[3] PING")

        result = await client.call_tool("ping", {})
        print(result)

        print("\n[4] WIKI STATUS")

        status = await client.call_tool(
            "wiki_status",
            {},
        )

        print(status)

        print("\n[5] LIST FILES")

        files = await client.call_tool(
            "list_wiki_files",
            {"limit": 10},
        )

        print(files)

        print("\n[6] TIER 1 ACCESS TEST")

        tier1_file = "tier1/assassins-creed-black-flag-resynced-index.md"

        result = await client.call_tool(
            "get_file_tier_info",
            {
                "path": tier1_file,
            },
        )

        print(result)

        print("\n[7] TIER 2 ACCESS TEST")

        tier2_file = "tier2/game-systems/dragons-dogma-2.md"

        result = await client.call_tool(
            "get_file_tier_info",
            {
                "path": tier2_file,
            },
        )

        print(result)

        print("\n[8] TIER 3 ACCESS TEST")

        tier3_file = "tier3/a-favor-for-radovid.md"

        result = await client.call_tool(
            "get_file_tier_info",
            {
                "path": tier3_file,
            },
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())
