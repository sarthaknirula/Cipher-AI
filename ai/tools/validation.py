"""Shared preflight validation for AI tool adapters."""

from pathlib import Path
from typing import Any


class ToolValidationClarification(Exception):
    """Raised when a tool request should pause for user clarification."""

    def __init__(self, question: str) -> None:
        super().__init__(question)
        self.question = question


def validate_existing_files(
    arguments: dict[str, Any],
    required_files: dict[str, str],
) -> None:
    """Validate required file arguments before invoking crypto services."""
    for argument_name, label in required_files.items():
        raw_path = arguments.get(argument_name)
        if raw_path is None:
            continue

        file_path = Path(raw_path)
        if not file_path.exists():
            raise ToolValidationClarification(
                f"The specified {label.lower()} does not exist:\n\n"
                f"{file_path}\n\n"
                "Please provide a valid file path before I continue."
            )
        if not file_path.is_file():
            raise ToolValidationClarification(
                f"The specified {label.lower()} is not a file:\n\n"
                f"{file_path}\n\n"
                "Please provide a valid file path before I continue."
            )


def validate_existing_directories(
    arguments: dict[str, Any],
    directory_arguments: dict[str, str],
) -> None:
    """Validate explicitly supplied output directories."""
    for argument_name, label in directory_arguments.items():
        raw_path = arguments.get(argument_name)
        if raw_path is None:
            continue

        directory_path = Path(raw_path)
        if not directory_path.exists():
            raise ToolValidationClarification(
                f"The specified {label.lower()} does not exist:\n\n"
                f"{directory_path}\n\n"
                "Would you like to:\n\n"
                "1. Provide a different output directory.\n\n"
                "2. Save the output in the default application output directory."
            )
        if not directory_path.is_dir():
            raise ToolValidationClarification(
                f"The specified {label.lower()} is not a directory:\n\n"
                f"{directory_path}\n\n"
                "Please provide a valid directory before I continue."
            )
