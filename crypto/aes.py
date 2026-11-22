"""AES symmetric encryption service supporting authenticated GCM (default) and CBC modes with streaming."""

import datetime
import os
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from core.paths import (
    PROJECT_ROOT,
    clean_decrypted_filename,
    ensure_directory,
    get_timestamped_directory,
    resolve_unique_path,
)
from core.validators import validate_iv


class AESService:
    """Service providing AES key generation, file encryption, and decryption."""

    VALID_KEY_SIZES = (128, 192, 256)
    KEY_SIZE_BYTES = {
        128: 16,
        192: 24,
        256: 32,
    }
    BLOCK_SIZE_BYTES = 16
    BLOCK_SIZE_BITS = BLOCK_SIZE_BYTES * 8
    GCM_NONCE_SIZE_BYTES = 12
    GCM_MAGIC_HEADER = b"AESGCM\x01"
    STREAMING_THRESHOLD_BYTES = 5 * 1024 * 1024  # 5 MB
    CHUNK_SIZE = 65536  # 64 KB

    def generate_key(self, key_size: int, save_directory: Path | None = None) -> Path:
        """Generate a cryptographically secure random AES key."""
        self._validate_key_size(key_size)
        save_directory = self._build_key_directory(key_size, save_directory)
        self._ensure_output_folder(save_directory)

        key_path = save_directory / "aes.key"
        key_bytes = self._generate_key_bytes(key_size)

        return self._save_key(key_path, key_bytes)

    def encrypt(
        self,
        key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
        iv: bytes | str | None = None,
        mode: str = "GCM",
    ) -> Path:
        """Encrypt a file with AES in authenticated GCM (default) or CBC mode."""
        key_path = Path(key_path)
        input_file_path = Path(input_file_path)

        self._validate_file(input_file_path, "Input file")
        output_folder = self._build_encryption_directory(output_folder)
        self._ensure_output_folder(output_folder)

        key_bytes = self._load_key(key_path)
        encrypted_file_path = output_folder / f"{input_file_path.name}.aes.enc"

        # If a 16-byte IV is passed without explicit mode override, gracefully use CBC for backward compatibility
        chosen_mode = mode.upper()
        if iv is not None and chosen_mode == "GCM":
            try:
                self._resolve_gcm_nonce(iv)
            except ValueError:
                try:
                    self._resolve_iv(iv)
                    chosen_mode = "CBC"
                except ValueError:
                    pass

        if chosen_mode == "GCM":
            nonce = self._resolve_gcm_nonce(iv)
            file_bytes = self._read_file_bytes(input_file_path)
            encrypted_payload = self._encrypt_bytes_gcm(key_bytes, file_bytes, nonce)
            return self._save_encrypted_file(encrypted_file_path, encrypted_payload)

        # CBC mode: use streaming for large files to avoid memory spikes
        file_size = input_file_path.stat().st_size
        resolved_iv = self._resolve_iv(iv)

        if file_size >= self.STREAMING_THRESHOLD_BYTES:
            target_path = resolve_unique_path(encrypted_file_path)
            self._encrypt_stream_cbc(key_bytes, resolved_iv, input_file_path, target_path)
            return target_path

        file_bytes = self._read_file_bytes(input_file_path)
        encrypted_bytes = self._encrypt_bytes_cbc(key_bytes, file_bytes, resolved_iv)
        return self._save_encrypted_file(encrypted_file_path, encrypted_bytes)

    def decrypt(
        self,
        key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
        mode: str | None = None,
    ) -> Path:
        """Decrypt an AES encrypted file with auto-detection for GCM/CBC and cleaned filenames."""
        key_path = Path(key_path)
        input_file_path = Path(input_file_path)

        self._validate_file(input_file_path, "Encrypted file")
        output_folder = self._build_decryption_directory(output_folder)
        self._ensure_output_folder(output_folder)

        key_bytes = self._load_key(key_path)
        encrypted_bytes = self._read_file_bytes(input_file_path)

        # Auto-detect GCM mode via magic header or explicit parameter
        is_gcm = (
            (mode and mode.upper() == "GCM")
            or encrypted_bytes.startswith(self.GCM_MAGIC_HEADER)
        )

        if is_gcm:
            decrypted_bytes = self._decrypt_bytes_gcm(key_bytes, encrypted_bytes)
        else:
            decrypted_bytes = self._decrypt_bytes_cbc(key_bytes, encrypted_bytes)

        clean_name = clean_decrypted_filename(input_file_path.name, ".aes.enc")
        decrypted_file_path = output_folder / clean_name

        return self._save_decrypted_file(decrypted_file_path, decrypted_bytes)

    # GCM Operations
    def encrypt_gcm(
        self,
        key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
        nonce: bytes | str | None = None,
    ) -> Path:
        """Convenience method for AES-GCM authenticated encryption."""
        return self.encrypt(key_path, input_file_path, output_folder, iv=nonce, mode="GCM")

    def decrypt_gcm(
        self,
        key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
    ) -> Path:
        """Convenience method for AES-GCM authenticated decryption."""
        return self.decrypt(key_path, input_file_path, output_folder, mode="GCM")

    def _resolve_gcm_nonce(self, nonce: bytes | str | None) -> bytes:
        if nonce is None:
            return os.urandom(self.GCM_NONCE_SIZE_BYTES)
        return validate_iv(nonce, self.GCM_NONCE_SIZE_BYTES)

    def _encrypt_bytes_gcm(self, key_bytes: bytes, file_bytes: bytes, nonce: bytes) -> bytes:
        aesgcm = AESGCM(key_bytes)
        ciphertext_and_tag = aesgcm.encrypt(nonce, file_bytes, None)
        return self.GCM_MAGIC_HEADER + nonce + ciphertext_and_tag

    def _decrypt_bytes_gcm(self, key_bytes: bytes, encrypted_payload: bytes) -> bytes:
        if encrypted_payload.startswith(self.GCM_MAGIC_HEADER):
            payload = encrypted_payload[len(self.GCM_MAGIC_HEADER) :]
        else:
            payload = encrypted_payload

        min_len = self.GCM_NONCE_SIZE_BYTES + 16  # nonce + 16-byte tag
        if len(payload) < min_len:
            raise ValueError("Encrypted GCM payload is too short to be valid.")

        nonce = payload[: self.GCM_NONCE_SIZE_BYTES]
        ciphertext_and_tag = payload[self.GCM_NONCE_SIZE_BYTES :]

        aesgcm = AESGCM(key_bytes)
        try:
            return aesgcm.decrypt(nonce, ciphertext_and_tag, None)
        except InvalidTag as exc:
            raise ValueError(
                "Authentication failed: The ciphertext has been tampered with or the key is invalid."
            ) from exc

    # Streaming CBC Operations
    def _encrypt_stream_cbc(
        self,
        key_bytes: bytes,
        iv: bytes,
        input_file_path: Path,
        output_file_path: Path,
    ) -> None:
        encryptor = self._build_cipher(key_bytes, iv).encryptor()
        padder = padding.PKCS7(self.BLOCK_SIZE_BITS).padder()

        with input_file_path.open("rb") as fin, output_file_path.open("wb") as fout:
            fout.write(iv)
            while chunk := fin.read(self.CHUNK_SIZE):
                padded = padder.update(chunk)
                if padded:
                    fout.write(encryptor.update(padded))
            final_padded = padder.finalize()
            if final_padded:
                fout.write(encryptor.update(final_padded))
            fout.write(encryptor.finalize())

    # CBC Byte Operations (Preserving backwards compatibility)
    def _encrypt_bytes(
        self,
        key_bytes: bytes,
        file_bytes: bytes,
        iv: bytes | str | None = None,
    ) -> bytes:
        return self._encrypt_bytes_cbc(key_bytes, file_bytes, self._resolve_iv(iv))

    def _encrypt_bytes_cbc(self, key_bytes: bytes, file_bytes: bytes, iv: bytes) -> bytes:
        padded_bytes = self._pad_bytes(file_bytes)
        encryptor = self._build_cipher(key_bytes, iv).encryptor()
        ciphertext = encryptor.update(padded_bytes) + encryptor.finalize()

        return iv + ciphertext

    def _decrypt_bytes(self, key_bytes: bytes, encrypted_bytes: bytes) -> bytes:
        return self._decrypt_bytes_cbc(key_bytes, encrypted_bytes)

    def _decrypt_bytes_cbc(self, key_bytes: bytes, encrypted_bytes: bytes) -> bytes:
        iv, ciphertext = self._split_iv_and_ciphertext(encrypted_bytes)
        decryptor = self._build_cipher(key_bytes, iv).decryptor()
        padded_bytes = decryptor.update(ciphertext) + decryptor.finalize()

        return self._unpad_bytes(padded_bytes)

    # Directory and File Helpers
    def _validate_key_size(self, key_size: int) -> None:
        if key_size not in self.VALID_KEY_SIZES:
            raise ValueError("Invalid AES key size. Key size must be 128, 192, or 256.")

    def _build_key_directory(self, key_size: int, save_directory: Path | None) -> Path:
        if save_directory is not None:
            return ensure_directory(Path(save_directory))

        return get_timestamped_directory("keys", f"AES_{key_size}")

    def _build_encryption_directory(self, output_folder: Path | None) -> Path:
        if output_folder is not None:
            return ensure_directory(Path(output_folder))

        return get_timestamped_directory("encrypted", "AES")

    def _build_decryption_directory(self, output_folder: Path | None) -> Path:
        if output_folder is not None:
            return ensure_directory(Path(output_folder))

        return get_timestamped_directory("decrypted", "AES")

    def _ensure_output_folder(self, output_folder: Path) -> None:
        ensure_directory(output_folder)

    def _validate_file(self, file_path: Path, file_label: str) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_label} not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"{file_label} is not a file: {file_path}")

    def _generate_key_bytes(self, key_size: int) -> bytes:
        self._validate_key_size(key_size)
        return os.urandom(self.KEY_SIZE_BYTES[key_size])

    def _generate_iv(self) -> bytes:
        return os.urandom(self.BLOCK_SIZE_BYTES)

    def _resolve_iv(self, iv: bytes | str | None) -> bytes:
        if iv is None:
            return self._generate_iv()
        return validate_iv(iv, self.BLOCK_SIZE_BYTES)

    def _load_key(self, key_path: Path) -> bytes:
        self._validate_file(key_path, "Key file")
        key_bytes = key_path.read_bytes()
        self._validate_key(key_bytes)
        return key_bytes

    def _validate_key(self, key_bytes: bytes) -> None:
        if not isinstance(key_bytes, bytes):
            raise TypeError("AES key must be bytes.")
        if len(key_bytes) not in self.KEY_SIZE_BYTES.values():
            raise ValueError("AES key must be 16, 24, or 32 bytes.")

    def _read_file_bytes(self, file_path: Path) -> bytes:
        return file_path.read_bytes()

    def _pad_bytes(self, file_bytes: bytes) -> bytes:
        padder = padding.PKCS7(self.BLOCK_SIZE_BITS).padder()
        return padder.update(file_bytes) + padder.finalize()

    def _unpad_bytes(self, padded_bytes: bytes) -> bytes:
        unpadder = padding.PKCS7(self.BLOCK_SIZE_BITS).unpadder()
        return unpadder.update(padded_bytes) + unpadder.finalize()

    def _split_iv_and_ciphertext(self, encrypted_bytes: bytes) -> tuple[bytes, bytes]:
        if len(encrypted_bytes) <= self.BLOCK_SIZE_BYTES:
            raise ValueError("Encrypted file is too small to contain an IV and ciphertext.")

        iv = encrypted_bytes[: self.BLOCK_SIZE_BYTES]
        ciphertext = encrypted_bytes[self.BLOCK_SIZE_BYTES :]
        if len(ciphertext) % self.BLOCK_SIZE_BYTES != 0:
            raise ValueError("Encrypted ciphertext has an invalid size.")

        return iv, ciphertext

    def _build_cipher(self, key_bytes: bytes, iv: bytes) -> Cipher:
        self._validate_key(key_bytes)
        if len(iv) != self.BLOCK_SIZE_BYTES:
            raise ValueError(f"IV must be {self.BLOCK_SIZE_BYTES} bytes.")

        return Cipher(AES(key_bytes), modes.CBC(iv))

    def _save_key(self, file_path: Path, key_bytes: bytes) -> Path:
        unique_path = resolve_unique_path(file_path)
        unique_path.write_bytes(key_bytes)
        return unique_path

    def _save_encrypted_file(self, file_path: Path, encrypted_bytes: bytes) -> Path:
        unique_path = resolve_unique_path(file_path)
        unique_path.write_bytes(encrypted_bytes)
        return unique_path

    def _save_decrypted_file(self, file_path: Path, decrypted_bytes: bytes) -> Path:
        unique_path = resolve_unique_path(file_path)
        unique_path.write_bytes(decrypted_bytes)
        return unique_path
