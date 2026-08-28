from chat_db import (
    create_conversation,
    save_message,
    get_conversation_messages,
)


conversation_id = create_conversation(
    "Claude Wiki Test"
)

print("Conversation ID:", conversation_id)


save_message(
    conversation_id,
    "user",
    "How many games are in my wiki?"
)


save_message(
    conversation_id,
    "assistant",
    "Your wiki contains 5 games."
)


messages = get_conversation_messages(conversation_id)


print("\nConversation:")

for role, content, created_at in messages:
    print(f"{role}: {content}")
    print(f"Time: {created_at}")