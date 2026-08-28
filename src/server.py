from pathlib import Path
import os
from datetime import datetime

from mcp.server.mcpserver import MCPServer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

WIKI_DIR = BASE_DIR / "wiki-data"
CHAT_HISTORY_DIR = BASE_DIR / "chat-history"


# ============================================================
# SERVER CONFIGURATION
# ============================================================

SERVER_TIER = os.getenv("MCP_TIER", "all").lower()

VALID_TIERS = {
    "tier1",
    "tier2",
    "tier3",
    "all",
}

if SERVER_TIER not in VALID_TIERS:
    raise ValueError(
        f"Invalid MCP_TIER={SERVER_TIER}. "
        f"Expected one of: {sorted(VALID_TIERS)}"
    )


mcp = MCPServer(
    name=f"Wiki MCP ({SERVER_TIER})",
    version="1.0.0",
    description="Tier-aware MCP server for the personal wiki with persistent chat history.",
)


# ============================================================
# TIER CONFIGURATION
# ============================================================

TIER_PATHS = {
    "tier1": ["tier1"],
    "tier2": ["tier2"],
    "tier3": ["tier3"],
}


# ============================================================
# ACCESS CONTROL
# ============================================================

def get_allowed_tiers() -> set[str]:
    if SERVER_TIER == "all":
        return {"tier1", "tier2", "tier3"}

    if SERVER_TIER == "tier1":
        return {"tier1", "tier2", "tier3"}

    if SERVER_TIER == "tier2":
        return {"tier2", "tier3"}

    if SERVER_TIER == "tier3":
        return {"tier3"}

    return set()


def get_file_tier(path: Path) -> str | None:
    try:
        relative = path.relative_to(WIKI_DIR).as_posix()
    except ValueError:
        return None

    for tier, prefixes in TIER_PATHS.items():
        for prefix in prefixes:
            prefix = prefix.strip("/")

            if (
                relative == prefix
                or relative.startswith(prefix + "/")
            ):
                return tier

    return None


def is_file_allowed(path: Path) -> bool:
    tier = get_file_tier(path)

    if tier is None:
        return False

    return tier in get_allowed_tiers()


# ============================================================
# FILE DISCOVERY
# ============================================================

def get_allowed_files() -> list[Path]:
    if not WIKI_DIR.exists():
        return []

    files = []

    for path in WIKI_DIR.rglob("*.md"):
        if is_file_allowed(path):
            files.append(path)

    return sorted(files)


# ============================================================
# SAFE PATH RESOLUTION
# ============================================================

def resolve_wiki_path(path: str) -> Path | None:
    try:
        requested = (WIKI_DIR / path).resolve()
        requested.relative_to(WIKI_DIR.resolve())
        return requested

    except ValueError:
        return None


# ============================================================
# CHAT HISTORY
# ============================================================

def ensure_chat_history_dir():
    CHAT_HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def create_chat_filename() -> Path:
    ensure_chat_history_dir()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    return CHAT_HISTORY_DIR / f"chat_{timestamp}.md"


# ============================================================
# MCP TOOLS
# ============================================================

@mcp.tool()
def ping() -> str:
    """
    Check whether the Wiki MCP server is running.
    """

    return "pong"


@mcp.tool()
def wiki_status() -> str:
    """
    Return tier-aware information about the wiki.
    """

    if not WIKI_DIR.exists():
        return f"Wiki directory not found: {WIKI_DIR}"

    allowed_files = get_allowed_files()

    tier_counts = {
        "tier1": 0,
        "tier2": 0,
        "tier3": 0,
    }

    for path in allowed_files:
        tier = get_file_tier(path)

        if tier in tier_counts:
            tier_counts[tier] += 1

    allowed = ", ".join(
        sorted(get_allowed_tiers())
    )

    return (
        f"Wiki directory: {WIKI_DIR}\n"
        f"MCP tier: {SERVER_TIER}\n"
        f"Allowed tiers: {allowed}\n"
        f"Accessible Markdown files: {len(allowed_files)}\n"
        f"Tier 1 files: {tier_counts['tier1']}\n"
        f"Tier 2 files: {tier_counts['tier2']}\n"
        f"Tier 3 files: {tier_counts['tier3']}"
    )


@mcp.tool()
def list_wiki_files(limit: int = 20) -> list[str]:
    """
    List Markdown files accessible to this MCP server.
    """

    limit = max(
        1,
        min(limit, 100),
    )

    files = [
        path.relative_to(WIKI_DIR).as_posix()
        for path in get_allowed_files()
    ]

    return files[:limit]


@mcp.tool()
def get_file_tier_info(path: str) -> str:
    """
    Return the tier assigned to a wiki file and whether
    this MCP server is allowed to access it.
    """

    requested = resolve_wiki_path(path)

    if requested is None:
        return "Access denied: invalid path."

    if not requested.exists():
        return "File not found."

    if requested.suffix.lower() != ".md":
        return "Access denied: only Markdown files are supported."

    tier = get_file_tier(requested)

    if tier is None:
        return "Access denied: file has no assigned tier."

    if not is_file_allowed(requested):
        return (
            f"Access denied: {path} belongs to {tier}, "
            f"which this MCP server cannot access."
        )

    return (
        f"File: {path}\n"
        f"Tier: {tier}\n"
        f"Access: allowed"
    )


@mcp.tool()
def read_wiki_file(path: str) -> str:
    """
    Read a Markdown file only when its tier is permitted
    by this MCP server.
    """

    requested = resolve_wiki_path(path)

    if requested is None:
        return "Access denied: invalid path."

    if not requested.exists():
        return "File not found."

    if not requested.is_file():
        return "Path is not a file."

    if requested.suffix.lower() != ".md":
        return "Access denied: only Markdown files are supported."

    if not is_file_allowed(requested):

        tier = get_file_tier(requested)

        if tier is None:
            return "Access denied: file has no assigned tier."

        return (
            f"Access denied: this MCP server cannot access "
            f"{tier} data."
        )

    try:
        return requested.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return "Unable to decode file as UTF-8."

    except OSError as error:
        return f"Unable to read file: {error}"


@mcp.tool()
def search_wiki(
    query: str,
    limit: int = 10,
) -> list[dict]:
    """
    Search accessible Markdown files by filename
    and content.

    Only files permitted by the current MCP tier
    are searched.
    """

    query = query.strip().lower()

    if not query:
        return []

    limit = max(
        1,
        min(limit, 50),
    )

    results = []

    for path in get_allowed_files():

        try:
            content = path.read_text(
                encoding="utf-8"
            )

        except (
            UnicodeDecodeError,
            OSError,
        ):
            continue

        relative_path = (
            path.relative_to(WIKI_DIR)
            .as_posix()
        )

        filename_match = (
            query in path.stem.lower()
        )

        content_lower = content.lower()

        content_match = (
            query in content_lower
        )

        if not filename_match and not content_match:
            continue

        tier = get_file_tier(path)

        snippet = ""

        if content_match:

            index = content_lower.find(query)

            start = max(
                0,
                index - 150,
            )

            end = min(
                len(content),
                index + len(query) + 300,
            )

            snippet = (
                content[start:end]
                .replace("\n", " ")
                .strip()
            )

        results.append(
            {
                "path": relative_path,
                "tier": tier,
                "filename_match": filename_match,
                "snippet": snippet,
            }
        )

        if len(results) >= limit:
            break

    return results


@mcp.tool()
def list_accessible_tiers() -> list[str]:
    """
    Return the tiers accessible through this MCP server.
    """

    return sorted(
        get_allowed_tiers()
    )


@mcp.tool()
def count_wiki_files() -> dict:
    """
    Return the number of accessible Markdown files
    grouped by tier.
    """

    counts = {
        "tier1": 0,
        "tier2": 0,
        "tier3": 0,
        "total": 0,
    }

    for path in get_allowed_files():

        tier = get_file_tier(path)

        if tier in {
            "tier1",
            "tier2",
            "tier3",
        }:

            counts[tier] += 1
            counts["total"] += 1

    return counts


# ============================================================
# CHAT HISTORY TOOLS
# ============================================================

@mcp.tool()
def save_chat(
    user_message: str,
    assistant_response: str,
) -> str:
    """
    Save a Claude conversation turn to the local
    chat-history directory.

    The user message and Claude's response are stored
    together in a Markdown file.
    """

    user_message = user_message.strip()
    assistant_response = assistant_response.strip()

    if not user_message:
        return "Error: user_message cannot be empty."

    if not assistant_response:
        return "Error: assistant_response cannot be empty."

    chat_file = create_chat_filename()

    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    content = f"""# Wiki Chat

**Date:** {timestamp}

## User

{user_message}

## Claude

{assistant_response}
"""

    try:
        chat_file.write_text(
            content,
            encoding="utf-8",
        )

        return (
            f"Chat saved successfully.\n"
            f"File: {chat_file.relative_to(BASE_DIR).as_posix()}"
        )

    except OSError as error:
        return f"Unable to save chat: {error}"


@mcp.tool()
def list_chat_history(limit: int = 20) -> list[str]:
    """
    List saved chat history files.
    """

    ensure_chat_history_dir()

    limit = max(
        1,
        min(limit, 100),
    )

    files = sorted(
        CHAT_HISTORY_DIR.glob("chat_*.md"),
        reverse=True,
    )

    return [
        path.relative_to(BASE_DIR).as_posix()
        for path in files[:limit]
    ]


@mcp.tool()
def read_chat_history(filename: str) -> str:
    """
    Read a previously saved chat history file.
    """

    try:
        requested = (
            CHAT_HISTORY_DIR / filename
        ).resolve()

        requested.relative_to(
            CHAT_HISTORY_DIR.resolve()
        )

    except ValueError:
        return "Access denied: invalid chat history path."

    if not requested.exists():
        return "Chat history file not found."

    if not requested.is_file():
        return "Path is not a file."

    if requested.suffix.lower() != ".md":
        return "Only Markdown chat history files are supported."

    try:
        return requested.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return "Unable to decode chat history as UTF-8."

    except OSError as error:
        return f"Unable to read chat history: {error}"


@mcp.tool()
def chat_history_status() -> str:
    """
    Return information about the local chat history.
    """

    ensure_chat_history_dir()

    files = list(
        CHAT_HISTORY_DIR.glob("chat_*.md")
    )

    return (
        f"Chat history directory: {CHAT_HISTORY_DIR}\n"
        f"Saved conversations: {len(files)}"
    )


# ============================================================
# SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )

    mcp.run(
        transport="streamable-http",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        port=port,
    )