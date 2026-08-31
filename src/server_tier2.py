from pathlib import Path
import os
import secrets
import time
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
    version="1.1.0",
    description=(
        "Tier 2 MCP server for the persistent game wiki. "
        "Tier 2 data is directly accessible. "
        "Tier 3 data is restricted and requires an explicit permission "
        "request followed by approval before retrieval. "
        "Tier 1 data is not accessible."
    ),
)


TIER2 = 2
TIER3 = 3

TIER_NAMES = {
    TIER2: "tier2",
    TIER3: "tier3",
}

# Direct retrieval/search is Tier 2 only.
ALLOWED_DIRECT_TIERS = {TIER2}

# Short-lived in-memory permission requests/tokens.
# This is intentionally process-local for the first implementation.
PENDING_TIER3_REQUESTS: dict[str, dict] = {}
APPROVED_TIER3_TOKENS: dict[str, dict] = {}

PERMISSION_TTL_SECONDS = 15 * 60


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


def get_tier_files(tier: int) -> list[Path]:
    if not WIKI_DIR.exists():
        return []

    tier_name = TIER_NAMES.get(tier)

    if not tier_name:
        return []

    tier_dir = WIKI_DIR / tier_name

    if not tier_dir.exists():
        return []

    return sorted(tier_dir.rglob("*.md"))


def get_allowed_files() -> list[Path]:
    return get_tier_files(TIER2)


def safe_path(relative_path: str) -> Optional[Path]:
    requested = (WIKI_DIR / relative_path).resolve()

    try:
        requested.relative_to(WIKI_DIR.resolve())
    except ValueError:
        return None

    return requested


def safe_tier2_path(relative_path: str) -> Optional[Path]:
    requested = safe_path(relative_path)

    if requested is None:
        return None

    if get_file_tier(requested) != TIER2:
        return None

    return requested


def safe_tier3_path(relative_path: str) -> Optional[Path]:
    requested = safe_path(relative_path)

    if requested is None:
        return None

    if get_file_tier(requested) != TIER3:
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


def cleanup_permission_state() -> None:
    now = time.time()

    expired_requests = [
        request_id
        for request_id, data in PENDING_TIER3_REQUESTS.items()
        if data["expires_at"] <= now
    ]

    for request_id in expired_requests:
        PENDING_TIER3_REQUESTS.pop(request_id, None)

    expired_tokens = [
        token
        for token, data in APPROVED_TIER3_TOKENS.items()
        if data["expires_at"] <= now
    ]

    for token in expired_tokens:
        APPROVED_TIER3_TOKENS.pop(token, None)


def find_tier3_matches(query: str, limit: int = 10) -> list[dict]:
    query = query.strip()

    if not query:
        return []

    limit = max(1, min(int(limit), 20))
    results = []

    for p in get_tier_files(TIER3):
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(encoding="utf-8-sig")
        except Exception:
            continue

        if query.lower() in text.lower():
            relative = p.relative_to(WIKI_DIR).as_posix()

            results.append(
                {
                    "path": relative,
                    "tier": TIER3,
                }
            )

            if len(results) >= limit:
                break

    return results


def validate_tier3_token(access_token: str, path: str) -> bool:
    cleanup_permission_state()

    if not access_token:
        return False

    approval = APPROVED_TIER3_TOKENS.get(access_token)

    if not approval:
        return False

    if approval["expires_at"] <= time.time():
        APPROVED_TIER3_TOKENS.pop(access_token, None)
        return False

    normalized_path = path.replace("\\", "/")

    return normalized_path in approval["paths"]


@mcp.tool()
def ping() -> str:
    """Check whether the Tier 2 MCP server is running."""
    return "pong"


@mcp.tool()
def list_accessible_tiers() -> list[str]:
    """Return directly accessible tiers. Tier 3 requires explicit approval."""
    return ["tier2", "tier3 (approval required)"]


@mcp.tool()
def get_file_tier_info(path: str) -> str:
    """Return tier information without exposing restricted Tier 3 content."""
    requested = safe_path(path)

    if requested is None:
        return "Access denied: invalid wiki path."

    tier = get_file_tier(requested)

    if tier == TIER2:
        return f"File: {path}\nTier: tier2\nAccess: allowed"

    if tier == TIER3:
        return (
            f"File: {path}\n"
            "Tier: tier3\n"
            "Access: permission required\n"
            "Use request_tier3_access before retrieval."
        )

    return "Access denied: file has no assigned tier."


@mcp.tool()
def wiki_status() -> str:
    """Return Tier 2 status and Tier 3 restricted-data count."""
    if not WIKI_DIR.exists():
        return f"Wiki directory not found: {WIKI_DIR}"

    tier2_count = len(get_tier_files(TIER2))
    tier3_count = len(get_tier_files(TIER3))

    return (
        "Mode: Tier 2 with controlled Tier 3 escalation\n"
        "Tier 1 access: denied\n"
        f"Tier 2 files: {tier2_count}\n"
        f"Tier 3 files: {tier3_count}\n"
        "Tier 3 direct retrieval: denied without approval\n"
        f"Wiki directory: {WIKI_DIR}"
    )


@mcp.tool()
def list_wiki_files(limit: int = 50) -> list[str]:
    """List directly accessible Tier 2 Markdown files."""
    limit = max(1, min(int(limit), 200))

    return [
        p.relative_to(WIKI_DIR).as_posix()
        for p in get_allowed_files()[:limit]
    ]


@mcp.tool()
def request_tier3_access(
    query: str,
    limit: int = 10,
) -> str:
    """
    Check whether the requested information appears to exist in Tier 3.

    This tool does not disclose Tier 3 content. It creates a short-lived
    permission request that must be explicitly approved before retrieval.
    """
    cleanup_permission_state()

    query = query.strip()

    if not query:
        return "Permission request denied: query is empty."

    matches = find_tier3_matches(query, limit=limit)

    if not matches:
        return (
            "No Tier 3 match found for the requested query. "
            "No permission request was created."
        )

    request_id = secrets.token_urlsafe(16)
    expires_at = time.time() + PERMISSION_TTL_SECONDS

    PENDING_TIER3_REQUESTS[request_id] = {
        "query": query,
        "paths": [item["path"] for item in matches],
        "expires_at": expires_at,
    }

    paths_text = "\n".join(
        f"- {item['path']}"
        for item in matches
    )

    return (
        "PERMISSION REQUIRED\n"
        f"Request ID: {request_id}\n"
        "Tier: tier3\n"
        f"Query: {query}\n"
        "Matching restricted files:\n"
        f"{paths_text}\n"
        "\n"
        "No Tier 3 content has been disclosed.\n"
        "Call approve_tier3_access with this Request ID only after "
        "explicit user approval."
    )


@mcp.tool()
def approve_tier3_access(request_id: str) -> str:
    """
    Explicitly approve a pending Tier 3 access request and issue
    a short-lived retrieval token.
    """
    cleanup_permission_state()

    request_id = request_id.strip()

    request = PENDING_TIER3_REQUESTS.get(request_id)

    if not request:
        return (
            "Approval denied: request ID is invalid, expired, "
            "or already removed."
        )

    access_token = secrets.token_urlsafe(24)
    expires_at = time.time() + PERMISSION_TTL_SECONDS

    APPROVED_TIER3_TOKENS[access_token] = {
        "paths": set(request["paths"]),
        "query": request["query"],
        "expires_at": expires_at,
    }

    PENDING_TIER3_REQUESTS.pop(request_id, None)

    return (
        "TIER 3 ACCESS APPROVED\n"
        f"Request ID: {request_id}\n"
        f"Access token: {access_token}\n"
        f"Expires in: {PERMISSION_TTL_SECONDS} seconds\n"
        "Use this token with read_wiki_file for the approved Tier 3 file(s)."
    )


@mcp.tool()
def read_wiki_file(
    path: str,
    access_token: str = "",
) -> str:
    """
    Read a Tier 2 file directly.

    Tier 3 files require a valid short-lived approval token issued by
    approve_tier3_access.
    """
    requested = safe_path(path)

    if requested is None:
        return "Access denied: invalid wiki path."

    tier = get_file_tier(requested)

    if tier == TIER2:
        pass

    elif tier == TIER3:
        if not validate_tier3_token(access_token, path):
            return (
                "Access denied: Tier 3 permission is required.\n"
                "Use request_tier3_access followed by explicit approval."
            )

    else:
        return "Access denied: file has no assigned tier."

    if not requested.is_file():
        return "File not found."

    try:
        return requested.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return requested.read_text(encoding="utf-8-sig")
    except Exception as exc:
        return f"Read error: {exc}"


@mcp.tool()
def search_wiki(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search Tier 2 only.

    Tier 3 is never silently searched or returned by this tool.
    """
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
            results.append(
                {
                    "path": p.relative_to(WIKI_DIR).as_posix(),
                    "tier": TIER2,
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
    """Return concise context from Tier 2 only."""
    results = search_wiki(query, limit=limit)

    if not results:
        return (
            "No matching Tier 2 wiki content found. "
            "Tier 3 content is restricted and is not searched automatically. "
            "Use request_tier3_access to request restricted access."
        )

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
