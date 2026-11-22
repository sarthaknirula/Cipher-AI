"""Cryptographic hashing and message authentication utilities."""

import hashlib
import hmac
from pathlib import Path
from typing import BinaryIO


class HashingService:
    """Service providing file hashing, byte hashing, and HMAC generation/verification."""

    SUPPORTED_ALGORITHMS = {
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "sha3_256": hashlib.sha3_256,
        "sha3_512": hashlib.sha3_512,
        "sha1": hashlib.sha1,
        "md5": hashlib.md5,
    }

    CHUNK_SIZE = 65536  # 64 KB

    def _get_hasher(self, algorithm: str) -> "hashlib._Hash":
        algo_key = algorithm.lower().replace("-", "_")
        hasher_factory = self.SUPPORTED_ALGORITHMS.get(algo_key)
        if hasher_factory is None:
            supported = ", ".join(sorted(self.SUPPORTED_ALGORITHMS.keys()))
            raise ValueError(
                f"Unsupported hashing algorithm '{algorithm}'. Supported: {supported}"
            )
        return hasher_factory()

    def hash_bytes(self, data: bytes, algorithm: str = "sha256") -> str:
        """Calculate hexadecimal hash digest for raw bytes."""
        if not isinstance(data, bytes):
            raise TypeError("Data must be bytes.")
        hasher = self._get_hasher(algorithm)
        hasher.update(data)
        return hasher.hexdigest()

    def hash_file(self, file_path: Path | str, algorithm: str = "sha256") -> str:
        """Calculate hexadecimal hash digest for a file using chunked streaming."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        hasher = self._get_hasher(algorithm)
        with file_path.open("rb") as f:
            while chunk := f.read(self.CHUNK_SIZE):
                hasher.update(chunk)

        return hasher.hexdigest()

    def generate_hmac(
        self,
        key: bytes,
        data: bytes | BinaryIO | Path,
        algorithm: str = "sha256",
    ) -> bytes:
        """Generate HMAC digest for bytes or a file."""
        if not isinstance(key, bytes) or len(key) == 0:
            raise ValueError("HMAC key must be non-empty bytes.")

        algo_key = algorithm.lower().replace("-", "_")
        hash_func = self.SUPPORTED_ALGORITHMS.get(algo_key)
        if hash_func is None:
            raise ValueError(f"Unsupported algorithm '{algorithm}' for HMAC.")

        mac = hmac.new(key, digestmod=hash_func)

        if isinstance(data, (str, Path)):
            file_path = Path(data)
            with file_path.open("rb") as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    mac.update(chunk)
        elif isinstance(data, bytes):
            mac.update(data)
        else:
            while chunk := data.read(self.CHUNK_SIZE):
                mac.update(chunk)

        return mac.digest()

    def verify_hmac(
        self,
        key: bytes,
        data: bytes | Path,
        expected_digest: bytes,
        algorithm: str = "sha256",
    ) -> bool:
        """Verify HMAC digest using constant-time comparison."""
        actual_digest = self.generate_hmac(key, data, algorithm)
        return hmac.compare_digest(actual_digest, expected_digest)


# Top-level module convenience functions
_default_service = HashingService()
hash_file = _default_service.hash_file
hash_bytes = _default_service.hash_bytes
generate_hmac = _default_service.generate_hmac
verify_hmac = _default_service.verify_hmac
