"""Conversation memory for the Cipher AI assistant."""

from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class ConversationMessage:
    """One readable message in the assistant conversation."""

    role: str
    content: str


class ConversationManager:
    """Store recent readable conversation history in chronological order."""

    MAX_USER_MESSAGES = 10
    MAX_ASSISTANT_MESSAGES = 10

    def __init__(self) -> None:
        self._messages: list[ConversationMessage] = []
        self._lock = RLock()

    def add_user_message(self, message: str) -> None:
        self._add_message("user", message)

    def add_assistant_message(self, message: str) -> None:
        self._add_message("assistant", message)

    def format_history(self) -> str:
        with self._lock:
            if not self._messages:
                return ""

            lines = ["Conversation History"]
            for message in self._messages:
                role = "User" if message.role == "user" else "Assistant"
                lines.extend(("", f"{role}:", message.content))

            return "\n".join(lines)

    def clear(self) -> None:
        with self._lock:
            self._messages.clear()

    def _add_message(self, role: str, content: str) -> None:
        content = content.strip()
        if not content:
            return

        with self._lock:
            self._messages.append(ConversationMessage(role, content))
            self._trim_role(role)

    def _trim_role(self, role: str) -> None:
        limit = (
            self.MAX_USER_MESSAGES
            if role == "user"
            else self.MAX_ASSISTANT_MESSAGES
        )
        role_indexes = [
            index
            for index, message in enumerate(self._messages)
            if message.role == role
        ]
        overflow = len(role_indexes) - limit
        if overflow <= 0:
            return

        remove_indexes = set(role_indexes[:overflow])
        self._messages = [
            message
            for index, message in enumerate(self._messages)
            if index not in remove_indexes
        ]


_conversation_manager = ConversationManager()


def get_conversation_manager() -> ConversationManager:
    """Return the application-lifetime conversation manager."""

    return _conversation_manager
