import datetime
import os
from pathlib import Path

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES

from core.validators import validate_iv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class AESService:
    VALID_KEY_SIZES = (128, 192, 256)
    KEY_SIZE_BYTES = {
        128: 16,
        192: 24,
        256: 32,
    }
    BLOCK_SIZE_BYTES = 16
    BLOCK_SIZE_BITS = BLOCK_SIZE_BYTES * 8

    def generate_key(self, key_size: int, save_directory: Path | None = None) -> Path:
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
    ) -> Path:
        key_path = Path(key_path)
        input_file_path = Path(input_file_path)

        self._validate_file(input_file_path, "Input file")
        output_folder = self._build_encryption_directory(output_folder)
        self._ensure_output_folder(output_folder)

        key_bytes = self._load_key(key_path)
        file_bytes = self._read_file_bytes(input_file_path)
        encrypted_bytes = self._encrypt_bytes(key_bytes, file_bytes, iv)
        encrypted_file_path = output_folder / f"{input_file_path.name}.aes.enc"

        return self._save_encrypted_file(encrypted_file_path, encrypted_bytes)

    def decrypt(
        self,
        key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
    ) -> Path:
        key_path = Path(key_path)
        input_file_path = Path(input_file_path)

        self._validate_file(input_file_path, "Encrypted file")
        output_folder = self._build_decryption_directory(output_folder)
        self._ensure_output_folder(output_folder)

        key_bytes = self._load_key(key_path)
        encrypted_bytes = self._read_file_bytes(input_file_path)
        decrypted_bytes = self._decrypt_bytes(key_bytes, encrypted_bytes)
        decrypted_file_path = output_folder / f"decrypted_{input_file_path.name}"

        return self._save_decrypted_file(decrypted_file_path, decrypted_bytes)

    def _validate_key_size(self, key_size: int) -> None:
        if key_size not in self.VALID_KEY_SIZES:
            raise ValueError("Invalid AES key size. Key size must be 128, 192, or 256.")

    def _build_key_directory(
        self,
        key_size: int,
        save_directory: Path | None,
    ) -> Path:
        if save_directory is not None:
            return Path(save_directory)

        return self._build_timestamped_directory("keys", f"AES_{key_size}")

    def _build_encryption_directory(self, output_folder: Path | None) -> Path:
        if output_folder is not None:
            return Path(output_folder)

        return self._build_timestamped_directory("encrypted", "AES")

    def _build_decryption_directory(self, output_folder: Path | None) -> Path:
        if output_folder is not None:
            return Path(output_folder)

        return self._build_timestamped_directory("decrypted", "AES")

    def _build_timestamped_directory(self, *parts: str) -> Path:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return PROJECT_ROOT / "storage" / Path(*parts) / timestamp

    def _ensure_output_folder(self, output_folder: Path) -> None:
        output_folder.mkdir(parents=True, exist_ok=True)
        if not output_folder.is_dir():
            raise ValueError(f"Output folder is not a directory: {output_folder}")

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

    def _encrypt_bytes(
        self,
        key_bytes: bytes,
        file_bytes: bytes,
        iv: bytes | str | None = None,
    ) -> bytes:
        iv = self._resolve_iv(iv)
        padded_bytes = self._pad_bytes(file_bytes)
        encryptor = self._build_cipher(key_bytes, iv).encryptor()
        ciphertext = encryptor.update(padded_bytes) + encryptor.finalize()

        return iv + ciphertext

    def _decrypt_bytes(self, key_bytes: bytes, encrypted_bytes: bytes) -> bytes:
        iv, ciphertext = self._split_iv_and_ciphertext(encrypted_bytes)
        decryptor = self._build_cipher(key_bytes, iv).decryptor()
        padded_bytes = decryptor.update(ciphertext) + decryptor.finalize()

        return self._unpad_bytes(padded_bytes)

    def _save_key(self, file_path: Path, key_bytes: bytes) -> Path:
        file_path.write_bytes(key_bytes)

        return file_path

    def _save_encrypted_file(self, file_path: Path, encrypted_bytes: bytes) -> Path:
        file_path.write_bytes(encrypted_bytes)

        return file_path

    def _save_decrypted_file(self, file_path: Path, decrypted_bytes: bytes) -> Path:
        file_path.write_bytes(decrypted_bytes)

        return file_path
