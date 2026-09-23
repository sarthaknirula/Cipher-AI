"""Manual interactive smoke test for AIService."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.service import AIService


def format_response(response_text: str) -> str:
    """Pretty-print valid JSON responses and return raw text otherwise."""
    try:
        parsed_response = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text

    return json.dumps(parsed_response, indent=4)


def main() -> None:
    """Run an interactive prompt loop against Gemini."""
    try:
        service = AIService()
    except RuntimeError as exc:
        print(f"AI service error: {exc}")
        return

    while True:
        try:
            user_input = input("\nYou:\n")
        except EOFError:
            break

        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            response = service.generate_response(user_input)
        except RuntimeError as exc:
            print(f"\nAI service error:\n{exc}")
            continue

        print("\nGemini:")
        print(format_response(response))


if __name__ == "__main__":
    main()
