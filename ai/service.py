"""Gemini chat service for the Cipher AI desktop application."""

import os
from typing import Any

from google import genai
from google.genai import types

from core import settings

from .conversation import ConversationManager, get_conversation_manager
from .prompts import SYSTEM_PROMPT
from .session_state import SessionState, get_session_state


class AIService:
    """Manage a persistent Gemini chat session and return raw responses."""

    DEFAULT_MODEL = settings.GEMINI_MODEL
    DEFAULT_TEMPERATURE = settings.GEMINI_TEMPERATURE

    def __init__(
        self,
        conversation_manager: ConversationManager | None = None,
        session_state: SessionState | None = None,
    ) -> None:
        """Configure the Gemini client and start a persistent chat session."""
        self.client: genai.Client | None = None
        self.chat_session: Any | None = None
        self.model_name = self.DEFAULT_MODEL
        self.conversation_manager = (
            conversation_manager or get_conversation_manager()
        )
        self.session_state = session_state or get_session_state()

        self._configure_client()
        self._start_chat()

    def _configure_client(self) -> None:
        """Create the Gemini client using the GEMINI_API_KEY environment variable."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

        self.client = genai.Client(api_key=api_key)

    def _start_chat(self) -> None:
        """Start a persistent Gemini chat session."""
        if self.client is None:
            raise RuntimeError("Gemini client is not configured.")

        self.chat_session = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=self.DEFAULT_TEMPERATURE,
            ),
        )

    def generate_response(self, user_message: str) -> str:
        """Send a user message to Gemini and return the raw response text."""
        if self.chat_session is None:
            raise RuntimeError("Gemini chat session is not started.")

        try:
            response = self.chat_session.send_message(self._build_prompt(user_message))
            return response.text or ""
        except Exception as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc

    def _build_prompt(self, user_message: str) -> str:
        """Build a memory-aware prompt while preserving the JSON contract."""
        sections = [
            "System Prompt",
            SYSTEM_PROMPT.strip(),
        ]

        session_context = self.session_state.format_context()
        if session_context:
            sections.append(session_context)

        conversation_history = self.conversation_manager.format_history()
        if conversation_history:
            sections.append(conversation_history)

        sections.extend(
            [
                "Current User Message",
                user_message,
            ]
        )

        return "\n\n".join(sections)
