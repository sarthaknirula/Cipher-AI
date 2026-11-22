"""Double DES cryptographic service with educational Meet-in-the-Middle notes."""

import hashlib
from pathlib import Path

from core.paths import clean_decrypted_filename
from crypto.base_des import BaseDESService


class DoubleDESService(BaseDESService):
    """Double DES encryption and decryption service.

    EDUCATIONAL SECURITY NOTE:
    Double DES uses two distinct 56-bit DES keys (total 112 bits of key material).
    While naive analysis suggests 112 bits of security, Double DES is vulnerable to the
    classic Meet-in-the-Middle (MitM) attack. A known-plaintext MitM attacker can compute
    forward encryptions with K1 and backward decryptions with K2, finding a match in approximately
    2^57 operations and O(2^56) storage rather than 2^112.

    Double DES is implemented here for educational and demonstration purposes. For production
    use cases, AES-256 or Triple DES (3DES) should be preferred.
    """

    KEY_COUNT = 2
    KEY_DIRECTORY_PREFIX = "DOUBLE_DES"

    def generate_key(self, save_directory: Path | None = None) -> tuple[Path, Path]:
        """Generate two 8-byte DES keys and save them to disk."""
        save_directory = self._build_key_directory(self.KEY_DIRECTORY_PREFIX, save_directory)
        self._ensure_output_folder(save_directory)

        key1_path = self._save_key(save_directory / "key1.key", self._generate_key_bytes())
        key2_path = self._save_key(save_directory / "key2.key", self._generate_key_bytes())

        return key1_path, key2_path

    def encrypt(
        self,
        key1_path: Path,
        key2_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
        iv: bytes | str | None = None,
    ) -> Path:
        """Encrypt a file using Double DES in CBC mode.

        Pass 1: E(K1, IV1, plaintext)
        Pass 2: E(K2, IV2, pass1_result)
        where IV2 is cryptographically derived from IV1 and K2 to prevent identical IV reuse.
        """
        key1_path = Path(key1_path)
        key2_path = Path(key2_path)
        input_file_path = Path(input_file_path)
        output_folder = self._build_encryption_directory(self.KEY_DIRECTORY_PREFIX, output_folder)
        self._ensure_output_folder(output_folder)

        self._validate_file(input_file_path, "Input file")

        key1, key2 = self._load_keys(key1_path, key2_path)
        file_bytes = self._read_file_bytes(input_file_path)
        encrypted_bytes = self._encrypt_bytes(key1, key2, file_bytes, iv)
        encrypted_file_path = output_folder / f"{input_file_path.name}.double_des.enc"

        return self._save_encrypted_file(encrypted_file_path, encrypted_bytes)

    def decrypt(
        self,
        key1_path: Path,
        key2_path: Path,
        encrypted_file_path: Path,
        output_folder: Path | None = None,
    ) -> Path:
        """Decrypt a Double DES encrypted file and restore clean filename."""
        key1_path = Path(key1_path)
        key2_path = Path(key2_path)
        encrypted_file_path = Path(encrypted_file_path)
        output_folder = self._build_decryption_directory(self.KEY_DIRECTORY_PREFIX, output_folder)
        self._ensure_output_folder(output_folder)

        self._validate_file(encrypted_file_path, "Encrypted file")

        key1, key2 = self._load_keys(key1_path, key2_path)
        encrypted_bytes = self._read_file_bytes(encrypted_file_path)
        decrypted_bytes = self._decrypt_bytes(key1, key2, encrypted_bytes)

        clean_name = clean_decrypted_filename(encrypted_file_path.name, ".double_des.enc")
        decrypted_file_path = output_folder / clean_name

        return self._save_decrypted_file(decrypted_file_path, decrypted_bytes)

    def _derive_secondary_iv(self, iv: bytes, key2: bytes) -> bytes:
        """Derive an independent secondary IV for the second CBC pass to avoid IV reuse."""
        return hashlib.sha256(b"DDES-IV2:" + iv + key2).digest()[: self.BLOCK_SIZE_BYTES]

    def _load_keys(self, key1_path: Path, key2_path: Path) -> tuple[bytes, bytes]:
        key1 = self._load_key(key1_path)
        key2 = self._load_key(key2_path)
        self._validate_keys((key1, key2), self.KEY_COUNT)

        return key1, key2

    def _encrypt_bytes(
        self,
        key1: bytes,
        key2: bytes,
        file_bytes: bytes,
        iv: bytes | str | None = None,
    ) -> bytes:
        iv1 = self._resolve_iv(iv)
        iv2 = self._derive_secondary_iv(iv1, key2)
        padded_bytes = self._pad_bytes(file_bytes)
        first_pass = self._encrypt_with_key(key1, iv1, padded_bytes)
        second_pass = self._encrypt_with_key(key2, iv2, first_pass)

        return iv1 + second_pass

    def _decrypt_bytes(self, key1: bytes, key2: bytes, encrypted_bytes: bytes) -> bytes:
        iv1, ciphertext = self._split_iv_and_ciphertext(encrypted_bytes)
        iv2 = self._derive_secondary_iv(iv1, key2)
        first_pass = self._decrypt_with_key(key2, iv2, ciphertext)
        padded_bytes = self._decrypt_with_key(key1, iv1, first_pass)

        return self._unpad_bytes(padded_bytes)
