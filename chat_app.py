from chat_db import (
    create_conversation,
    save_message,
    get_conversation_messages,
    list_conversations,
)

from persistent_chat import ask_gemini


def show_conversations():
    conversations = list_conversations()

    if not conversations:
        print("\nNo conversations found.\n")
        return

    print("\n=== Conversations ===")

    for conversation in conversations:
        conversation_id, title, created_at, updated_at = conversation

        print(
            f"{conversation_id} | "
            f"{title or 'Untitled'} | "
            f"{updated_at}"
        )

    print()


def show_history(conversation_id):
    messages = get_conversation_messages(conversation_id)

    print("\n=== Conversation History ===\n")

    for role, content, created_at in messages:
        print(f"{role.upper()}:")
        print(content)
        print(f"[{created_at}]")
        print()


def start_conversation():
    title = input("Conversation title: ").strip()

    if not title:
        title = "New Wiki Chat"

    conversation_id = create_conversation(title)

    print()
    print("Created conversation:")
    print(conversation_id)
    print()

    return conversation_id


def chat(conversation_id):
    print("\nType 'exit' to leave the conversation.")
    print("Type 'history' to view this conversation.\n")

    while True:
        user_message = input("You: ").strip()

        if user_message.lower() == "exit":
            break

        if user_message.lower() == "history":
            show_history(conversation_id)
            continue

        if not user_message:
            continue

        try:
            response = ask_gemini(
                conversation_id,
                user_message,
            )

            print("\nAI:")
            print(response)
            print()

        except Exception as error:
            print("\nERROR:")
            print(error)
            print()


def main():
    while True:
        print(
            """
==============================
        WIKI AI CHAT
==============================

1. New conversation
2. Show conversations
3. Exit
"""
        )

        choice = input("Choose: ").strip()

        if choice == "1":
            conversation_id = start_conversation()
            chat(conversation_id)

        elif choice == "2":
            show_conversations()

        elif choice == "3":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()