from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QThread, Qt, QTimer, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ai.conversation import ConversationManager, get_conversation_manager
from ai.dispatcher import AIDispatcher
from ai.parser import AIParser
from ai.service import AIService
from ai.session_state import SessionState, get_session_state
from ai.tools.validation import ToolValidationClarification
from gui.theme import DARK_THEME, ThemeName, get_home_stylesheet


WELCOME_MESSAGE = (
    "Hello!\n\n"
    "I can help you with:\n"
    "- Generate encryption keys\n"
    "- Encrypt files\n"
    "- Decrypt files\n"
    "- Explain cryptographic algorithms\n"
    "- Compare encryption methods\n\n"
    "What would you like to do today?"
)


@dataclass(frozen=True)
class AIResult:
    """Completed AI pipeline response for display."""

    parsed_response: dict[str, Any]
    dispatch_result: Any


class AIIntegrationError(Exception):
    """Error raised by the GUI coordinator for a failed pipeline stage."""

    def __init__(self, stage: str, original: Exception) -> None:
        super().__init__(str(original))
        self.stage = stage
        self.original = original


class AIWorker(QObject):
    """Run the existing AI backend pipeline away from the GUI thread."""

    started = Signal()
    finished = Signal()
    result_ready = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        user_message: str,
        conversation_manager: ConversationManager | None = None,
        session_state: SessionState | None = None,
    ) -> None:
        super().__init__()
        self.user_message = user_message
        self.conversation_manager = (
            conversation_manager or get_conversation_manager()
        )
        self.session_state = session_state or get_session_state()

    def run(self) -> None:
        self.started.emit()
        try:
            result = self._run_pipeline()
        except Exception as exc:
            self.error_occurred.emit(self._friendly_error_message(exc))
        else:
            self._record_success(result)
            self.result_ready.emit(result)
        finally:
            self.finished.emit()

    def _run_pipeline(self) -> AIResult:
        try:
            raw_response = AIService().generate_response(self.user_message)
        except Exception as exc:
            raise AIIntegrationError("service", exc) from exc

        try:
            parsed_response = AIParser().parse(raw_response)
        except Exception as exc:
            raise AIIntegrationError("parser", exc) from exc

        try:
            dispatch_result = AIDispatcher().dispatch(parsed_response)
        except ToolValidationClarification as exc:
            parsed_response = {
                "action": "clarify",
                "question": exc.question,
            }
            dispatch_result = exc.question
        except Exception as exc:
            raise AIIntegrationError("dispatcher", exc) from exc

        return AIResult(parsed_response, dispatch_result)

    def _record_success(self, result: AIResult) -> None:
        self.conversation_manager.add_user_message(self.user_message)

        if result.parsed_response.get("action") == "tool":
            self.session_state.update_from_tool_result(
                result.parsed_response,
                result.dispatch_result,
            )

        self.conversation_manager.add_assistant_message(
            self._format_assistant_memory(result)
        )

    def _format_assistant_memory(self, result: AIResult) -> str:
        action = result.parsed_response.get("action")
        if action in {"chat", "clarify"}:
            return str(result.dispatch_result)

        if action == "tool":
            service = str(result.parsed_response.get("service", "Tool")).replace(
                "_",
                " ",
            )
            operation = str(result.parsed_response.get("operation", "operation"))
            result_text = self._format_result_value(result.dispatch_result)
            return (
                f"{service.title()} {operation.replace('_', ' ')} completed "
                f"successfully. {result_text}"
            )

        return str(result.dispatch_result)

    def _format_result_value(self, result: Any) -> str:
        paths = self._flatten_paths(result)
        if paths:
            return "Result: " + ", ".join(str(path) for path in paths)

        if result is None:
            return ""

        return f"Result: {result}"

    def _flatten_paths(self, value: Any) -> list[Path]:
        if isinstance(value, Path):
            return [value]
        if isinstance(value, dict):
            paths: list[Path] = []
            for item in value.values():
                paths.extend(self._flatten_paths(item))
            return paths
        if isinstance(value, (list, tuple)):
            paths: list[Path] = []
            for item in value:
                paths.extend(self._flatten_paths(item))
            return paths

        return []

    def _friendly_error_message(self, error: Exception) -> str:
        if isinstance(error, AIIntegrationError):
            if error.stage == "service":
                return (
                    "I couldn't reach the AI service or complete its request right "
                    f"now. {error.original}"
                )

            if error.stage == "parser":
                return (
                    "I received a response from the AI service, but it was not in "
                    f"the expected format. {error.original}"
                )

            return (
                "I understood the request, but couldn't complete the crypto "
                f"operation. {error.original}"
            )

        return (
            "Something went wrong while completing that request. "
            "Please try again or rephrase it."
        )


class ChatInput(QTextEdit):
    """Text input that sends on Enter and inserts new lines on Shift+Enter."""

    send_requested = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)
            else:
                self.send_requested.emit()
            return

        super().keyPressEvent(event)


class MessageBubble(QFrame):
    """Reusable chat bubble with subtle metadata."""

    def __init__(
        self,
        role: str,
        message: str,
        object_name: str | None = None,
        title: str | None = None,
    ) -> None:
        super().__init__()
        base_name = object_name or f"{role}Message"
        self.setObjectName(base_name)
        self.setMaximumWidth(760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        if title:
            title_label = QLabel(title)
            title_label.setObjectName(f"{base_name}Title")
            title_label.setTextFormat(Qt.PlainText)
            layout.addWidget(title_label)

        body = QLabel(message)
        body.setObjectName(f"{base_name}Text")
        body.setTextFormat(Qt.PlainText)
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(body)

        timestamp = QLabel(datetime.now().strftime("%H:%M"))
        timestamp.setObjectName("messageMeta")
        timestamp.setAlignment(Qt.AlignRight)
        layout.addWidget(timestamp)


class ToolResultCard(QFrame):
    """Structured card for displaying completed tool operations."""

    def __init__(
        self,
        title: str,
        details: list[tuple[str, str]],
    ) -> None:
        super().__init__()
        self.setObjectName("toolResultCard")
        self.setMaximumWidth(760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("toolResultTitle")
        title_label.setTextFormat(Qt.PlainText)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        for label, value in details:
            field = QWidget()
            field.setObjectName("toolResultField")
            field_layout = QVBoxLayout(field)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(3)

            label_widget = QLabel(label)
            label_widget.setObjectName("toolResultLabel")
            label_widget.setTextFormat(Qt.PlainText)

            value_widget = QLabel(value)
            value_widget.setObjectName("toolResultValue")
            value_widget.setTextFormat(Qt.PlainText)
            value_widget.setWordWrap(True)
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)

            field_layout.addWidget(label_widget)
            field_layout.addWidget(value_widget)
            layout.addWidget(field)

        timestamp = QLabel(datetime.now().strftime("%H:%M"))
        timestamp.setObjectName("messageMeta")
        timestamp.setAlignment(Qt.AlignRight)
        layout.addWidget(timestamp)


class HomePage(QWidget):
    """AI assistant dashboard shown when the application starts."""

    SUGGESTIONS = (
        "Generate an AES key",
        "Encrypt a file",
        "Decrypt a file",
        "Explain AES",
        "Explain RSA",
        "AES vs RSA",
        "What is Triple DES?",
    )

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("homePage")
        self._theme = DARK_THEME
        self._thread: QThread | None = None
        self._worker: AIWorker | None = None
        self._is_busy = False

        self._build_layout()
        self._append_welcome_message()
        self._apply_styles()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 42, 48, 42)
        layout.setSpacing(18)

        header = QWidget()
        header.setObjectName("homeHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(14)

        title_area = QWidget()
        title_layout = QVBoxLayout(title_area)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(3)

        title = QLabel("Cipher AI")
        title.setObjectName("homeTitle")

        subtitle = QLabel("Your intelligent cryptography assistant.")
        subtitle.setObjectName("homeSubtitle")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(title_area, stretch=1)

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setObjectName("chatScrollArea")
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setFrameShape(QFrame.NoFrame)
        self.chat_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        chat_content = QWidget()
        chat_content.setObjectName("chatContent")
        self.chat_layout = QVBoxLayout(chat_content)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()
        self.chat_scroll.setWidget(chat_content)

        suggestions = self._create_suggestions()

        input_panel = QFrame()
        input_panel.setObjectName("chatInputPanel")
        input_layout = QHBoxLayout(input_panel)
        input_layout.setContentsMargins(12, 12, 12, 12)
        input_layout.setSpacing(12)

        self.input_edit = ChatInput()
        self.input_edit.setObjectName("chatInput")
        self.input_edit.setPlaceholderText(
            "Ask about cryptography or request an operation..."
        )
        self.input_edit.setFixedHeight(70)
        self.input_edit.send_requested.connect(self._send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setFixedWidth(104)
        self.send_button.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_edit, stretch=1)
        input_layout.addWidget(self.send_button)

        layout.addWidget(header)
        layout.addWidget(self.chat_scroll, stretch=1)
        layout.addWidget(suggestions)
        layout.addWidget(input_panel)

    def _create_suggestions(self) -> QWidget:
        scroll_area = QScrollArea()
        scroll_area.setObjectName("suggestionScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFixedHeight(48)

        wrapper = QWidget()
        wrapper.setObjectName("suggestionContent")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.suggestion_buttons: list[QPushButton] = []
        for suggestion in self.SUGGESTIONS:
            button = QPushButton(suggestion)
            button.setObjectName("suggestionButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedHeight(32)
            button.setMinimumWidth(button.sizeHint().width())
            button.clicked.connect(
                lambda checked=False, text=suggestion: self._use_suggestion(text)
            )
            self.suggestion_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()
        scroll_area.setWidget(wrapper)
        return scroll_area

    def _use_suggestion(self, text: str) -> None:
        self.input_edit.setPlainText(text)
        self.input_edit.setFocus()

    def _send_message(self) -> None:
        message = self.input_edit.toPlainText().strip()
        if not message or self._is_busy:
            return

        self.input_edit.clear()
        self._append_message("user", message)
        self._append_typing_indicator()
        self._set_busy(True)
        self._start_worker(message)

    def _start_worker(self, message: str) -> None:
        self._thread = QThread(self)
        self._worker = AIWorker(message)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.result_ready.connect(self._handle_worker_result)
        self._worker.error_occurred.connect(self._handle_worker_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_worker_thread)
        self._thread.start()

    def _handle_worker_result(self, result: AIResult) -> None:
        self._remove_thinking_message()
        self._append_result(result)
        self._scroll_to_bottom()

    def _handle_worker_error(self, error_message: str) -> None:
        self._remove_thinking_message()
        self._append_message("error", error_message)
        self._scroll_to_bottom()

    def _cleanup_worker_thread(self) -> None:
        thread = self._thread
        if thread is not None:
            thread.wait()
            thread.deleteLater()

        self._thread = None
        self._worker = None
        self._set_busy(False)

    def _append_result(self, result: AIResult) -> None:
        action = result.parsed_response.get("action")
        if action == "chat":
            self._append_message("assistant", str(result.dispatch_result))
            return

        if action == "clarify":
            self._append_message("assistant", str(result.dispatch_result))
            return

        if action == "tool":
            self._append_tool_result(result.parsed_response, result.dispatch_result)
            return

        self._append_message("assistant", str(result.dispatch_result))

    def _append_welcome_message(self) -> None:
        self._append_message(
            "assistant",
            WELCOME_MESSAGE,
            object_name="welcomeMessage",
            title="Cipher AI Assistant",
        )

    def _append_typing_indicator(self) -> None:
        self._append_message(
            "assistant",
            "Assistant is thinking...",
            object_name="thinkingMessage",
        )

    def _append_tool_result(
        self,
        parsed_response: dict[str, Any],
        result: Any,
    ) -> None:
        title = self._format_tool_title(parsed_response)
        details = self._build_tool_details(parsed_response, result)
        self._append_card(ToolResultCard(title, details))

    def _format_tool_title(self, parsed_response: dict[str, Any]) -> str:
        service = str(parsed_response.get("service", "Tool")).replace("_", " ")
        operation = str(parsed_response.get("operation", "operation"))
        operation_titles = {
            "generate_key": "Key Generated Successfully",
            "generate_key_pair": "Key Pair Generated Successfully",
            "encrypt": "Encryption Complete",
            "decrypt": "Decryption Complete",
        }
        fallback = f"{operation.replace('_', ' ').title()} Complete"
        summary = operation_titles.get(operation, fallback)
        return f"{service.title()} {summary}"

    def _build_tool_details(
        self,
        parsed_response: dict[str, Any],
        result: Any,
    ) -> list[tuple[str, str]]:
        details: list[tuple[str, str]] = []
        arguments = parsed_response.get("arguments", {})

        if isinstance(arguments, dict):
            display_keys = (
                "key_size",
                "algorithm",
                "mode",
                "input_file",
                "output_file",
                "key_file",
                "public_key_file",
                "private_key_file",
                "input_path",
                "output_path",
                "key_path",
                "public_key_path",
                "private_key_path",
            )
            for key in display_keys:
                if key in arguments and arguments[key]:
                    details.append((self._format_field_name(key), str(arguments[key])))

        paths = self._flatten_paths(result)
        if paths:
            details.append(("Saved To", "\n".join(str(path) for path in paths)))
        elif result is not None:
            details.append(("Result", self._format_result_value(result)))

        return details

    def _format_field_name(self, name: str) -> str:
        return name.replace("_", " ").title()

    def _format_result_value(self, result: Any) -> str:
        if isinstance(result, dict):
            return "\n".join(
                f"{self._format_field_name(str(key))}: {value}"
                for key, value in result.items()
            )

        return str(result)

    def _flatten_paths(self, value: Any) -> list[Path]:
        if isinstance(value, Path):
            return [value]
        if isinstance(value, dict):
            paths: list[Path] = []
            for item in value.values():
                paths.extend(self._flatten_paths(item))
            return paths
        if isinstance(value, (list, tuple)):
            paths: list[Path] = []
            for item in value:
                paths.extend(self._flatten_paths(item))
            return paths

        return []

    def _append_message(
        self,
        role: str,
        message: str,
        object_name: str | None = None,
        title: str | None = None,
    ) -> None:
        self._append_card(MessageBubble(role, message, object_name, title), role)

    def _append_card(self, card: QWidget, role: str = "assistant") -> None:
        row = QWidget()
        row.setObjectName(f"{role}MessageRow")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(0)

        if role == "user":
            row_layout.addStretch()
            row_layout.addWidget(card)
        else:
            row_layout.addWidget(card)
            row_layout.addStretch()

        insert_index = max(0, self.chat_layout.count() - 1)
        self.chat_layout.insertWidget(insert_index, row)
        self._scroll_to_bottom()

    def _remove_thinking_message(self) -> None:
        thinking_bubble = self.findChild(QFrame, "thinkingMessage")
        if thinking_bubble is None:
            return

        row = thinking_bubble.parentWidget()
        if row is not None:
            self.chat_layout.removeWidget(row)
            row.deleteLater()

    def _scroll_to_bottom(self) -> None:
        scrollbar = self.chat_scroll.verticalScrollBar()
        QTimer.singleShot(0, lambda: scrollbar.setValue(scrollbar.maximum()))

    def _set_busy(self, busy: bool) -> None:
        self.input_edit.setDisabled(busy)
        self.send_button.setDisabled(busy)
        for button in self.suggestion_buttons:
            button.setDisabled(busy)

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_home_stylesheet(self._theme))
