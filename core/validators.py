"""Shared validation helpers for crypto services."""


IV_HEX_ERROR = "The IV must contain only hexadecimal characters."
IV_LENGTH_ERROR = "The IV must be exactly 16 bytes (32 hexadecimal characters)."


def validate_iv(iv: bytes | str, expected_byte_length: int = 16) -> bytes:
    """Return a validated IV as bytes."""
    if isinstance(iv, bytes):
        _validate_iv_length(iv, expected_byte_length)
        return iv

    if not isinstance(iv, str):
        raise TypeError("IV must be bytes or text.")

    trimmed_iv = iv.strip()
    try:
        iv_bytes = bytes.fromhex(trimmed_iv)
    except ValueError as exc:
        raise ValueError(IV_HEX_ERROR) from exc

    _validate_iv_length(iv_bytes, expected_byte_length)
    return iv_bytes


def _validate_iv_length(iv: bytes, expected_byte_length: int) -> None:
    if len(iv) != expected_byte_length:
        if expected_byte_length == 16:
            raise ValueError(IV_LENGTH_ERROR)

        hex_characters = expected_byte_length * 2
        raise ValueError(
            f"The IV must be exactly {expected_byte_length} bytes "
            f"({hex_characters} hexadecimal characters)."
        )
