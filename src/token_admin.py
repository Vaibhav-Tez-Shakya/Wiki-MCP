import argparse

from token_store import (
    create_user_token,
    init_token_db,
    list_user_tokens,
    revoke_user_token,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wiki MCP user token administration"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new user token",
    )
    create_parser.add_argument(
        "--user",
        required=True,
        help="User identifier",
    )

    revoke_parser = subparsers.add_parser(
        "revoke",
        help="Revoke a token",
    )
    revoke_parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="Token database ID",
    )

    subparsers.add_parser(
        "list",
        help="List token metadata",
    )

    args = parser.parse_args()

    init_token_db()

    if args.command == "create":
        token = create_user_token(args.user)

        print()
        print("TOKEN CREATED")
        print("User:", args.user)
        print("Token:", token)
        print()
        print("IMPORTANT: save this token now.")
        print("The raw token is not stored in the database.")
        print()

    elif args.command == "revoke":
        success = revoke_user_token(args.id)

        if success:
            print(f"Token {args.id} revoked successfully.")
        else:
            print(
                f"Token {args.id} was not found "
                "or is already revoked."
            )

    elif args.command == "list":
        rows = list_user_tokens()

        if not rows:
            print("No tokens found.")
            return

        print()
        print(
            f"{'ID':<5}"
            f"{'USER':<25}"
            f"{'STATUS':<12}"
            f"{'CREATED':<30}"
            f"{'REVOKED'}"
        )
        print("-" * 100)

        for row in rows:
            token_id, user_id, status, created_at, revoked_at = row

            print(
                f"{token_id:<5}"
                f"{user_id:<25}"
                f"{status:<12}"
                f"{str(created_at):<30}"
                f"{str(revoked_at or '')}"
            )


if __name__ == "__main__":
    main()
