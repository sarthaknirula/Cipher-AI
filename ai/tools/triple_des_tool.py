"""Triple DES AI tool interface."""

from typing import Any

from crypto.triple_des import TripleDESService

from .validation import validate_existing_directories, validate_existing_files


class TripleDESTool:
    """Thin adapter for Triple DES service operations."""

    def __init__(self) -> None:
        """Create the Triple DES service used by this tool."""
        self.service = TripleDESService()
        self.operations = {
            "generate_key": "generate_key",
            "encrypt": "encrypt",
            "decrypt": "decrypt",
        }

    def execute(self, operation: str, arguments: dict[str, Any]) -> Any:
        """Execute a Triple DES operation with dispatcher-provided arguments."""
        method_name = self.operations.get(operation)
        if method_name is None:
            raise ValueError(f"Unsupported operation: {operation}")

        self._validate_arguments(operation, arguments)
        method = getattr(self.service, method_name)
        return method(**arguments)

    def _validate_arguments(self, operation: str, arguments: dict[str, Any]) -> None:
        """Validate paths before the Triple DES service touches the filesystem."""
        file_arguments = {
            "encrypt": {
                "key1_path": "DES key file",
                "key2_path": "DES key file",
                "key3_path": "DES key file",
                "input_file_path": "Input file",
            },
            "decrypt": {
                "key1_path": "DES key file",
                "key2_path": "DES key file",
                "key3_path": "DES key file",
                "encrypted_file_path": "Encrypted file",
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
