"""Manual smoke tests for AIParser."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.parser import AIParser


def run_case(name: str, raw_response: str) -> None:
    """Parse one hardcoded response and print the result."""
    parser = AIParser()

    print(f"\n{name}")
    try:
        parser.parse(raw_response)
    except ValueError as exc:
        print(f"Error: {exc}")
    else:
        print("✓ Parsed Successfully")


def main() -> None:
    """Run manual parser checks without contacting Gemini."""
    cases = [
        (
            "Valid chat",
            '{"action": "chat", "response": "AES is a symmetric cipher."}',
        ),
        (
            "Valid tool",
            (
                '{"action": "tool", "service": "AES", "operation": "encrypt", '
                '"reason": "The user requested encryption.", "arguments": {}}'
            ),
        ),
        (
            "Valid clarify",
            '{"action": "clarify", "question": "Which algorithm would you like?"}',
        ),
        (
            "Invalid JSON",
            '{"action": "chat", "response": "AES is..."',
        ),
        (
            "Unknown action",
            '{"action": "unknown", "response": "No matching action."}',
        ),
        (
            "Missing chat field",
            '{"action": "chat"}',
        ),
        (
            "Missing tool field",
            (
                '{"action": "tool", "service": "AES", "operation": "encrypt", '
                '"reason": "The user requested encryption."}'
            ),
        ),
        (
            "Invalid tool arguments",
            (
                '{"action": "tool", "service": "AES", "operation": "encrypt", '
                '"reason": "The user requested encryption.", "arguments": []}'
            ),
        ),
        (
            "Missing clarify field",
            '{"action": "clarify"}',
        ),
    ]

    for name, raw_response in cases:
        run_case(name, raw_response)


if __name__ == "__main__":
    main()
