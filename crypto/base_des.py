import datetime
import os
from pathlib import Path

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES

from core.validators import validate_iv

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class BaseDESService:
    KEY_SIZE_BYTES = 8
    BLOCK_SIZE_BYTES = 8
    BLOCK_SIZE_BITS = BLOCK_SIZE_BYTES * 8

    def _build_key_directory(self, algorithm_name: str, save_directory: Path | None) -> Path:
        if save_directory is not None:
            return Path(save_directory)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return PROJECT_ROOT / "storage" / "keys" / f"{algorithm_name}_{timestamp}"

    def _ensure_output_folder(self, output_folder: Path) -> None:
        output_folder.mkdir(parents=True, exist_ok=True)
        if not output_folder.is_dir():
            raise ValueError(f"Output folder is not a directory: {output_folder}")

    def _validate_file(self, file_path: Path, file_label: str) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_label} not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"{file_label} is not a file: {file_path}")

    def _generate_key_bytes(self) -> bytes:
        return os.urandom(self.KEY_SIZE_BYTES)

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
            raise TypeError("DES key must be bytes.")
        if len(key_bytes) != self.KEY_SIZE_BYTES:
            raise ValueError(f"DES key must be {self.KEY_SIZE_BYTES} bytes.")

    def _validate_keys(self, key_bytes_list: tuple[bytes, ...], expected_count: int) -> None:
        if len(key_bytes_list) != expected_count:
            raise ValueError(f"Expected {expected_count} DES keys.")

        for key_bytes in key_bytes_list:
            self._validate_key(key_bytes)

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

        return Cipher(TripleDES(key_bytes), modes.CBC(iv))

    def _encrypt_with_key(self, key_bytes: bytes, iv: bytes, file_bytes: bytes) -> bytes:
        encryptor = self._build_cipher(key_bytes, iv).encryptor()

        return encryptor.update(file_bytes) + encryptor.finalize()

    def _decrypt_with_key(self, key_bytes: bytes, iv: bytes, encrypted_bytes: bytes) -> bytes:
        decryptor = self._build_cipher(key_bytes, iv).decryptor()

        return decryptor.update(encrypted_bytes) + decryptor.finalize()

    def _save_key(self, file_path: Path, key_bytes: bytes) -> Path:
        file_path.write_bytes(key_bytes)

        return file_path

    def _save_encrypted_file(self, file_path: Path, encrypted_bytes: bytes) -> Path:
        file_path.write_bytes(encrypted_bytes)

        return file_path

    def _save_decrypted_file(self, file_path: Path, decrypted_bytes: bytes) -> Path:
        file_path.write_bytes(decrypted_bytes)

        return file_path
