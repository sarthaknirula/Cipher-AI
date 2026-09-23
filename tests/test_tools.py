"""Tests for AI tool adapters."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from ai.tools.aes_tool import AESTool
from ai.tools.double_des_tool import DoubleDESTool
from ai.tools.rsa_tool import RSATool
from ai.tools.triple_des_tool import TripleDESTool
from ai.tools.validation import ToolValidationClarification


class ToolAdapterTests(unittest.TestCase):
    """Verify AI tools dispatch operations to crypto services."""

    def test_unsupported_operation_raises_value_error(self) -> None:
        """Unsupported operations should fail before calling a service."""
        tool = AESTool()

        with self.assertRaisesRegex(ValueError, "Unsupported operation: rotate"):
            tool.execute("rotate", {})

    def test_aes_encrypt_dispatches_to_service(self) -> None:
        """AES encrypt should call AESService.encrypt."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key_path = temp_path / "aes.key"
            input_path = temp_path / "plain.txt"
            output_folder = temp_path / "out"
            key_path.write_bytes(b"0" * 16)
            input_path.write_text("plain")
            output_folder.mkdir()

            tool = AESTool()
            tool.service.encrypt = Mock(return_value="encrypted")
            arguments = {
                "key_path": key_path,
                "input_file_path": input_path,
                "output_folder": output_folder,
            }

            result = tool.execute("encrypt", arguments)

            self.assertEqual(result, "encrypted")
            tool.service.encrypt.assert_called_once_with(**arguments)

    def test_aes_decrypt_dispatches_to_service(self) -> None:
        """AES decrypt should call AESService.decrypt."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key_path = temp_path / "aes.key"
            input_path = temp_path / "plain.txt.aes.enc"
            output_folder = temp_path / "out"
            key_path.write_bytes(b"0" * 16)
            input_path.write_bytes(b"encrypted")
            output_folder.mkdir()

            tool = AESTool()
            tool.service.decrypt = Mock(return_value="decrypted")
            arguments = {
                "key_path": key_path,
                "input_file_path": input_path,
                "output_folder": output_folder,
            }

            result = tool.execute("decrypt", arguments)

            self.assertEqual(result, "decrypted")
            tool.service.decrypt.assert_called_once_with(**arguments)

    def test_aes_encrypt_invalid_output_folder_asks_for_clarification(self) -> None:
        """Invalid explicit output folders should pause before encryption."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key_path = temp_path / "aes.key"
            input_path = temp_path / "plain.txt"
            missing_output = temp_path / "missing"
            key_path.write_bytes(b"0" * 16)
            input_path.write_text("plain")

            tool = AESTool()
            tool.service.encrypt = Mock(return_value="encrypted")
            arguments = {
                "key_path": key_path,
                "input_file_path": input_path,
                "output_folder": missing_output,
            }

            with self.assertRaises(ToolValidationClarification) as context:
                tool.execute("encrypt", arguments)

            self.assertIn("does not exist", context.exception.question)
            self.assertIn(str(missing_output), context.exception.question)
            self.assertIn(
                "default application output directory",
                context.exception.question,
            )
            tool.service.encrypt.assert_not_called()

    def test_aes_encrypt_missing_input_file_asks_for_clarification(self) -> None:
        """Missing required files should pause before encryption."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key_path = temp_path / "aes.key"
            missing_input = temp_path / "plain.txt"
            output_folder = temp_path / "out"
            key_path.write_bytes(b"0" * 16)
            output_folder.mkdir()

            tool = AESTool()
            tool.service.encrypt = Mock(return_value="encrypted")
            arguments = {
                "key_path": key_path,
                "input_file_path": missing_input,
                "output_folder": output_folder,
            }

            with self.assertRaises(ToolValidationClarification) as context:
                tool.execute("encrypt", arguments)

            self.assertIn("input file does not exist", context.exception.question)
            self.assertIn(str(missing_input), context.exception.question)
            tool.service.encrypt.assert_not_called()

    def test_rsa_generate_key_pair_dispatches_to_service(self) -> None:
        """RSA generate_key_pair should call RSAService.generate_key_pair."""
        with TemporaryDirectory() as temp_dir:
            save_directory = Path(temp_dir)
            tool = RSATool()
            tool.service.generate_key_pair = Mock(
                return_value=("public.pem", "private.pem")
            )
            arguments = {"key_length": 4096, "save_directory": save_directory}

            result = tool.execute("generate_key", arguments)

            self.assertEqual(result, ("public.pem", "private.pem"))
            tool.service.generate_key_pair.assert_called_once_with(**arguments)

    def test_double_des_encrypt_dispatches_to_service(self) -> None:
        """Double DES encrypt should call DoubleDESService.encrypt."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key1_path = temp_path / "key1.key"
            key2_path = temp_path / "key2.key"
            input_path = temp_path / "plain.txt"
            output_folder = temp_path / "out"
            key1_path.write_bytes(b"1" * 8)
            key2_path.write_bytes(b"2" * 8)
            input_path.write_text("plain")
            output_folder.mkdir()

            tool = DoubleDESTool()
            tool.service.encrypt = Mock(return_value="double-des-encrypted")
            arguments = {
                "key1_path": key1_path,
                "key2_path": key2_path,
                "input_file_path": input_path,
                "output_folder": output_folder,
            }

            result = tool.execute("encrypt", arguments)

            self.assertEqual(result, "double-des-encrypted")
            tool.service.encrypt.assert_called_once_with(**arguments)

    def test_triple_des_decrypt_dispatches_to_service(self) -> None:
        """Triple DES decrypt should call TripleDESService.decrypt."""
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            key1_path = temp_path / "key1.key"
            key2_path = temp_path / "key2.key"
            key3_path = temp_path / "key3.key"
            encrypted_path = temp_path / "plain.txt.triple_des.enc"
            output_folder = temp_path / "out"
            key1_path.write_bytes(b"1" * 8)
            key2_path.write_bytes(b"2" * 8)
            key3_path.write_bytes(b"3" * 8)
            encrypted_path.write_bytes(b"encrypted")
            output_folder.mkdir()

            tool = TripleDESTool()
            tool.service.decrypt = Mock(return_value="triple-des-decrypted")
            arguments = {
                "key1_path": key1_path,
                "key2_path": key2_path,
                "key3_path": key3_path,
                "encrypted_file_path": encrypted_path,
                "output_folder": output_folder,
            }

            result = tool.execute("decrypt", arguments)

            self.assertEqual(result, "triple-des-decrypted")
            tool.service.decrypt.assert_called_once_with(**arguments)


if __name__ == "__main__":
    unittest.main()
