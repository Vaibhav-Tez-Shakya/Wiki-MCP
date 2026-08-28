FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY wiki-data ./wiki-data
COPY chat-history ./chat-history
COPY chat_db.py ./chat_db.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/server_tier3.py"]