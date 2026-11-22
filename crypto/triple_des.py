"""Triple DES (3DES / TDEA) cryptographic service."""

from pathlib import Path

from core.paths import clean_decrypted_filename
from crypto.base_des import BaseDESService


class TripleDESService(BaseDESService):
    """Triple DES encryption and decryption service in EDE (Encrypt-Decrypt-Encrypt) mode."""

    KEY_COUNT = 3
    KEY_DIRECTORY_PREFIX = "TRIPLE_DES"

    def generate_key(self, save_directory: Path | None = None) -> tuple[Path, Path, Path]:
        """Generate three 8-byte DES keys and save them to disk."""
        save_directory = self._build_key_directory(self.KEY_DIRECTORY_PREFIX, save_directory)
        self._ensure_output_folder(save_directory)

        key1_path = self._save_key(save_directory / "key1.key", self._generate_key_bytes())
        key2_path = self._save_key(save_directory / "key2.key", self._generate_key_bytes())
        key3_path = self._save_key(save_directory / "key3.key", self._generate_key_bytes())

        return key1_path, key2_path, key3_path

    def encrypt(
        self,
        key1_path: Path,
        key2_path: Path,
        key3_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
        iv: bytes | str | None = None,
    ) -> Path:
        """Encrypt a file using Triple DES (EDE mode with CBC)."""
        key1_path = Path(key1_path)
        key2_path = Path(key2_path)
        key3_path = Path(key3_path)
        input_file_path = Path(input_file_path)
        output_folder = self._build_encryption_directory(self.KEY_DIRECTORY_PREFIX, output_folder)
        self._ensure_output_folder(output_folder)

        self._validate_file(input_file_path, "Input file")

        key1, key2, key3 = self._load_keys(key1_path, key2_path, key3_path)
        file_bytes = self._read_file_bytes(input_file_path)
        encrypted_bytes = self._encrypt_bytes(key1, key2, key3, file_bytes, iv)
        encrypted_file_path = output_folder / f"{input_file_path.name}.triple_des.enc"

        return self._save_encrypted_file(encrypted_file_path, encrypted_bytes)

    def decrypt(
        self,
        key1_path: Path,
        key2_path: Path,
        key3_path: Path,
        encrypted_file_path: Path,
        output_folder: Path | None = None,
    ) -> Path:
        """Decrypt a Triple DES encrypted file and restore clean filename."""
        key1_path = Path(key1_path)
        key2_path = Path(key2_path)
        key3_path = Path(key3_path)
        encrypted_file_path = Path(encrypted_file_path)
        output_folder = self._build_decryption_directory(self.KEY_DIRECTORY_PREFIX, output_folder)
        self._ensure_output_folder(output_folder)

        self._validate_file(encrypted_file_path, "Encrypted file")

        key1, key2, key3 = self._load_keys(key1_path, key2_path, key3_path)
        encrypted_bytes = self._read_file_bytes(encrypted_file_path)
        decrypted_bytes = self._decrypt_bytes(key1, key2, key3, encrypted_bytes)

        clean_name = clean_decrypted_filename(encrypted_file_path.name, ".triple_des.enc")
        decrypted_file_path = output_folder / clean_name

        return self._save_decrypted_file(decrypted_file_path, decrypted_bytes)

    def _load_keys(self, key1_path: Path, key2_path: Path, key3_path: Path) -> tuple[bytes, bytes, bytes]:
        key1 = self._load_key(key1_path)
        key2 = self._load_key(key2_path)
        key3 = self._load_key(key3_path)
        self._validate_keys((key1, key2, key3), self.KEY_COUNT)

        return key1, key2, key3

    def _encrypt_bytes(
        self,
        key1: bytes,
        key2: bytes,
        key3: bytes,
        file_bytes: bytes,
        iv: bytes | str | None = None,
    ) -> bytes:
        iv = self._resolve_iv(iv)
        padded_bytes = self._pad_bytes(file_bytes)
        first_pass = self._encrypt_with_key(key1, iv, padded_bytes)
        second_pass = self._decrypt_with_key(key2, iv, first_pass)
        third_pass = self._encrypt_with_key(key3, iv, second_pass)

        return iv + third_pass

    def _decrypt_bytes(self, key1: bytes, key2: bytes, key3: bytes, encrypted_bytes: bytes) -> bytes:
        iv, ciphertext = self._split_iv_and_ciphertext(encrypted_bytes)
        first_pass = self._decrypt_with_key(key3, iv, ciphertext)
        second_pass = self._encrypt_with_key(key2, iv, first_pass)
        padded_bytes = self._decrypt_with_key(key1, iv, second_pass)

        return self._unpad_bytes(padded_bytes)
