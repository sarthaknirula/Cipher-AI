"""Dispatcher for validated AI responses."""

from typing import Any

from ai.tools.aes_tool import AESTool
from ai.tools.double_des_tool import DoubleDESTool
from ai.tools.rsa_tool import RSATool
from ai.tools.triple_des_tool import TripleDESTool


class AIDispatcher:
    """Route parsed AI responses to chat, clarification, or tools."""

    def __init__(self) -> None:
        """Instantiate all available AI tools once."""
        self.tools = {
            "AES": AESTool(),
            "RSA": RSATool(),
            "DOUBLE_DES": DoubleDESTool(),
            "TRIPLE_DES": TripleDESTool(),
        }

    def dispatch(self, parsed_response: dict[str, Any]) -> Any:
        """Dispatch a validated parser response and return the result."""
        action = parsed_response["action"]

        if action == "chat":
            return parsed_response["response"]

        if action == "clarify":
            return parsed_response["question"]

        if action == "tool":
            return self._dispatch_tool(parsed_response)

        raise ValueError(f"Unsupported action: {action}")

    def _dispatch_tool(self, parsed_response: dict[str, Any]) -> Any:
        """Execute the selected tool for a validated tool response."""
        service = parsed_response["service"]
        operation = parsed_response["operation"]
        arguments = parsed_response["arguments"]

        tool = self.tools.get(service)
        if tool is None:
            raise ValueError(f"Unsupported service: {service}")

        return tool.execute(operation, arguments)
