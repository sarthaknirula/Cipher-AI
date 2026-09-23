"""Application session state for the Cipher AI assistant."""

from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any


@dataclass
class SessionSnapshot:
    """Serializable snapshot of the current application session."""

    last_algorithm: str | None = None
    last_generated_key: str | None = None
    last_public_key: str | None = None
    last_private_key: str | None = None
    last_input_file: str | None = None
    last_output_folder: str | None = None
    last_iv: str | None = None
    last_operation: str | None = None


class SessionState:
    """Store important application state separately from conversation text."""

    FIELD_LABELS = {
        "last_algorithm": "Last Algorithm",
        "last_generated_key": "Last Generated Key",
        "last_public_key": "Last Public Key",
        "last_private_key": "Last Private Key",
        "last_input_file": "Last Input File",
        "last_output_folder": "Last Output Folder",
        "last_iv": "Last IV",
        "last_operation": "Last Operation",
    }

    def __init__(self) -> None:
        self._snapshot = SessionSnapshot()
        self._lock = RLock()

    def update_from_tool_result(
        self,
        parsed_response: dict[str, Any],
        result: Any,
    ) -> None:
        if parsed_response.get("action") != "tool":
            return

        service = self._normalize_service(parsed_response.get("service"))
        operation = self._string_or_none(parsed_response.get("operation"))
        arguments = parsed_response.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}

        with self._lock:
            if service:
                self._snapshot.last_algorithm = service
            if operation:
                self._snapshot.last_operation = operation

            if operation == "generate_key":
                self._update_generated_keys(service, result)
            elif operation in {"encrypt", "decrypt"}:
                self._update_file_operation(arguments, result)

    def format_context(self) -> str:
        with self._lock:
            fields = [
                ("last_algorithm", self._snapshot.last_algorithm),
                ("last_generated_key", self._snapshot.last_generated_key),
                ("last_public_key", self._snapshot.last_public_key),
                ("last_private_key", self._snapshot.last_private_key),
                ("last_input_file", self._snapshot.last_input_file),
                ("last_output_folder", self._snapshot.last_output_folder),
                ("last_iv", self._snapshot.last_iv),
                ("last_operation", self._snapshot.last_operation),
            ]

        populated = [
            (self.FIELD_LABELS[name], value)
            for name, value in fields
            if value
        ]
        if not populated:
            return ""

        lines = ["Current Session"]
        for label, value in populated:
            lines.extend(("", f"{label}:", value))

        return "\n".join(lines)

    def clear(self) -> None:
        with self._lock:
            self._snapshot = SessionSnapshot()

    def _update_generated_keys(self, service: str | None, result: Any) -> None:
        paths = self._flatten_paths(result)
        if service == "RSA" and len(paths) >= 2:
            self._snapshot.last_public_key = str(paths[0])
            self._snapshot.last_private_key = str(paths[1])
            return

        if paths:
            self._snapshot.last_generated_key = "\n".join(str(path) for path in paths)

    def _update_file_operation(
        self,
        arguments: dict[str, Any],
        result: Any,
    ) -> None:
        input_file = (
            arguments.get("input_file_path")
            or arguments.get("encrypted_file_path")
            or arguments.get("input_file")
            or arguments.get("input_path")
        )
        if input_file:
            self._snapshot.last_input_file = str(input_file)

        output_paths = self._flatten_paths(result)
        if output_paths:
            self._snapshot.last_output_folder = str(output_paths[0].parent)
        elif arguments.get("output_folder"):
            self._snapshot.last_output_folder = str(arguments["output_folder"])

        if arguments.get("iv"):
            self._snapshot.last_iv = str(arguments["iv"])

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

    def _normalize_service(self, service: Any) -> str | None:
        if not isinstance(service, str) or not service:
            return None

        return service.replace("_", " ")

    def _string_or_none(self, value: Any) -> str | None:
        if isinstance(value, str) and value:
            return value

        return None


_session_state = SessionState()


def get_session_state() -> SessionState:
    """Return the application-lifetime session state."""

    return _session_state
