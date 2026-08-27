from pathlib import Path
import os

from mcp.server.mcpserver import MCPServer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
WIKI_DIR = BASE_DIR / "wiki-data"


# ============================================================
# SERVER CONFIGURATION
# ============================================================

SERVER_TIER = os.getenv("MCP_TIER", "all").lower()

VALID_TIERS = {"tier1", "tier2", "tier3", "all"}

if SERVER_TIER not in VALID_TIERS:
    raise ValueError(
        f"Invalid MCP_TIER={SERVER_TIER}. "
        f"Expected one of: {sorted(VALID_TIERS)}"
    )


mcp = MCPServer(
    name=f"Wiki MCP ({SERVER_TIER})",
    version="1.0.0",
    description=(
        "Tier-aware MCP server for the personal wiki."
    ),
)


# ============================================================
# TIER CONFIGURATION
# ============================================================

# IMPORTANT:
# These are examples for now.
#
# We will replace these with your actual wiki classification
# after inspecting the 420 Markdown files.

TIER_PATHS = {
    "tier1": ["tier1"],
    "tier2": ["tier2"],
    "tier3": ["tier3"],
}


# ============================================================
# ACCESS CONTROL
# ============================================================

def get_allowed_tiers() -> set[str]:
    """
    Return the tiers this MCP server is allowed to access.
    """

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
    """
    Determine the tier of a wiki file based on its path.
    """

    relative = path.relative_to(WIKI_DIR).as_posix()

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
    """
    Server-side access control.

    A file is accessible only if its tier is explicitly
    permitted by this MCP instance.
    """

    tier = get_file_tier(path)

    if tier is None:
        return False

    return tier in get_allowed_tiers()


def get_allowed_files() -> list[Path]:
    """
    Return only files that this MCP instance is permitted
    to expose.
    """

    if not WIKI_DIR.exists():
        return []

    files = []

    for path in WIKI_DIR.rglob("*.md"):
        if is_file_allowed(path):
            files.append(path)

    return sorted(files)


# ============================================================
# TOOLS
# ============================================================

@mcp.tool()
def ping() -> str:
    """Check whether the Wiki MCP server is running."""

    return "pong"


@mcp.tool()
def wiki_status() -> str:
    """Return tier-aware information about the wiki."""

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

    allowed = ", ".join(sorted(get_allowed_tiers()))

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

    limit = max(1, min(limit, 100))

    files = [
        path.relative_to(WIKI_DIR).as_posix()
        for path in get_allowed_files()
    ]

    return files[:limit]


@mcp.tool()
def get_file_tier_info(path: str) -> str:
    """
    Return the tier assigned to a wiki file and whether this
    MCP server is allowed to access it.
    """

    requested = (WIKI_DIR / path).resolve()

    try:
        requested.relative_to(WIKI_DIR.resolve())
    except ValueError:
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

    requested = (WIKI_DIR / path).resolve()

    try:
        requested.relative_to(WIKI_DIR.resolve())
    except ValueError:
        return "Access denied: invalid path."

    if not requested.exists():
        return "File not found."

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
        return requested.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Unable to decode file as UTF-8."


# ============================================================
# SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    mcp.run(
        transport="streamable-http",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        port=port,
    )