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

print("CHAT DB CHECK:", flush=True)
try:
    import psycopg
    print("DATABASE_URL SET:", bool(os.getenv("DATABASE_URL")), flush=True)
    psycopg.connect(os.getenv("DATABASE_URL")).close()
    print("POSTGRES CONNECTION: OK", flush=True)
except Exception as exc:
    print(f"POSTGRES CONNECTION FAILED: {exc}", flush=True)
BASE_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = BASE_DIR / "wiki-data"
CHAT_DIR = BASE_DIR / "chat-history"

mcp = MCPServer(
    name="Unified Wiki MCP",
    version="2.0.0",
    description=(
        "Single MCP server for the persistent game wiki. The wiki is organized "
        "into Tier 1 (complete/full-access dataset), Tier 2 (intermediate/detail), "
        "and Tier 3 (deep/restricted detail). This server has access to all tiers. "
        "Use max_tier to control retrieval depth: 1=Tier 1 only, 2=Tier 1+2, "
        "3=Tier 1+2+3. Tier labels are organizational retrieval controls, not a "
        "claim that Claude itself is a security boundary."
    ),
)

VALID_TIERS = {1, 2, 3}
TIER_NAMES = {1: "tier1", 2: "tier2", 3: "tier3"}


def normalize_max_tier(max_tier: int) -> int:
    return max(1, min(int(max_tier), 3))


def get_file_tier(path: Path) -> Optional[int]:
    try:
        relative = path.relative_to(WIKI_DIR).as_posix()
    except ValueError:
        return None
    first = relative.split("/", 1)[0].lower()
    if first in TIER_NAMES.values():
        return int(first[-1])
    return None


def get_allowed_files(max_tier: int = 3) -> list[Path]:
    max_tier = normalize_max_tier(max_tier)
    if not WIKI_DIR.exists():
        return []
    return sorted(
        p for p in WIKI_DIR.rglob("*.md")
        if (get_file_tier(p) or 99) <= max_tier
    )


def safe_path(relative_path: str) -> Optional[Path]:
    requested = (WIKI_DIR / relative_path).resolve()
    try:
        requested.relative_to(WIKI_DIR.resolve())
    except ValueError:
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
    """Check whether the unified Wiki MCP server is running."""
    return "pong"


@mcp.tool()
def list_accessible_tiers() -> list[str]:
    """Return all tiers available through this single unified MCP server."""
    return ["tier1", "tier2", "tier3"]


@mcp.tool()
def get_file_tier_info(path: str) -> str:
    """Return a wiki file's tier. This unified server can read all three tiers."""
    requested = safe_path(path)
    if requested is None:
        return "Access denied: invalid path."
    if not requested.exists() or not requested.is_file():
        return "File not found."
    tier = get_file_tier(requested)
    if tier is None:
        return "File has no recognized tier."
    return f"File: {path}\nTier: tier{tier}\nAccess: allowed"


@mcp.tool()
def wiki_status() -> str:
    """Return status and counts for the unified Tier 1/2/3 wiki."""
    if not WIKI_DIR.exists():
        return f"Wiki directory not found: {WIKI_DIR}"
    counts = {1: 0, 2: 0, 3: 0}
    for p in get_allowed_files(3):
        tier = get_file_tier(p)
        if tier in counts:
            counts[tier] += 1
    return (
        f"Wiki directory: {WIKI_DIR}\n"
        f"Mode: unified MCP (all tiers)\n"
        f"Tier 1 files: {counts[1]}\n"
        f"Tier 2 files: {counts[2]}\n"
        f"Tier 3 files: {counts[3]}\n"
        f"Total accessible files: {sum(counts.values())}"
    )


@mcp.tool()
def list_wiki_files(max_tier: int = 3, limit: int = 50) -> list[str]:
    """List wiki Markdown files up to max_tier. max_tier 1, 2, or 3."""
    limit = max(1, min(int(limit), 200))
    return [p.relative_to(WIKI_DIR).as_posix() for p in get_allowed_files(max_tier)[:limit]]


@mcp.tool()
def read_wiki_file(path: str) -> str:
    """Read a wiki Markdown file from any Tier 1/2/3 directory."""
    requested = safe_path(path)
    if requested is None:
        return "Access denied: invalid path."
    if not requested.exists() or not requested.is_file():
        return "File not found."
    if requested.suffix.lower() != ".md":
        return "Access denied: only Markdown files are supported."
    if get_file_tier(requested) is None:
        return "Access denied: file has no assigned tier."
    try:
        return requested.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Unable to decode file as UTF-8."


@mcp.tool()
def search_wiki(query: str, max_tier: int = 3, limit: int = 10) -> list[dict]:
    """Search wiki content by keyword. max_tier controls retrieval depth: 1=Tier 1, 2=Tier 1+2, 3=all tiers."""
    query = query.strip()
    if not query:
        return []
    limit = max(1, min(int(limit), 30))
    terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
    results = []
    for p in get_allowed_files(max_tier):
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lower = text.lower()
        score = sum(lower.count(t) for t in terms)
        if score:
            results.append({
                "path": p.relative_to(WIKI_DIR).as_posix(),
                "tier": get_file_tier(p),
                "score": score,
                "excerpt": excerpt(text, query),
            })
    results.sort(key=lambda x: (-x["score"], x["path"]))
    return results[:limit]


@mcp.tool()
def get_context(query: str, max_tier: int = 3, limit: int = 5) -> str:
    """Build a compact context from the best wiki search results for a question."""
    results = search_wiki(query, max_tier=max_tier, limit=limit)
    if not results:
        return "No matching wiki context found."
    chunks = []
    for r in results:
        chunks.append(f"[{r['path']} | Tier {r['tier']}]\n{r['excerpt']}")
    return "\n\n---\n\n".join(chunks)


@mcp.tool()
def chat_history_status() -> str:
    """Return the status of file-based and PostgreSQL chat history."""
    files = sorted(CHAT_DIR.glob("*.md")) if CHAT_DIR.exists() else []
    db_status = "PostgreSQL chat DB unavailable"
    db_count = None
    if list_conversations:
        try:
            rows = list_conversations()
            db_count = len(rows)
            db_status = f"PostgreSQL conversations: {db_count}"
        except Exception as exc:
            db_status = f"PostgreSQL check failed: {exc}"
    return f"Chat-history files: {len(files)}\n{db_status}\nDirectory: {CHAT_DIR}"


@mcp.tool()
def list_chat_history(limit: int = 20) -> list[str]:
    """List saved Markdown chat-history files from the project chat-history directory."""
    limit = max(1, min(int(limit), 100))
    if not CHAT_DIR.exists():
        return []
    return [p.name for p in sorted(CHAT_DIR.glob("*.md"), reverse=True)[:limit]]


@mcp.tool()
def read_chat_history(filename: str) -> str:
    """Read one saved Markdown chat-history file."""
    requested = (CHAT_DIR / filename).resolve()
    try:
        requested.relative_to(CHAT_DIR.resolve())
    except ValueError:
        return "Access denied: invalid chat-history path."
    if requested.suffix.lower() != ".md" or not requested.exists():
        return "Chat-history file not found."
    return requested.read_text(encoding="utf-8")


@mcp.tool()
def save_chat(
    user_message: str,
    assistant_response: str,
    conversation_id: Optional[int] = None,
    title: Optional[str] = None,
) -> str:
    """
    Persist a Claude chat turn.

    One conversation_id maps to one Markdown transcript.
    New conversation -> new file.
    Existing conversation -> append to the same file.
    PostgreSQL uses the same conversation_id.
    """
    CHAT_DIR.mkdir(parents=True, exist_ok=True)

    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)

    # Create a conversation only when this is a genuinely new thread.
    if conversation_id is None:
        if not create_conversation:
            return "Save failed: PostgreSQL chat database is unavailable."

        try:
            conversation_id = create_conversation(
                title or "Claude Wiki Chat"
            )
        except Exception as exc:
            return f"Save failed: could not create conversation: {exc}"

    conversation_id = int(conversation_id)

    # One thread = one Markdown file.
    filename = f"thread_{conversation_id}.md"
    filepath = CHAT_DIR / filename

    # Create the file only for the first turn.
    if not filepath.exists():
        content = (
            "# Claude Wiki Chat\n\n"
            f"**Conversation ID:** {conversation_id}\n\n"
            f"**Created:** {now.isoformat()}\n\n"
            "---\n\n"
            "## User\n\n"
            f"{user_message.strip()}\n\n"
            "## Assistant\n\n"
            f"{assistant_response.strip()}\n\n"
        )
        filepath.write_text(content, encoding="utf-8")
    else:
        # Existing thread: append the next turn.
        with filepath.open("a", encoding="utf-8") as f:
            f.write(
                "\n---\n\n"
                "## User\n\n"
                f"{user_message.strip()}\n\n"
                "## Assistant\n\n"
                f"{assistant_response.strip()}\n\n"
            )

    # Save the same turn to PostgreSQL.
    db_result = "PostgreSQL not configured"

    if save_message:
        try:
            save_message(
                conversation_id,
                "user",
                user_message,
            )

            save_message(
                conversation_id,
                "assistant",
                assistant_response,
            )

            db_result = (
                f"PostgreSQL conversation_id={conversation_id}"
            )

        except Exception as exc:
            db_result = f"PostgreSQL save failed: {exc}"

    return (
        f"Saved: chat-history/{filename}\n"
        f"Conversation ID: {conversation_id}\n"
        f"{db_result}"
    )

@mcp.tool()
def read_database_chat_history(conversation_id: int) -> str:
    """Read a PostgreSQL conversation by ID, when PostgreSQL chat persistence is configured."""
    if not get_conversation_messages:
        return "PostgreSQL chat database is unavailable."
    try:
        rows = get_conversation_messages(int(conversation_id))
    except Exception as exc:
        return f"Database error: {exc}"
    if not rows:
        return "No messages found."
    return "\n\n".join(f"{role.upper()}: {content}\n[{created_at}]" for role, content, created_at in rows)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        port=port,
    )







