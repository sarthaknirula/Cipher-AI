"""RSA asymmetric encryption service supporting passphrase protection and hybrid file encryption."""

import datetime
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.paths import (
    PROJECT_ROOT,
    clean_decrypted_filename,
    ensure_directory,
    get_timestamped_directory,
    resolve_unique_path,
)


class RSAService:
    """Service providing RSA key generation, passphrase protection, and hybrid file encryption."""

    VALID_KEY_SIZES = (2048, 3072, 4096)
    HYBRID_MAGIC_HEADER = b"RSAHYBRID\x01"  # 10 bytes magic prefix for hybrid ciphertexts
    AES_KEY_SIZE_BYTES = 32
    GCM_NONCE_SIZE_BYTES = 12

    def generate_key_pair(
        self,
        key_length: int,
        save_directory: Path | None = None,
        passphrase: str | None = None,
    ) -> tuple[Path, Path]:
        """Generate RSA key pair with optional passphrase protection on the private key."""
        self._validate_key_size(key_length)
        if save_directory is None:
            save_directory = get_timestamped_directory("keys", f"RSA_{key_length}")
        else:
            save_directory = ensure_directory(Path(save_directory))

        private_key, public_key = self._generate_keys(key_length)
        private_ser = self._serialize_private_key(private_key, passphrase=passphrase)
        public_ser = self._serialize_public_key(public_key)

        private_key_path = self._save_key(save_directory / "private_key.pem", private_ser)
        public_key_path = self._save_key(save_directory / "public_key.pem", public_ser)

        return public_key_path, private_key_path

    def encrypt_file(
        self,
        public_key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
        hybrid: bool | None = None,
    ) -> Path:
        """Encrypt a file using RSA public key.

        If the file exceeds RSA OAEP plaintext size limits or hybrid=True, uses secure
        Hybrid Encryption (ephemeral AES-256-GCM session key encrypted with RSA OAEP).
        """
        public_key_path = Path(public_key_path)
        input_file_path = Path(input_file_path)
        output_folder = self._build_encryption_directory(output_folder)
        self._ensure_output_folder(output_folder)

        self._validate_input_file(public_key_path, "Public key")
        self._validate_input_file(input_file_path, "Input file")

        public_key = self._load_public_key(public_key_path)
        file_bytes = self._read_file_bytes(input_file_path)

        # Determine whether to use hybrid encryption
        max_oaep_size = self._max_oaep_plaintext_size(public_key)
        use_hybrid = hybrid if hybrid is not None else (len(file_bytes) > max_oaep_size)

        if use_hybrid:
            encrypted_bytes = self._encrypt_bytes_hybrid(public_key, file_bytes)
        else:
            encrypted_bytes = self._encrypt_bytes(public_key, file_bytes)

        encrypted_file_path = output_folder / f"{input_file_path.name}.enc"
        return self._save_encrypted_file(encrypted_file_path, encrypted_bytes)

    def decrypt_file(
        self,
        private_key_path: Path,
        encrypted_file_path: Path,
        output_folder: Path | None = None,
        passphrase: str | None = None,
    ) -> Path:
        """Decrypt an RSA encrypted file (supports both direct RSA and Hybrid AES-GCM)."""
        private_key_path = Path(private_key_path)
        encrypted_file_path = Path(encrypted_file_path)
        output_folder = self._build_decryption_directory(output_folder)
        self._ensure_output_folder(output_folder)

        self._validate_input_file(private_key_path, "Private key")
        self._validate_input_file(encrypted_file_path, "Encrypted file")

        private_key = self._load_private_key(private_key_path, passphrase=passphrase)
        encrypted_bytes = self._read_file_bytes(encrypted_file_path)

        if encrypted_bytes.startswith(self.HYBRID_MAGIC_HEADER):
            decrypted_bytes = self._decrypt_bytes_hybrid(private_key, encrypted_bytes)
        else:
            decrypted_bytes = self._decrypt_bytes(private_key, encrypted_bytes)

        clean_name = clean_decrypted_filename(encrypted_file_path.name, ".enc")
        decrypted_file_path = output_folder / clean_name

        return self._save_decrypted_file(decrypted_file_path, decrypted_bytes)

    # Hybrid RSA + AES-GCM Operations
    def encrypt_hybrid(
        self,
        public_key_path: Path,
        input_file_path: Path,
        output_folder: Path | None = None,
    ) -> Path:
        """Convenience method to explicitly perform hybrid RSA+AES-GCM encryption."""
        return self.encrypt_file(public_key_path, input_file_path, output_folder, hybrid=True)

    def decrypt_hybrid(
        self,
        private_key_path: Path,
        encrypted_file_path: Path,
        output_folder: Path | None = None,
        passphrase: str | None = None,
    ) -> Path:
        """Convenience method to decrypt hybrid encrypted files."""
        return self.decrypt_file(private_key_path, encrypted_file_path, output_folder, passphrase=passphrase)

    def _encrypt_bytes_hybrid(self, public_key: RSAPublicKey, file_bytes: bytes) -> bytes:
        aes_key = os.urandom(self.AES_KEY_SIZE_BYTES)
        nonce = os.urandom(self.GCM_NONCE_SIZE_BYTES)

        aesgcm = AESGCM(aes_key)
        ciphertext = aesgcm.encrypt(nonce, file_bytes, None)

        enc_aes_key = self._encrypt_bytes(public_key, aes_key)
        key_len = len(enc_aes_key).to_bytes(2, "big")

        return self.HYBRID_MAGIC_HEADER + key_len + enc_aes_key + nonce + ciphertext

    def _decrypt_bytes_hybrid(self, private_key: RSAPrivateKey, payload: bytes) -> bytes:
        header_len = len(self.HYBRID_MAGIC_HEADER)
        if len(payload) < header_len + 2:
            raise ValueError("Corrupted hybrid RSA payload.")

        key_len = int.from_bytes(payload[header_len : header_len + 2], "big")
        start = header_len + 2
        enc_aes_key = payload[start : start + key_len]
        nonce_start = start + key_len
        nonce = payload[nonce_start : nonce_start + self.GCM_NONCE_SIZE_BYTES]
        ciphertext = payload[nonce_start + self.GCM_NONCE_SIZE_BYTES :]

        aes_key = self._decrypt_bytes(private_key, enc_aes_key)
        aesgcm = AESGCM(aes_key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    # Core RSA Primitives
    def _validate_key_size(self, key_length: int) -> None:
        if key_length not in self.VALID_KEY_SIZES:
            raise ValueError(
                f"Invalid key size {key_length}. Key size must be 2048, 3072, or 4096."
            )

    def _validate_input_file(self, file_path: Path, file_label: str) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_label} not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"{file_label} is not a file: {file_path}")

    def _build_encryption_directory(self, output_folder: Path | None) -> Path:
        if output_folder is not None:
            return ensure_directory(Path(output_folder))
        return get_timestamped_directory("encrypted", "RSA")

    def _build_decryption_directory(self, output_folder: Path | None) -> Path:
        if output_folder is not None:
            return ensure_directory(Path(output_folder))
        return get_timestamped_directory("decrypted", "RSA")

    def _ensure_output_folder(self, output_folder: Path) -> None:
        ensure_directory(output_folder)

    def _generate_keys(self, key_length: int, public_exponent: int = 65537) -> tuple[RSAPrivateKey, RSAPublicKey]:
        private_key = rsa.generate_private_key(
            public_exponent=public_exponent,
            key_size=key_length,
        )
        return private_key, private_key.public_key()

    def _serialize_private_key(self, private_key: RSAPrivateKey, passphrase: str | None = None) -> bytes:
        if passphrase:
            enc_algorithm = serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
        else:
            enc_algorithm = serialization.NoEncryption()

        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=enc_algorithm,
        )

    def _serialize_public_key(self, public_key: RSAPublicKey) -> bytes:
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def _load_public_key(self, public_key_path: Path) -> RSAPublicKey:
        key = serialization.load_pem_public_key(self._read_file_bytes(public_key_path))
        if not isinstance(key, RSAPublicKey):
            raise ValueError("Invalid RSA public key.")
        return key

    def _load_private_key(self, private_key_path: Path, passphrase: str | None = None) -> RSAPrivateKey:
        key_bytes = self._read_file_bytes(private_key_path)
        password_bytes = passphrase.encode("utf-8") if passphrase else None
        try:
            key = serialization.load_pem_private_key(key_bytes, password=password_bytes)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Failed to decrypt private key. Passphrase may be missing, incorrect, or key is corrupted."
            ) from exc

        if not isinstance(key, RSAPrivateKey):
            raise ValueError("Invalid RSA private key.")
        return key

    def _read_file_bytes(self, file_path: Path) -> bytes:
        return file_path.read_bytes()

    def _max_oaep_plaintext_size(self, public_key: RSAPublicKey) -> int:
        hash_size = hashes.SHA256().digest_size
        return (public_key.key_size // 8) - (2 * hash_size) - 2

    def _validate_plaintext_size(self, public_key: RSAPublicKey, file_bytes: bytes) -> None:
        max_size = self._max_oaep_plaintext_size(public_key)
        if len(file_bytes) > max_size:
            raise ValueError(
                f"Input file is too large for direct RSA OAEP encryption. "
                f"Maximum size for this key is {max_size} bytes. Use hybrid encryption for large files."
            )

    def _encrypt_bytes(self, public_key: RSAPublicKey, file_bytes: bytes) -> bytes:
        return public_key.encrypt(
            file_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def _decrypt_bytes(self, private_key: RSAPrivateKey, encrypted_bytes: bytes) -> bytes:
        return private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

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
