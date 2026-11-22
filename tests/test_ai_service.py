"""Unit tests for AIService and response formatting."""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from ai.service import AIService


def format_response(response_text: str) -> str:
    """Pretty-print valid JSON responses and return raw text otherwise."""
    try:
        parsed_response = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text

    return json.dumps(parsed_response, indent=4)


class AIServiceTests(unittest.TestCase):
    """Test suite for Gemini AIService interactions."""

    def test_format_response_valid_json(self) -> None:
        """Valid JSON strings should be pretty-printed."""
        raw = '{"action": "chat", "message": "hello"}'
        formatted = format_response(raw)
        self.assertIn('"action": "chat"', formatted)
        self.assertIn("\n", formatted)

    def test_format_response_invalid_json(self) -> None:
        """Non-JSON text should be returned as raw string."""
        raw = "plain text response"
        self.assertEqual(format_response(raw), "plain text response")

    def test_missing_api_key_raises_runtime_error(self) -> None:
        """Initializing AIService without GEMINI_API_KEY must raise RuntimeError."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                AIService()
            self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    @patch("ai.service.genai.Client")
    def test_generate_response_calls_client(self, mock_client_cls: MagicMock) -> None:
        """generate_response should send message to Gemini chat session."""
        mock_client = MagicMock()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"action": "chat", "message": "Ready"}'
        mock_chat.send_message.return_value = mock_response
        mock_client.chats.create.return_value = mock_chat
        mock_client_cls.return_value = mock_client

        with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-test-key"}):
            service = AIService()
            reply = service.generate_response("hello copilot")
            self.assertEqual(reply, '{"action": "chat", "message": "Ready"}')
            mock_chat.send_message.assert_called_once()


if __name__ == "__main__":
    unittest.main()
