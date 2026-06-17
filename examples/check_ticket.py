"""Hit the service-desk API programmatically with the `requests` library.

Start the server first (in another terminal):

    uv run python webapp/server.py

Then run this:

    uv run python examples/check_ticket.py
    uv run python examples/check_ticket.py "My app crashes when I upload a PDF"
"""

from __future__ import annotations

import json
import sys

import requests

API_URL = "http://localhost:8000/api/classify"

DEFAULT_TICKET = "I was charged 49.99 three times but expected only one charge. How much do I get back?"


def classify(text: str) -> dict:
    response = requests.post(API_URL, json={"text": text}, timeout=120)
    response.raise_for_status()
    return response.json()


def main() -> None:
    ticket = " ".join(sys.argv[1:]) or DEFAULT_TICKET
    print(f"Ticket: {ticket}\n")
    try:
        result = classify(ticket)
    except requests.exceptions.ConnectionError:
        print("Could not reach the server. Start it with: uv run python webapp/server.py")
        sys.exit(1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
