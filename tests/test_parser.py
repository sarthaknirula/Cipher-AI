"""Unit tests for AIParser."""

import unittest

from ai.parser import AIParser


class ParserTests(unittest.TestCase):
    """Verify AIParser validates schemas and handles markdown code fences."""

    def setUp(self) -> None:
        self.parser = AIParser()

    def test_valid_chat(self) -> None:
        raw = '{"action": "chat", "response": "AES is a symmetric cipher."}'
        parsed = self.parser.parse(raw)
        self.assertEqual(parsed["action"], "chat")
        self.assertEqual(parsed["response"], "AES is a symmetric cipher.")

    def test_markdown_code_fence_json(self) -> None:
        """Verify replies wrapped in ```json ... ``` code fences parse cleanly."""
        raw = """```json
{
    "action": "chat",
    "response": "Here is an explanation of AES-GCM."
}
```"""
        parsed = self.parser.parse(raw)
        self.assertEqual(parsed["action"], "chat")
        self.assertIn("AES-GCM", parsed["response"])

    def test_markdown_generic_fence(self) -> None:
        """Verify replies wrapped in ``` ... ``` code fences parse cleanly."""
        raw = """```
{
    "action": "clarify",
    "question": "What key size would you like to use?"
}
```"""
        parsed = self.parser.parse(raw)
        self.assertEqual(parsed["action"], "clarify")

    def test_valid_tool(self) -> None:
        raw = (
            '{"action": "tool", "service": "AES", "operation": "encrypt", '
            '"reason": "The user requested encryption.", "arguments": {"mode": "GCM"}}'
        )
        parsed = self.parser.parse(raw)
        self.assertEqual(parsed["action"], "tool")
        self.assertEqual(parsed["arguments"]["mode"], "GCM")

    def test_invalid_json_raises_value_error(self) -> None:
        raw = '{"action": "chat", "response": "Unclosed string'
        with self.assertRaisesRegex(ValueError, "Invalid JSON received from AI"):
            self.parser.parse(raw)

    def test_unknown_action_raises_value_error(self) -> None:
        raw = '{"action": "dance", "response": "music"}'
        with self.assertRaisesRegex(ValueError, "Unsupported action: dance"):
            self.parser.parse(raw)

    def test_missing_required_fields(self) -> None:
        raw = '{"action": "chat"}'
        with self.assertRaisesRegex(ValueError, "Missing required field: response"):
            self.parser.parse(raw)


if __name__ == "__main__":
    unittest.main()
