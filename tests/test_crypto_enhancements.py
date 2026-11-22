"""Tests for newly implemented cryptographic enhancements (Items 1, 2, 3, 5, 6, 7, 8, 9)."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtWidgets import QApplication, QPushButton

APP = QApplication.instance() or QApplication(sys.argv)

from core.paths import clean_decrypted_filename, get_timestamped_directory
from crypto.aes import AESService
from crypto.double_des import DoubleDESService
from crypto.hashing import HashingService, generate_hmac, hash_bytes, hash_file, verify_hmac
from crypto.rsa import RSAService
from crypto.triple_des import TripleDESService
from gui.pages.aes import AESPage
from gui.pages.home import MessageBubble, ToolResultCard
from gui.pages.rsa import RSAPage


class CryptoEnhancementsTests(unittest.TestCase):
    """Verify enhancements across AES-GCM, RSA passphrase/hybrid, Double DES, hashing, and filename cleaning."""

    # Item 9: Hashing & HMAC
    def test_hashing_bytes_and_file(self) -> None:
        """Hashing service computes valid digests for bytes and files."""
        hasher = HashingService()
        data = b"Cipher AI Cryptographic Test Data"
        digest_bytes = hasher.hash_bytes(data, "sha256")
        self.assertEqual(len(digest_bytes), 64)

        with TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "test.bin"
            test_file.write_bytes(data)
            digest_file = hasher.hash_file(test_file, "sha256")
            self.assertEqual(digest_bytes, digest_file)

    def test_hmac_generation_and_verification(self) -> None:
        """HMAC generation and constant-time verification."""
        key = b"super-secret-hmac-key"
        data = b"Critical Message That Must Not Be Tampered"
        mac = generate_hmac(key, data, "sha256")
        self.assertTrue(verify_hmac(key, data, mac, "sha256"))
        self.assertFalse(verify_hmac(key, b"Tampered Message", mac, "sha256"))
        self.assertFalse(verify_hmac(b"wrong-key", data, mac, "sha256"))

    # Item 1: AES-GCM (Authenticated Encryption)
    def test_aes_gcm_encryption_and_decryption(self) -> None:
        """AES-GCM encrypts with AEAD and decrypts accurately."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            service = AESService()
            key_path = service.generate_key(256, tmp_path)
            input_file = tmp_path / "plain.txt"
            content = "Confidential GCM Authenticated Payload"
            input_file.write_text(content)

            enc_path = service.encrypt_gcm(key_path, input_file, tmp_path / "enc")
            self.assertTrue(enc_path.exists())

            dec_path = service.decrypt(key_path, enc_path, tmp_path / "dec")
            self.assertTrue(dec_path.exists())
            self.assertEqual(dec_path.read_text(), content)
            self.assertEqual(dec_path.name, "decrypted_plain.txt")

    def test_aes_gcm_detects_ciphertext_tampering(self) -> None:
        """Tampering with an AES-GCM encrypted file must raise authentication failure."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            service = AESService()
            key_path = service.generate_key(256, tmp_path)
            input_file = tmp_path / "plain.txt"
            input_file.write_text("Secret Data")

            enc_path = service.encrypt_gcm(key_path, input_file, tmp_path / "enc")
            # Flip bits in ciphertext
            raw = bytearray(enc_path.read_bytes())
            raw[-1] ^= 0xFF
            enc_path.write_bytes(bytes(raw))

            with self.assertRaises(ValueError) as ctx:
                service.decrypt(key_path, enc_path, tmp_path / "dec")
            self.assertIn("Authentication failed", str(ctx.exception))

    # Item 8: Chunked / Streaming File Processing
    def test_aes_streaming_encryption(self) -> None:
        """AES streaming handles large content without corruption."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            service = AESService()
            key_path = service.generate_key(256, tmp_path)
            input_file = tmp_path / "data.bin"
            large_content = b"StreamBlockTest!" * 4096  # 64 KB
            input_file.write_bytes(large_content)

            # Test stream CBC directly
            enc_file = tmp_path / "stream.enc"
            dec_file = tmp_path / "decrypted_stream.bin"
            iv = service._generate_iv()
            service._encrypt_stream_cbc(service._load_key(key_path), iv, input_file, enc_file)
            self.assertTrue(enc_file.exists())

            # Decrypt and verify match
            dec_path = service.decrypt(key_path, enc_file, tmp_path / "dec")
            self.assertEqual(dec_path.read_bytes(), large_content)

    # Item 2: RSA Private Key Passphrase Protection
    def test_rsa_passphrase_protected_key(self) -> None:
        """RSA private key protected with passphrase decrypts with password and rejects wrong password."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            service = RSAService()
            passphrase = "UltraSecurePassword123!"

            pub_path, priv_path = service.generate_key_pair(2048, tmp_path, passphrase=passphrase)
            priv_bytes = priv_path.read_bytes()
            # Encrypted PKCS#8 private keys have ENCRYPTED PRIVATE KEY header
            self.assertIn(b"ENCRYPTED PRIVATE KEY", priv_bytes)

            input_file = tmp_path / "message.txt"
            content = "Passphrase Test Message"
            input_file.write_text(content)

            enc_path = service.encrypt_file(pub_path, input_file, tmp_path / "enc")

            # Decrypt with correct passphrase
            dec_path = service.decrypt_file(priv_path, enc_path, tmp_path / "dec", passphrase=passphrase)
            self.assertEqual(dec_path.read_text(), content)

            # Decrypt with incorrect passphrase must fail
            with self.assertRaises(ValueError) as ctx:
                service.decrypt_file(priv_path, enc_path, tmp_path / "dec2", passphrase="WrongPassword")
            self.assertIn("Failed to decrypt private key", str(ctx.exception))

    # Item 3: Hybrid RSA + AES-GCM Encryption for Large Files
    def test_rsa_hybrid_encryption_large_file(self) -> None:
        """RSA Hybrid encryption seamlessly encrypts files far larger than RSA key OAEP limit."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            service = RSAService()
            pub_path, priv_path = service.generate_key_pair(2048, tmp_path, passphrase="hybrid_passphrase")

            input_file = tmp_path / "large_document.txt"
            # 2048-bit RSA OAEP max plaintext is ~190 bytes. We encrypt 20,000 bytes.
            large_content = "This is a large document encrypted via Hybrid RSA-AES " * 400
            input_file.write_text(large_content)

            # encrypt_file automatically falls back to hybrid when payload > max_oaep_size
            enc_path = service.encrypt_file(pub_path, input_file, tmp_path / "enc")
            self.assertTrue(enc_path.exists())

            dec_path = service.decrypt_file(priv_path, enc_path, tmp_path / "dec", passphrase="hybrid_passphrase")
            self.assertTrue(dec_path.exists())
            self.assertEqual(dec_path.read_text(), large_content)
            self.assertEqual(dec_path.name, "decrypted_large_document.txt")

    def test_rsa_generate_key_pair_requires_passphrase(self) -> None:
        """Generating RSA key pair without passphrase or with empty passphrase must raise ValueError."""
        service = RSAService()
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with self.assertRaises(ValueError) as ctx:
                service.generate_key_pair(2048, tmp_path, passphrase=None)
            self.assertIn("Passphrase is required", str(ctx.exception))

            with self.assertRaises(ValueError) as ctx2:
                service.generate_key_pair(2048, tmp_path, passphrase="   ")
            self.assertIn("Passphrase is required", str(ctx2.exception))

    # Item 5: Double DES Cascade & Secondary IV
    def test_double_des_independent_iv(self) -> None:
        """Double DES uses secondary derived IV to avoid IV reuse across passes."""
        service = DoubleDESService()
        iv = b"12345678"
        k2 = b"abcdefgh"
        derived_iv = service._derive_secondary_iv(iv, k2)
        self.assertEqual(len(derived_iv), 8)
        self.assertNotEqual(derived_iv, iv)
        # Docstring check for MitM explanation
        self.assertIn("Meet-in-the-Middle", DoubleDESService.__doc__)

    # Item 6: Decrypted Filename Cleanup
    def test_cleaned_decrypted_filenames(self) -> None:
        """Decrypted files have .enc suffixes stripped and original extensions preserved."""
        self.assertEqual(clean_decrypted_filename("file.txt.aes.enc", ".aes.enc"), "decrypted_file.txt")
        self.assertEqual(
            clean_decrypted_filename("document.pdf.double_des.enc", ".double_des.enc"),
            "decrypted_document.pdf",
        )
        self.assertEqual(
            clean_decrypted_filename("archive.tar.triple_des.enc", ".triple_des.enc"),
            "decrypted_archive.tar",
        )
        self.assertEqual(clean_decrypted_filename("photo.jpg.enc", ".enc"), "decrypted_photo.jpg")
        self.assertEqual(clean_decrypted_filename("sample.csv"), "decrypted_sample.csv")

    # Item 7: Default Output Folders
    def test_default_output_folders(self) -> None:
        """Crypto services accept output_folder=None and generate timestamped output."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            service_ddes = DoubleDESService()
            k1, k2 = service_ddes.generate_key(tmp_path)
            input_file = tmp_path / "note.txt"
            input_file.write_text("Default Folder Test")

            enc_path = service_ddes.encrypt(k1, k2, input_file, output_folder=None)
            self.assertTrue(enc_path.exists())
            self.assertIn("storage", str(enc_path))

    # GUI Enhancements: AI Assistant Copy Symbol & Service Page Controls
    def test_chat_copy_symbol_button(self) -> None:
        """AI Assistant message bubble uses a clear copy symbol '📋' instead of 'Copy'."""
        bubble = MessageBubble("assistant", "Testing assistant message")
        copy_btn = bubble.findChild(QPushButton, "copySymbolButton")
        self.assertIsNotNone(copy_btn, "MessageBubble must contain a copySymbolButton")
        self.assertEqual(copy_btn.text(), "📋")
        self.assertNotEqual(copy_btn.text(), "Copy")

        card = ToolResultCard("Operation Completed", [("Output Path", "/storage/keys/key1.key")])
        card_copy_btn = card.findChild(QPushButton, "copySymbolButton")
        self.assertIsNotNone(card_copy_btn, "ToolResultCard must contain a copySymbolButton")
        self.assertEqual(card_copy_btn.text(), "📋")

    def test_aes_gui_mode_selector(self) -> None:
        """AES page provides CBC and GCM mode selection with GCM as default."""
        page = AESPage()
        self.assertTrue(hasattr(page, "enc_mode_selector"))
        self.assertIn("GCM", page.enc_mode_selector.current_value())
        # Toggle to CBC
        page._on_mode_changed("CBC (Standard)")
        self.assertIn("16-byte", page.enc_iv_input.placeholderText())
        # Toggle to GCM
        page._on_mode_changed("GCM (AEAD)")
        self.assertIn("12-byte", page.enc_iv_input.placeholderText())

    def test_rsa_gui_passphrase_fields(self) -> None:
        """RSA page provides passphrase input for key generation and decryption with visibility toggling."""
        page = RSAPage()
        self.assertTrue(hasattr(page, "key_passphrase_input"))
        self.assertTrue(hasattr(page, "dec_passphrase_input"))
        self.assertEqual(page.key_passphrase_input.echoMode(), page.key_passphrase_input.EchoMode.Password)
        self.assertEqual(page.dec_passphrase_input.echoMode(), page.dec_passphrase_input.EchoMode.Password)
        self.assertFalse(page.key_passphrase_input.is_password_visible())
        self.assertFalse(page.dec_passphrase_input.is_password_visible())

        # Toggle visibility on key generation passphrase input
        page.key_passphrase_input.toggle_visibility()
        self.assertEqual(page.key_passphrase_input.echoMode(), page.key_passphrase_input.EchoMode.Normal)
        self.assertTrue(page.key_passphrase_input.is_password_visible())

        page.key_passphrase_input.toggle_visibility()
        self.assertEqual(page.key_passphrase_input.echoMode(), page.key_passphrase_input.EchoMode.Password)
        self.assertFalse(page.key_passphrase_input.is_password_visible())

        # Toggle visibility on decryption passphrase input
        page.dec_passphrase_input.toggle_visibility()
        self.assertEqual(page.dec_passphrase_input.echoMode(), page.dec_passphrase_input.EchoMode.Normal)
        self.assertTrue(page.dec_passphrase_input.is_password_visible())

        page.dec_passphrase_input.toggle_visibility()
        self.assertEqual(page.dec_passphrase_input.echoMode(), page.dec_passphrase_input.EchoMode.Password)
        self.assertFalse(page.dec_passphrase_input.is_password_visible())

    def test_password_line_edit_trailing_action(self) -> None:
        """PasswordLineEdit trailing action triggers visibility toggle and updates tooltip."""
        from gui.components import PasswordLineEdit
        le = PasswordLineEdit("Test placeholder")
        self.assertEqual(le.echoMode(), le.EchoMode.Password)
        self.assertEqual(le._toggle_action.toolTip(), "Show passphrase")

        # Trigger via action click
        le._toggle_action.trigger()
        self.assertEqual(le.echoMode(), le.EchoMode.Normal)
        self.assertTrue(le.is_password_visible())
        self.assertEqual(le._toggle_action.toolTip(), "Hide passphrase")

        # Trigger again
        le._toggle_action.trigger()
        self.assertEqual(le.echoMode(), le.EchoMode.Password)
        self.assertFalse(le.is_password_visible())
        self.assertEqual(le._toggle_action.toolTip(), "Show passphrase")

    def test_task_bridge_main_thread_execution(self) -> None:
        """TaskBridge guarantees callbacks and widget updates execute strictly on the main thread."""
        from PySide6.QtCore import QThread
        from PySide6.QtWidgets import QApplication, QLabel
        from gui.components import CryptoTaskWorker, TaskBridge

        app = QApplication.instance()
        self.assertIsNotNone(app)

        test_label = QLabel("Initial")
        test_label.setTextInteractionFlags(test_label.textInteractionFlags().TextSelectableByMouse)

        main_thread_checked = []
        cleaned_up = []

        def worker_task() -> str:
            return "worker_result_ok"

        def on_success_callback(result: str) -> None:
            # Must run on main Qt GUI thread
            is_main = QThread.currentThread() == app.thread()
            main_thread_checked.append(is_main)
            test_label.setText(result)

        def cleanup_callback() -> None:
            cleaned_up.append(True)

        worker = CryptoTaskWorker(worker_task)
        thread = QThread()
        worker.moveToThread(thread)
        bridge = TaskBridge(
            on_success=on_success_callback,
            cleanup=cleanup_callback,
        )

        from PySide6.QtCore import Qt
        thread.started.connect(worker.run)
        worker.result_ready.connect(bridge.handle_success, Qt.QueuedConnection)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)

        thread.start()
        while thread.isRunning():
            app.processEvents()
            thread.wait(10)

        thread.deleteLater()
        bridge.deleteLater()

        self.assertTrue(cleaned_up)
        self.assertTrue(main_thread_checked)
        self.assertTrue(main_thread_checked[0], "TaskBridge callback must execute on main Qt thread")
        self.assertEqual(test_label.text(), "worker_result_ok")


if __name__ == "__main__":
    unittest.main()
