"""AES AI tool interface."""

from typing import Any

from crypto.aes import AESService

from .validation import validate_existing_directories, validate_existing_files


class AESTool:
    """Thin adapter for AES service operations."""

    def __init__(self) -> None:
        """Create the AES service used by this tool."""
        self.service = AESService()
        self.operations = {
            "generate_key": "generate_key",
            "encrypt": "encrypt",
            "decrypt": "decrypt",
        }

    def execute(self, operation: str, arguments: dict[str, Any]) -> Any:
        """Execute an AES operation with dispatcher-provided arguments."""
        method_name = self.operations.get(operation)
        if method_name is None:
            raise ValueError(f"Unsupported operation: {operation}")

        self._validate_arguments(operation, arguments)
        method = getattr(self.service, method_name)
        return method(**arguments)

    def _validate_arguments(self, operation: str, arguments: dict[str, Any]) -> None:
        """Validate paths before the AES service touches the filesystem."""
        file_arguments = {
            "encrypt": {
                "key_path": "Key file",
                "input_file_path": "Input file",
            },
            "decrypt": {
                "key_path": "Key file",
                "input_file_path": "Encrypted file",
            },
        }
        directory_arguments = {
            "generate_key": {"save_directory": "Output directory"},
            "encrypt": {"output_folder": "Output directory"},
            "decrypt": {"output_folder": "Output directory"},
        }

        validate_existing_files(arguments, file_arguments.get(operation, {}))
        validate_existing_directories(
            arguments,
            directory_arguments.get(operation, {}),
        )
