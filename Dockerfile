FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY wiki-data ./wiki-data
COPY chat-history ./chat-history
COPY chat_db.py ./chat_db.py

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "case \"$MCP_TIER\" in all) exec python src/server.py ;; tier2) exec python src/server_tier2.py ;; tier3) exec python src/server_tier3.py ;; *) echo \"ERROR: MCP_TIER must be all, tier2, or tier3\"; exit 1 ;; esac"]



