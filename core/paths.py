"""Centralized filesystem paths and directory management for Cipher AI."""

import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STORAGE_DIR = PROJECT_ROOT / "storage"
KEYS_DIR = STORAGE_DIR / "keys"
ENCRYPTED_DIR = STORAGE_DIR / "encrypted"
DECRYPTED_DIR = STORAGE_DIR / "decrypted"


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists and return it."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if not path.is_dir():
        raise ValueError(f"Output folder is not a directory: {path}")
    return path


def get_timestamped_directory(category: str, algorithm_name: str) -> Path:
    """Build and create a timestamped storage directory.

    Args:
        category: Subfolder under storage (e.g., 'keys', 'encrypted', 'decrypted').
        algorithm_name: Algorithm label (e.g., 'AES_256', 'RSA_2048', 'DOUBLE_DES').

    Returns:
        The created Path.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = STORAGE_DIR / category / f"{algorithm_name}_{timestamp}"
    ensure_directory(target)
    return target


def clean_decrypted_filename(filename: str, algorithm_suffix: str = "") -> str:
    """Clean the filename for decrypted output by stripping algorithm suffixes.

    Example:
        'document.pdf.aes.enc' -> 'decrypted_document.pdf'
        'data.csv.double_des.enc' -> 'decrypted_data.csv'
        'photo.jpg.enc' -> 'decrypted_photo.jpg'
    """
    name = filename
    if algorithm_suffix and name.endswith(algorithm_suffix):
        name = name[: -len(algorithm_suffix)]
    elif name.endswith(".enc"):
        name = name[: -len(".enc")]

    if not name.startswith("decrypted_"):
        name = f"decrypted_{name}"

    return name
