from pathlib import Path
import os
import re
from typing import Optional

from mcp.server.mcpserver import MCPServer

try:
    from chat_db import (
        create_conversation,
        save_message,
        get_conversation_messages,
        list_conversations,
        get_conversation,
    )
except Exception:
    create_conversation = save_message = get_conversation_messages = None
    list_conversations = get_conversation = None


BASE_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = BASE_DIR / "wiki-data"
CHAT_DIR = BASE_DIR / "chat-history"

mcp = MCPServer(
    name="Wiki MCP Tier 2",
    version="1.0.0",
    description=(
        "Tier 2+3 MCP server for the persistent game wiki. "
        "This server can access Tier 2 and Tier 3 data. "
        "Tier 1 data is not accessible."
    ),
)


ALLOWED_TIERS = {2, 3}
TIER_NAMES = {2: "tier2", 3: "tier3"}


def get_file_tier(path: Path) -> Optional[int]:
    try:
        relative = path.relative_to(WIKI_DIR).as_posix()
    except ValueError:
        return None

    first = relative.split("/", 1)[0].lower()

    for tier, name in TIER_NAMES.items():
        if first == name:
            return tier

    return None


def get_allowed_files() -> list[Path]:
    if not WIKI_DIR.exists():
        return []

    return sorted(
        p
        for p in WIKI_DIR.rglob("*.md")
        if get_file_tier(p) in ALLOWED_TIERS
    )


def safe_tier2_path(relative_path: str) -> Optional[Path]:
    requested = (WIKI_DIR / relative_path).resolve()

    try:
        requested.relative_to(WIKI_DIR.resolve())
    except ValueError:
        return None

    tier = get_file_tier(requested)

    if tier not in ALLOWED_TIERS:
        return None

    return requested


def excerpt(text: str, query: str, limit: int = 1400) -> str:
    text = text.strip()

    if len(text) <= limit:
        return text

    q = query.lower().strip()
    pos = text.lower().find(q) if q else -1

    start = max(0, pos - 400) if pos >= 0 else 0

    return text[start:start + limit]


@mcp.tool()
def ping() -> str:
    """Check whether the Tier 2 MCP server is running."""
    return "pong"


@mcp.tool()
def list_accessible_tiers() -> list[str]:
    """Return the tiers accessible through this MCP server."""
    return ["tier2", "tier3"]


@mcp.tool()
def get_file_tier_info(path: str) -> str:
    """Return tier information for an accessible wiki file."""
    requested = safe_tier2_path(path)

    if requested is None:
        return "Access denied: Tier 2+3 server cannot access this file."

    tier = get_file_tier(requested)

    return f"File: {path}\nTier: tier{tier}\nAccess: allowed"


@mcp.tool()
def wiki_status() -> str:
    """Return status and counts for Tier 2 and Tier 3 wiki data."""
    if not WIKI_DIR.exists():
        return f"Wiki directory not found: {WIKI_DIR}"

    counts = {2: 0, 3: 0}

    for p in get_allowed_files():
        tier = get_file_tier(p)

        if tier in counts:
            counts[tier] += 1

    return (
        "Mode: Tier 2 + Tier 3\n"
        "Tier 1 access: denied\n"
        f"Tier 2 files: {counts[2]}\n"
        f"Tier 3 files: {counts[3]}\n"
        f"Total accessible files: {counts[2] + counts[3]}\n"
        f"Wiki directory: {WIKI_DIR}"
    )


@mcp.tool()
def list_wiki_files(limit: int = 50) -> list[str]:
    """List accessible Tier 2 and Tier 3 Markdown files."""
    limit = max(1, min(int(limit), 200))

    return [
        p.relative_to(WIKI_DIR).as_posix()
        for p in get_allowed_files()[:limit]
    ]


@mcp.tool()
def read_wiki_file(path: str) -> str:
    """Read a Tier 2 or Tier 3 wiki file."""
    requested = safe_tier2_path(path)

    if requested is None:
        return "Access denied: Tier 1 files are not accessible."

    if not requested.is_file():
        return "File not found."

    try:
        return requested.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return requested.read_text(encoding="utf-8-sig")


@mcp.tool()
def search_wiki(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """Search accessible Tier 2 and Tier 3 wiki content."""
    query = query.strip()

    if not query:
        return []

    limit = max(1, min(int(limit), 50))

    results = []

    for p in get_allowed_files():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="utf-8-sig")
        except Exception:
            continue

        if query.lower() in text.lower():
            tier = get_file_tier(p)

            results.append(
                {
                    "path": p.relative_to(WIKI_DIR).as_posix(),
                    "tier": tier,
                    "excerpt": excerpt(text, query),
                }
            )

            if len(results) >= limit:
                break

    return results


@mcp.tool()
def get_context(
    query: str,
    limit: int = 5,
) -> str:
    """Return concise context from accessible Tier 2 and Tier 3 files."""
    results = search_wiki(query, limit=limit)

    if not results:
        return "No matching Tier 2 or Tier 3 wiki content found."

    chunks = []

    for result in results:
        chunks.append(
            f"[Tier {result['tier']}] {result['path']}\n"
            f"{result['excerpt']}"
        )

    return "\n\n---\n\n".join(chunks)


@mcp.tool()
def chat_history_status() -> str:
    """Return chat history integration status."""
    if list_conversations is None:
        return "Chat database integration unavailable."

    try:
        conversations = list_conversations()
        return f"Chat database available. Conversations: {len(conversations)}"
    except Exception as e:
        return f"Chat database error: {e}"


@mcp.tool()
def list_chat_history(limit: int = 20) -> list[str]:
    """List recent chat conversations."""
    if list_conversations is None:
        return ["Chat database integration unavailable."]

    limit = max(1, min(int(limit), 100))

    try:
        conversations = list_conversations(limit=limit)

        return [
            str(c)
            for c in conversations
        ]

    except Exception as e:
        return [f"Chat database error: {e}"]


@mcp.tool()
def read_chat_history(conversation_id: int) -> str:
    """Read messages from a stored conversation."""
    if get_conversation_messages is None:
        return "Chat database integration unavailable."

    try:
        messages = get_conversation_messages(int(conversation_id))

        return "\n\n".join(
            f"{m.get('role', 'unknown')}: {m.get('content', '')}"
            if isinstance(m, dict)
            else str(m)
            for m in messages
        )

    except Exception as e:
        return f"Chat database error: {e}"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    mcp.run(
        transport="streamable-http",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        port=port,
    )
