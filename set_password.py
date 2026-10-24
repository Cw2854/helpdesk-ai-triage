"""
Create or change the admin login for the web app.

    python set_password.py

It asks for a username and password, then saves to your .env file:
  - ADMIN_USERNAME
  - ADMIN_PASSWORD_HASH  (a salted hash: the real password is never stored anywhere)
  - SECRET_KEY           (a random key that signs the sign-in cookie; only created once)

Your other .env settings, like your Groq key, are left exactly as they are.
"""

import getpass
import secrets
from pathlib import Path

from werkzeug.security import generate_password_hash

ENV_PATH = Path(__file__).resolve().parent / ".env"   # always next to this script
MIN_LENGTH = 10


def update_env(values):
    """Set these keys in .env, keeping every other line as it was."""
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    remaining = dict(values)
    new_lines = []
    for line in lines:
        key = line.split("=", 1)[0].strip()
        if key in remaining:
            new_lines.append(f"{key}={remaining.pop(key)}")
        else:
            new_lines.append(line)
    if remaining:
        new_lines.append("")
        new_lines.append("# Admin web app (created by set_password.py)")
        new_lines.extend(f"{key}={value}" for key, value in remaining.items())
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def has_secret_key():
    if not ENV_PATH.exists():
        return False
    return any(line.startswith("SECRET_KEY=") and len(line) > len("SECRET_KEY=") + 10
               for line in ENV_PATH.read_text(encoding="utf-8").splitlines())


def main():
    print("\nSet up the admin login for the web app.")
    username = input("Username (press Enter for 'admin'): ").strip() or "admin"

    print(f"\nChoose a password of at least {MIN_LENGTH} characters.")
    print("(Nothing appears on screen while you type. That's normal.)")
    while True:
        password = getpass.getpass("Password: ")
        if len(password) < MIN_LENGTH:
            print(f"Too short: use at least {MIN_LENGTH} characters.\n")
            continue
        if getpass.getpass("Type it again: ") != password:
            print("Those didn't match. Try again.\n")
            continue
        break

    values = {
        "ADMIN_USERNAME": username,
        "ADMIN_PASSWORD_HASH": generate_password_hash(password),
    }
    if not has_secret_key():
        values["SECRET_KEY"] = secrets.token_hex(32)

    update_env(values)
    print(f"\nSaved. Sign in as '{username}' after running:  python app.py\n")


if __name__ == "__main__":
    main()
