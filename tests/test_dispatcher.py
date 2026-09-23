"""Manual smoke tests for AIDispatcher."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.dispatcher import AIDispatcher


def test_chat(dispatcher: AIDispatcher) -> None:
    """Verify chat responses are returned directly."""
    parsed_response = {
        "action": "chat",
        "response": "AES is a symmetric algorithm.",
    }

    result = dispatcher.dispatch(parsed_response)
    if result == parsed_response["response"]:
        print("✓ Chat dispatch successful")


def test_clarify(dispatcher: AIDispatcher) -> None:
    """Verify clarification questions are returned directly."""
    parsed_response = {
        "action": "clarify",
        "question": "Which algorithm would you like?",
    }

    result = dispatcher.dispatch(parsed_response)
    if result == parsed_response["question"]:
        print("✓ Clarify dispatch successful")


def test_tool_selection(dispatcher: AIDispatcher) -> None:
    """Verify a supported tool is selected and called."""
    parsed_response = {
        "action": "tool",
        "service": "AES",
        "operation": "encrypt",
        "reason": "User requested AES encryption.",
        "arguments": {},
    }

    try:
        dispatcher.dispatch(parsed_response)
    except NotImplementedError:
        print("✓ Correct tool selected")


def test_unsupported_service(dispatcher: AIDispatcher) -> None:
    """Verify unsupported services raise a readable error."""
    parsed_response = {
        "action": "tool",
        "service": "BLOWFISH",
        "operation": "encrypt",
        "reason": "User requested unsupported encryption.",
        "arguments": {},
    }

    try:
        dispatcher.dispatch(parsed_response)
    except ValueError as exc:
        print(f"✓ Unsupported service handled: {exc}")


def main() -> None:
    """Run manual dispatcher checks without contacting Gemini."""
    dispatcher = AIDispatcher()

    test_chat(dispatcher)
    test_clarify(dispatcher)
    test_tool_selection(dispatcher)
    test_unsupported_service(dispatcher)


if __name__ == "__main__":
    main()
