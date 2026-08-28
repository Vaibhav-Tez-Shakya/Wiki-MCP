# Unified Wiki MCP

## Unified MCP architecture

The project now uses one deployed MCP server instead of separate MCP services for each tier. The single server exposes Tier 1, Tier 2, and Tier 3 data and provides a `max_tier` retrieval control. Tier 1 is the index/general layer, Tier 2 is intermediate detail, and Tier 3 contains deep detail.

Claude connects to one `/mcp` endpoint. The server-side tools `search_wiki`, `get_context`, `list_wiki_files`, and `read_wiki_file` understand the tier layout.

## Chat history

The migrated chat-history Markdown files are stored in `chat-history/`. The `save_chat` tool writes each turn to this directory and also attempts to persist the turn to PostgreSQL when `DATABASE_URL` is configured.

## Added games

- Red Dead Redemption 2 — mission index
- Assassin's Creed IV: Black Flag Resynced — main mission index and major side-mission groups

