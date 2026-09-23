from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives import hashes, serialization
import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RSAService() :
    VALID_KEY_SIZES = (2048,3072,4096)
    def generate_key_pair(self,key_length : int , save_directory : Path | None = None) -> tuple[Path, Path] :
        self._validate_key_size(key_length)
        if save_directory is None:
            save_directory = PROJECT_ROOT / "storage" / "keys" / f"RSA_{key_length}" / datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        else:
            save_directory = Path(save_directory)

        save_directory.mkdir(parents=True, exist_ok=True)

        private_key, public_key = self._generate_keys(key_length)
        private_ser = self._serialize_private_key(private_key)
        public_ser = self._serialize_public_key(public_key)
        private_key_path = self._save_key(save_directory/ "private_key.pem" , private_ser)
        public_key_path = self._save_key(save_directory / "public_key.pem", public_ser)

        return public_key_path, private_key_path

    def encrypt_file(self, public_key_path: Path, input_file_path: Path, output_folder: Path) -> Path:
        public_key_path = Path(public_key_path)
        input_file_path = Path(input_file_path)
        output_folder = Path(output_folder)

        self._validate_input_file(public_key_path, "Public key")
        self._validate_input_file(input_file_path, "Input file")
        self._ensure_output_folder(output_folder)

        public_key = self._load_public_key(public_key_path)
        file_bytes = self._read_file_bytes(input_file_path)
        self._validate_plaintext_size(public_key, file_bytes)
        encrypted_bytes = self._encrypt_bytes(public_key, file_bytes)
        encrypted_file_path = output_folder / f"{input_file_path.name}.enc"

        return self._save_encrypted_file(encrypted_file_path, encrypted_bytes)

    def decrypt_file(self, private_key_path: Path, encrypted_file_path: Path, output_folder: Path) -> Path:
        private_key_path = Path(private_key_path)
        encrypted_file_path = Path(encrypted_file_path)
        output_folder = Path(output_folder)

        self._validate_input_file(private_key_path, "Private key")
        self._validate_input_file(encrypted_file_path, "Encrypted file")
        self._ensure_output_folder(output_folder)

        private_key = self._load_private_key(private_key_path)
        encrypted_bytes = self._read_file_bytes(encrypted_file_path)
        decrypted_bytes = self._decrypt_bytes(private_key, encrypted_bytes)
        decrypted_file_path = output_folder / f"decrypted_{encrypted_file_path.name}"

        return self._save_decrypted_file(decrypted_file_path, decrypted_bytes)


    def _validate_key_size(self,key_length : int) -> None: 
        if key_length not in RSAService.VALID_KEY_SIZES :
            raise ValueError(f'Invalid key size {key_length}. Key size must be 2048 or 3072 or 4096.')

    def _validate_input_file(self, file_path: Path, file_label: str) -> None:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_label} not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"{file_label} is not a file: {file_path}")

    def _ensure_output_folder(self, output_folder: Path) -> None:
        output_folder.mkdir(parents=True, exist_ok=True)
        if not output_folder.is_dir():
            raise ValueError(f"Output folder is not a directory: {output_folder}")
        
    def _generate_keys(self,key_length : int , public_exponent = 65537) :
        private_key = rsa.generate_private_key(public_exponent=public_exponent,key_size=key_length)
        public_key = private_key.public_key()

        return (private_key,public_key)
    
    def _serialize_private_key(self,private_key) -> bytes :
        private_ser = private_key.private_bytes(encoding = serialization.Encoding.PEM,
                                                format = serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm = serialization.NoEncryption())
        
        return private_ser
    
    def _serialize_public_key(self,public_key) -> bytes:
        public_ser = public_key.public_bytes(encoding = serialization.Encoding.PEM,
                                             format = serialization.PublicFormat.SubjectPublicKeyInfo)

        return public_ser

    def _load_public_key(self, public_key_path: Path) -> RSAPublicKey:
        key = serialization.load_pem_public_key(self._read_file_bytes(public_key_path))
        if not isinstance(key, RSAPublicKey):
            raise ValueError("Invalid RSA public key.")

        return key

    def _load_private_key(self, private_key_path: Path) -> RSAPrivateKey:
        key = serialization.load_pem_private_key(
            self._read_file_bytes(private_key_path),
            password=None,
        )
        if not isinstance(key, RSAPrivateKey):
            raise ValueError("Invalid RSA private key.")

        return key

    def _read_file_bytes(self, file_path: Path) -> bytes:
        return file_path.read_bytes()

    def _validate_plaintext_size(self, public_key: RSAPublicKey, file_bytes: bytes) -> None:
        hash_size = hashes.SHA256().digest_size
        max_size = (public_key.key_size // 8) - (2 * hash_size) - 2
        if len(file_bytes) > max_size:
            raise ValueError(
                f"Input file is too large for RSA OAEP encryption. "
                f"Maximum size for this key is {max_size} bytes."
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
    
    def _save_key(self, file_path : Path , key_bytes : bytes) -> Path:
        with file_path.open('wb') as f:
            f.write(key_bytes)
            
        return file_path

    def _save_encrypted_file(self, file_path: Path, encrypted_bytes: bytes) -> Path:
        file_path.write_bytes(encrypted_bytes)

        return file_path

    def _save_decrypted_file(self, file_path: Path, decrypted_bytes: bytes) -> Path:
        file_path.write_bytes(decrypted_bytes)

        return file_path

        
