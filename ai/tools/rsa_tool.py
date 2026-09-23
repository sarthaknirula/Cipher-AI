"""RSA AI tool interface."""

from typing import Any

from crypto.rsa import RSAService

from .validation import validate_existing_directories, validate_existing_files


class RSATool:
    """Thin adapter for RSA service operations."""

    def __init__(self) -> None:
        """Create the RSA service used by this tool."""
        self.service = RSAService()
        self.operations = {
            "generate_key": "generate_key_pair",
            "encrypt": "encrypt_file",
            "decrypt": "decrypt_file",
        }

    def execute(self, operation: str, arguments: dict[str, Any]) -> Any:
        """Execute an RSA operation with dispatcher-provided arguments."""
        method_name = self.operations.get(operation)
        if method_name is None:
            raise ValueError(f"Unsupported operation: {operation}")

        self._validate_arguments(operation, arguments)
        method = getattr(self.service, method_name)
        return method(**arguments)

    def _validate_arguments(self, operation: str, arguments: dict[str, Any]) -> None:
        """Validate paths before the RSA service touches the filesystem."""
        file_arguments = {
            "encrypt": {
                "public_key_path": "RSA public key",
                "input_file_path": "Input file",
            },
            "decrypt": {
                "private_key_path": "RSA private key",
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
