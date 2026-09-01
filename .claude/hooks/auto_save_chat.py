import json
import os
import sys
import urllib.request

REMOTE_URL = "https://wiki-mcp-ss2m.onrender.com/chat-save"
TOKEN = os.getenv("CHAT_SAVE_TOKEN")

def extract_user_message(transcript_path):
    if not transcript_path:
        return ""

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in reversed(lines):
            try:
                obj = json.loads(line)
            except Exception:
                continue

            if obj.get("type") != "user":
                continue

            message = obj.get("message", {})
            content = message.get("content", "") if isinstance(message, dict) else message

            if isinstance(content, str):
                if content.strip():
                    return content.strip()

            if isinstance(content, list):
                parts = []

                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(str(item.get("text", "")))

                result = "\n".join(x for x in parts if x.strip()).strip()

                if result:
                    return result

    except Exception:
        pass

    return ""


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    if payload.get("stop_hook_active"):
        return

    assistant_response = str(
        payload.get("last_assistant_message", "")
    ).strip()

    if not assistant_response:
        return

    user_message = extract_user_message(
        payload.get("transcript_path", "")
    )

    if not user_message:
        return

    session_id = str(payload.get("session_id", "")).strip()

    if not TOKEN:
        return

    body = json.dumps(
        {
            "user_message": user_message,
            "assistant_response": assistant_response,
            "session_id": session_id,
            "title": "Claude Code Chat",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        REMOTE_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Chat-Save-Token": TOKEN,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read()
    except Exception:
        pass


if __name__ == "__main__":
    main()
