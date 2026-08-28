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
    )
except Exception:
    create_conversation = save_message = get_conversation_messages = None
    list_conversations = None


BASE_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = BASE_DIR / "wiki-data"
CHAT_DIR = BASE_DIR / "chat-history"

mcp = MCPServer(
    name="Wiki MCP Tier 3",
    version="1.0.0",
    description=(
        "Tier 3-only MCP server for the persistent game wiki. "
        "This server is restricted to deep Tier 3 wiki data. "
        "Tier 1 and Tier 2 data are not accessible."
    ),
)


TIER3_NAME = "tier3"


def get_file_tier(path: Path) -> Optional[int]:
    try:
        relative = path.relative_to(WIKI_DIR).as_posix()
    except ValueError:
        return None

    first = relative.split("/", 1)[0].lower()

    if first == TIER3_NAME:
        return 3

    return None


def get_allowed_files() -> list[Path]:
    if not WIKI_DIR.exists():
        return []

    tier3_dir = WIKI_DIR / TIER3_NAME

    if not tier3_dir.exists():
        return []

    return sorted(tier3_dir.rglob("*.md"))


def safe_tier3_path(relative_path: str) -> Optional[Path]:
    requested = (WIKI_DIR / relative_path).resolve()

    try:
        requested.relative_to(WIKI_DIR.resolve())
    except ValueError:
        return None

    tier = get_file_tier(requested)

    if tier != 3:
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
    """Check whether the Tier 3 MCP server is running."""
    return "pong"


@mcp.tool()
def list_accessible_tiers() -> list[str]:
    """Return the only tier accessible through this MCP server."""
    return ["tier3"]


@mcp.tool()
def get_file_tier_info(path: str) -> str:
    """Return tier information only for Tier 3 files."""
    requested = safe_tier3_path(path)

    if requested is None:
        return "Access denied: Tier 3 only."

    if not requested.exists() or not requested.is_file():
        return "File not found."

    return f"File: {path}\nTier: tier3\nAccess: allowed"


@mcp.tool()
def wiki_status() -> str:
    """Return status and count for Tier 3 wiki data."""
    if not WIKI_DIR.exists():
        return f"Wiki directory not found: {WIKI_DIR}"

    files = get_allowed_files()

    return (
        f"Wiki directory: {WIKI_DIR}\n"
        f"Mode: Tier 3 only\n"
        f"Tier 1 access: denied\n"
        f"Tier 2 access: denied\n"
        f"Tier 3 files: {len(files)}\n"
        f"Total accessible files: {len(files)}"
    )


@mcp.tool()
def list_wiki_files(limit: int = 50) -> list[str]:
    """List Tier 3 Markdown files only."""
    limit = max(1, min(int(limit), 200))

    return [
        p.relative_to(WIKI_DIR).as_posix()
        for p in get_allowed_files()[:limit]
    ]


@mcp.tool()
def read_wiki_file(path: str) -> str:
    """Read a Markdown file only from Tier 3."""
    requested = safe_tier3_path(path)

    if requested is None:
        return "Access denied: Tier 3 only."

    if not requested.exists() or not requested.is_file():
        return "File not found."

    if requested.suffix.lower() != ".md":
        return "Access denied: only Markdown files are supported."

    try:
        return requested.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Unable to decode file as UTF-8."


@mcp.tool()
def search_wiki(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """Search Tier 3 wiki content only."""
    query = query.strip()

    if not query:
        return []

    limit = max(1, min(int(limit), 30))

    terms = [
        t.lower()
        for t in re.findall(r"\w+", query)
        if len(t) > 1
    ]

    results = []

    for p in get_allowed_files():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        lower = text.lower()

        score = sum(
            lower.count(term)
            for term in terms
        )

        if score:
            results.append(
                {
                    "path": p.relative_to(WIKI_DIR).as_posix(),
                    "tier": 3,
                    "score": score,
                    "excerpt": excerpt(text, query),
                }
            )

    results.sort(
        key=lambda x: (-x["score"], x["path"])
    )

    return results[:limit]


@mcp.tool()
def get_context(
    query: str,
    limit: int = 5,
) -> str:
    """Build context exclusively from Tier 3 wiki data."""
    results = search_wiki(
        query,
        limit=limit,
    )

    if not results:
        return "No matching Tier 3 wiki context found."

    chunks = []

    for result in results:
        chunks.append(
            f"[{result['path']} | Tier 3]\n"
            f"{result['excerpt']}"
        )

    return "\n\n---\n\n".join(chunks)


@mcp.tool()
def chat_history_status() -> str:
    """Return chat-history status."""
    files = (
        sorted(CHAT_DIR.glob("*.md"))
        if CHAT_DIR.exists()
        else []
    )

    db_status = "PostgreSQL chat DB unavailable"

    if list_conversations:
        try:
            rows = list_conversations()

            db_status = (
                f"PostgreSQL conversations: {len(rows)}"
            )

        except Exception as exc:
            db_status = (
                f"PostgreSQL check failed: {exc}"
            )

    return (
        f"Chat-history files: {len(files)}\n"
        f"{db_status}\n"
        f"Directory: {CHAT_DIR}"
    )


@mcp.tool()
def list_chat_history(limit: int = 20) -> list[str]:
    """List saved Markdown chat-history files."""
    limit = max(1, min(int(limit), 100))

    if not CHAT_DIR.exists():
        return []

    return [
        p.name
        for p in sorted(
            CHAT_DIR.glob("*.md"),
            reverse=True,
        )[:limit]
    ]


@mcp.tool()
def read_chat_history(filename: str) -> str:
    """Read one saved Markdown chat-history file."""
    requested = (
        CHAT_DIR / filename
    ).resolve()

    try:
        requested.relative_to(
            CHAT_DIR.resolve()
        )
    except ValueError:
        return "Access denied: invalid chat-history path."

    if (
        requested.suffix.lower() != ".md"
        or not requested.exists()
    ):
        return "Chat-history file not found."

    return requested.read_text(
        encoding="utf-8"
    )


@mcp.tool()
def read_database_chat_history(
    conversation_id: int,
) -> str:
    """Read a PostgreSQL conversation by ID."""
    if not get_conversation_messages:
        return (
            "PostgreSQL chat database is unavailable."
        )

    try:
        rows = get_conversation_messages(
            int(conversation_id)
        )

    except Exception as exc:
        return f"Database error: {exc}"

    if not rows:
        return "No messages found."

    return "\n\n".join(
        f"{role.upper()}: {content}\n[{created_at}]"
        for role, content, created_at in rows
    )


if __name__ == "__main__":
    port = int(
        os.getenv("PORT", "8000")
    )

    mcp.run(
        transport="streamable-http",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        port=port,
    )