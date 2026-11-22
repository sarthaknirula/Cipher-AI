"""Parser for raw AI responses used by the desktop application."""

import json
from typing import Any


class AIParser:
    """Convert raw AI response text into a validated dictionary."""

    ALLOWED_ACTIONS = {"chat", "tool", "clarify"}

    def parse(self, raw_response: str) -> dict[str, Any]:
        """Parse and validate a raw JSON response from AIService, handling markdown fences."""
        data = self._parse_json(raw_response)

        action = self._require_field(data, "action")
        if action not in self.ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported action: {action}")

        if action == "chat":
            self._validate_chat(data)
        elif action == "tool":
            self._validate_tool(data)
        elif action == "clarify":
            self._validate_clarify(data)

        return data

    def _parse_json(self, raw_response: str) -> dict[str, Any]:
        """Decode raw response text as a JSON object, stripping markdown code fences if present."""
        clean_text = self._strip_markdown_code_fences(raw_response)
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON received from AI.") from exc

        if not isinstance(data, dict):
            raise ValueError("AI response must be a JSON object.")

        return data

    @staticmethod
    def _strip_markdown_code_fences(text: str) -> str:
        """Strip ```json ... ``` code fences if present in the response."""
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            # drop opening fence line
            lines = lines[1:]
            # drop closing fence line if present
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return stripped

    def _validate_chat(self, data: dict[str, Any]) -> None:
        """Validate a chat response."""
        response = self._require_field(data, "response")
        if not isinstance(response, str):
            raise ValueError("Field must be a string: response")

    def _validate_tool(self, data: dict[str, Any]) -> None:
        """Validate a tool response."""
        self._require_field(data, "service")
        self._require_field(data, "operation")
        self._require_field(data, "reason")
        arguments = self._require_field(data, "arguments")

        if not isinstance(arguments, dict):
            raise ValueError("Field must be a dictionary: arguments")

    def _validate_clarify(self, data: dict[str, Any]) -> None:
        """Validate a clarify response."""
        question = self._require_field(data, "question")
        if not isinstance(question, str):
            raise ValueError("Field must be a string: question")

    def _require_field(self, data: dict[str, Any], field_name: str) -> Any:
        """Return a required field or raise a descriptive validation error."""
        if field_name not in data:
            raise ValueError(f"Missing required field: {field_name}")

        return data[field_name]
