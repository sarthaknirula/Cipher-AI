"""Tests for shared IV validation."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.validators import IV_HEX_ERROR, IV_LENGTH_ERROR, validate_iv
from crypto.aes import AESService
from crypto.double_des import DoubleDESService
from crypto.triple_des import TripleDESService


class IVValidationTests(unittest.TestCase):
    """Verify hex IV parsing is centralized and byte-length based."""

    VALID_AES_IVS = (
        "2370dc78519f8d6ee2cf7f40348662c0",
        "a657d396355b717d9ec55d3d308baa0d",
        "00000000000000000000000000000000",
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
    )

    INVALID_HEX_IVS = ("2370dc78519f8d6ee2cf7f40348662cg",)

    INVALID_LENGTH_IVS = (
        "2370dc78519f8d6ee2cf7f40348662",
        "2370dc78519f8d6ee2cf7f40348662c011",
        "",
        "      ",
    )

    def test_validate_iv_accepts_valid_16_byte_hex_strings(self) -> None:
        """Valid 32-character hex strings should decode to 16 IV bytes."""
        for iv in self.VALID_AES_IVS:
            with self.subTest(iv=iv):
                self.assertEqual(validate_iv(iv), bytes.fromhex(iv))

    def test_validate_iv_trims_whitespace(self) -> None:
        """Leading and trailing whitespace should not invalidate an IV."""
        iv = "  2370dc78519f8d6ee2cf7f40348662c0\n"

        self.assertEqual(validate_iv(iv), bytes.fromhex(iv.strip()))

    def test_validate_iv_rejects_non_hex_values(self) -> None:
        """Non-hex IVs should receive the required hex error message."""
        for iv in self.INVALID_HEX_IVS:
            with self.subTest(iv=iv):
                with self.assertRaises(ValueError) as context:
                    validate_iv(iv)
                self.assertEqual(str(context.exception), IV_HEX_ERROR)

    def test_validate_iv_rejects_wrong_decoded_length(self) -> None:
        """IV length should be checked after hexadecimal decoding."""
        for iv in self.INVALID_LENGTH_IVS:
            with self.subTest(iv=iv):
                with self.assertRaises(ValueError) as context:
                    validate_iv(iv)
                self.assertEqual(str(context.exception), IV_LENGTH_ERROR)

    def test_aes_encryption_accepts_valid_hex_iv(self) -> None:
        """AES encryption should accept a 32-character hex IV."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key_path = temp_path / "aes.key"
            input_path = temp_path / "plain.txt"
            output_folder = temp_path / "out"
            key_path.write_bytes(b"0" * 16)
            input_path.write_text("plain")

            result = AESService().encrypt(
                key_path,
                input_path,
                output_folder,
                iv=self.VALID_AES_IVS[0],
            )

            self.assertTrue(result.exists())

    def test_double_des_encryption_accepts_valid_hex_iv(self) -> None:
        """Double DES should accept a decoded 8-byte IV for its block size."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key1_path = temp_path / "key1.key"
            key2_path = temp_path / "key2.key"
            input_path = temp_path / "plain.txt"
            output_folder = temp_path / "out"
            key1_path.write_bytes(b"1" * 8)
            key2_path.write_bytes(b"2" * 8)
            input_path.write_text("plain")

            result = DoubleDESService().encrypt(
                key1_path,
                key2_path,
                input_path,
                output_folder,
                iv="2370dc78519f8d6e",
            )

            self.assertTrue(result.exists())

    def test_triple_des_encryption_accepts_valid_hex_iv(self) -> None:
        """Triple DES should accept a decoded 8-byte IV for its block size."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key1_path = temp_path / "key1.key"
            key2_path = temp_path / "key2.key"
            key3_path = temp_path / "key3.key"
            input_path = temp_path / "plain.txt"
            output_folder = temp_path / "out"
            key1_path.write_bytes(b"1" * 8)
            key2_path.write_bytes(b"2" * 8)
            key3_path.write_bytes(b"3" * 8)
            input_path.write_text("plain")

            result = TripleDESService().encrypt(
                key1_path,
                key2_path,
                key3_path,
                input_path,
                output_folder,
                iv="2370dc78519f8d6e",
            )

            self.assertTrue(result.exists())


if __name__ == "__main__":
    unittest.main()
