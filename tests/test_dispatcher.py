"""Unit tests for AIDispatcher."""

import unittest
from unittest.mock import Mock, patch

from ai.dispatcher import AIDispatcher


class DispatcherTests(unittest.TestCase):
    """Verify AIDispatcher routes chat, clarify, and tool operations."""

    def setUp(self) -> None:
        self.dispatcher = AIDispatcher()

    def test_chat(self) -> None:
        """Verify chat responses are returned directly."""
        parsed_response = {
            "action": "chat",
            "response": "AES is a symmetric algorithm.",
        }
        result = self.dispatcher.dispatch(parsed_response)
        self.assertEqual(result, parsed_response["response"])

    def test_clarify(self) -> None:
        """Verify clarification questions are returned directly."""
        parsed_response = {
            "action": "clarify",
            "question": "Which algorithm would you like?",
        }
        result = self.dispatcher.dispatch(parsed_response)
        self.assertEqual(result, parsed_response["question"])

    def test_tool_selection(self) -> None:
        """Verify a supported tool is selected and called."""
        parsed_response = {
            "action": "tool",
            "service": "AES",
            "operation": "generate_key",
            "reason": "User requested AES key generation.",
            "arguments": {"key_size": 256},
        }

        mock_tool = Mock()
        mock_tool.execute.return_value = "/mock/path/aes.key"
        self.dispatcher.tools["AES"] = mock_tool

        result = self.dispatcher.dispatch(parsed_response)
        self.assertEqual(result, "/mock/path/aes.key")
        mock_tool.execute.assert_called_once_with("generate_key", {"key_size": 256})

    def test_unsupported_service(self) -> None:
        """Verify unsupported services raise a readable error."""
        parsed_response = {
            "action": "tool",
            "service": "BLOWFISH",
            "operation": "encrypt",
            "reason": "User requested unsupported encryption.",
            "arguments": {},
        }

        with self.assertRaisesRegex(ValueError, "Unsupported service: BLOWFISH"):
            self.dispatcher.dispatch(parsed_response)

    def test_unsupported_action(self) -> None:
        """Verify unsupported actions raise ValueError."""
        parsed_response = {
            "action": "unknown_action",
            "payload": "test",
        }

        with self.assertRaisesRegex(ValueError, "Unsupported action: unknown_action"):
            self.dispatcher.dispatch(parsed_response)


if __name__ == "__main__":
    unittest.main()
