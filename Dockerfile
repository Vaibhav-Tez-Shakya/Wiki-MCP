FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY wiki-data ./wiki-data

RUN echo "=== BUILD DATASET DEBUG ===" && \
    echo "Tier1:" && find /app/wiki-data/tier1 -type f -name "*.md" | wc -l && \
    echo "Tier2:" && find /app/wiki-data/tier2 -type f -name "*.md" | wc -l && \
    echo "Tier3:" && find /app/wiki-data/tier3 -type f -name "*.md" | wc -l && \
    echo "TOTAL:" && find /app/wiki-data -type f -name "*.md" | wc -l
COPY chat-history ./chat-history
COPY chat_db.py ./chat_db.py

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "case \"$MCP_TIER\" in all) exec python src/server.py ;; tier2) exec python src/server_tier2.py ;; tier3) exec python src/server_tier3.py ;; *) echo \"ERROR: MCP_TIER must be all, tier2, or tier3\"; exit 1 ;; esac"]



