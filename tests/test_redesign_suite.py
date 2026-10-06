"""Comprehensive test suite verifying CipherAI UI/UX redesign and functional preservation."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from PySide6.QtCore import QEventLoop, QThread, QTimer
from PySide6.QtWidgets import QApplication

# Ensure QApplication exists for GUI tests
APP = QApplication.instance() or QApplication(sys.argv)

from ai.dispatcher import AIDispatcher
from ai.parser import AIParser
from ai.tools.validation import ToolValidationClarification
from crypto.aes import AESService
from crypto.double_des import DoubleDESService
from crypto.rsa import RSAService
from crypto.triple_des import TripleDESService
from gui.activity import get_activity_tracker
from gui.dialogs import CyberDialog, show_error, show_info, show_success, show_warning
from gui.main_window import MainWindow
from gui.pages.aes import AESPage
from gui.pages.dashboard import DashboardPage
from gui.pages.des import DESPage
from gui.pages.files import FilesPage
from gui.pages.home import AIResult, AIWorker, HomePage
from gui.pages.rsa import RSAPage
from gui.pages.settings import SettingsPage
from gui.sidebar import Sidebar
from gui.theme import DARK_THEME, LIGHT_THEME, normalize_theme


class RedesignFunctionalTestSuite(unittest.TestCase):
    """Test 20 minimum required functional verification workflows."""

    # 1. AES key generation
    def test_01_aes_key_generation(self) -> None:
        with TemporaryDirectory() as tmp:
            service = AESService()
            key_path = service.generate_key(256, Path(tmp))
            self.assertTrue(key_path.exists())
            self.assertEqual(key_path.stat().st_size, 32)  # 256 bits = 32 bytes

    # 2. AES encryption
    def test_02_aes_encryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = AESService()
            tmp_p = Path(tmp)
            key_path = service.generate_key(256, tmp_p)
            input_file = tmp_p / "sample.txt"
            input_file.write_text("Confidential Cyber Intelligence Data")
            out_folder = tmp_p / "enc"

            enc_path = service.encrypt(key_path, input_file, out_folder)
            self.assertTrue(enc_path.exists())
            self.assertNotEqual(enc_path.read_bytes(), input_file.read_bytes())

    # 3. AES decryption
    def test_03_aes_decryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = AESService()
            tmp_p = Path(tmp)
            key_path = service.generate_key(256, tmp_p)
            input_file = tmp_p / "sample.txt"
            content = "Highly Classified Payload 12345"
            input_file.write_text(content)
            enc_path = service.encrypt(key_path, input_file, tmp_p / "enc")

            dec_path = service.decrypt(key_path, enc_path, tmp_p / "dec")
            self.assertTrue(dec_path.exists())
            self.assertEqual(dec_path.read_text(), content)

    # 4. RSA key generation
    def test_04_rsa_key_generation(self) -> None:
        with TemporaryDirectory() as tmp:
            service = RSAService()
            pub_path, priv_path = service.generate_key_pair(2048, Path(tmp))
            self.assertTrue(pub_path.exists())
            self.assertTrue(priv_path.exists())
            self.assertIn(b"BEGIN PUBLIC KEY", pub_path.read_bytes())
            self.assertIn(b"BEGIN PRIVATE KEY", priv_path.read_bytes())

    # 5. RSA encryption
    def test_05_rsa_encryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = RSAService()
            tmp_p = Path(tmp)
            pub_path, priv_path = service.generate_key_pair(2048, tmp_p)
            input_file = tmp_p / "rsa_plain.txt"
            input_file.write_text("Asymmetric Secret")

            enc_path = service.encrypt_file(pub_path, input_file, tmp_p / "enc")
            self.assertTrue(enc_path.exists())
            self.assertNotEqual(enc_path.read_bytes(), input_file.read_bytes())

    # 6. RSA decryption
    def test_06_rsa_decryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = RSAService()
            tmp_p = Path(tmp)
            pub_path, priv_path = service.generate_key_pair(2048, tmp_p)
            input_file = tmp_p / "rsa_plain.txt"
            content = "Top Secret RSA Token"
            input_file.write_text(content)
            enc_path = service.encrypt_file(pub_path, input_file, tmp_p / "enc")

            dec_path = service.decrypt_file(priv_path, enc_path, tmp_p / "dec")
            self.assertTrue(dec_path.exists())
            self.assertEqual(dec_path.read_text(), content)

    # 7. Double DES encryption
    def test_07_double_des_encryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = DoubleDESService()
            tmp_p = Path(tmp)
            k1, k2 = service.generate_key(tmp_p)
            input_file = tmp_p / "ddes.txt"
            input_file.write_text("Double DES Test")

            enc_path = service.encrypt(k1, k2, input_file, tmp_p / "enc")
            self.assertTrue(enc_path.exists())
            self.assertNotEqual(enc_path.read_bytes(), input_file.read_bytes())

    # 8. Double DES decryption
    def test_08_double_des_decryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = DoubleDESService()
            tmp_p = Path(tmp)
            k1, k2 = service.generate_key(tmp_p)
            input_file = tmp_p / "ddes.txt"
            content = "Double DES Round Trip Payload"
            input_file.write_text(content)
            enc_path = service.encrypt(k1, k2, input_file, tmp_p / "enc")

            dec_path = service.decrypt(k1, k2, enc_path, tmp_p / "dec")
            self.assertTrue(dec_path.exists())
            self.assertEqual(dec_path.read_text(), content)

    # 9. Triple DES encryption
    def test_09_triple_des_encryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = TripleDESService()
            tmp_p = Path(tmp)
            k1, k2, k3 = service.generate_key(tmp_p)
            input_file = tmp_p / "tdes.txt"
            input_file.write_text("Triple DES Test")

            enc_path = service.encrypt(k1, k2, k3, input_file, tmp_p / "enc")
            self.assertTrue(enc_path.exists())
            self.assertNotEqual(enc_path.read_bytes(), input_file.read_bytes())

    # 10. Triple DES decryption
    def test_10_triple_des_decryption(self) -> None:
        with TemporaryDirectory() as tmp:
            service = TripleDESService()
            tmp_p = Path(tmp)
            k1, k2, k3 = service.generate_key(tmp_p)
            input_file = tmp_p / "tdes.txt"
            content = "Triple DES Round Trip Payload 123"
            input_file.write_text(content)
            enc_path = service.encrypt(k1, k2, k3, input_file, tmp_p / "enc")

            dec_path = service.decrypt(k1, k2, k3, enc_path, tmp_p / "dec")
            self.assertTrue(dec_path.exists())
            self.assertEqual(dec_path.read_text(), content)

    # 11. AI chat parsing & routing
    def test_11_ai_chat_response(self) -> None:
        parser = AIParser()
        raw = '{"action": "chat", "response": "AES is a symmetric block cipher standardized by NIST."}'
        parsed = parser.parse(raw)
        self.assertEqual(parsed["action"], "chat")
        dispatcher = AIDispatcher()
        result = dispatcher.dispatch(parsed)
        self.assertIn("symmetric block cipher", result)

    # 12. AI tool commands
    def test_12_ai_tool_commands(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            raw = (
                f'{{"action": "tool", "service": "AES", "operation": "generate_key", "reason": "create key", '
                f'"arguments": {{"key_size": 128, "save_directory": "{str(tmp_p).replace("\\", "/")}"}}}}'
            )
            parsed = AIParser().parse(raw)
            self.assertEqual(parsed["action"], "tool")
            res = AIDispatcher().dispatch(parsed)
            self.assertTrue(Path(res).exists())

    # 13. AI clarification responses
    def test_13_ai_clarification_response(self) -> None:
        raw = '{"action": "clarify", "question": "What key size would you like to use for AES?"}'
        parsed = AIParser().parse(raw)
        self.assertEqual(parsed["action"], "clarify")
        res = AIDispatcher().dispatch(parsed)
        self.assertIn("What key size", res)

    # 14. Invalid key handling
    def test_14_invalid_key_handling(self) -> None:
        service = AESService()
        with self.assertRaises(ValueError):
            service._validate_key_size(512)  # Invalid AES size

    # 15. Invalid IV handling
    def test_15_invalid_iv_handling(self) -> None:
        from core.validators import validate_iv
        with self.assertRaises(ValueError):
            validate_iv("short_iv", 16)
        with self.assertRaises(ValueError):
            validate_iv("not_hex_chars_123456789012345678", 16)

    # 16. Invalid file handling
    def test_16_invalid_file_handling(self) -> None:
        service = AESService()
        with TemporaryDirectory() as tmp:
            k = Path(tmp) / "aes.key"
            k.write_bytes(b"0" * 32)
            missing = Path(tmp) / "nonexistent.txt"
            with self.assertRaises(FileNotFoundError):
                service.encrypt(k, missing)

    # 17. Invalid output path handling
    def test_17_invalid_output_path_handling(self) -> None:
        service = RSAService()
        with TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            pub, priv = service.generate_key_pair(2048, tmp_p)
            inp = tmp_p / "inp.txt"
            inp.write_text("hello")
            # Output folder cannot be an existing file
            file_as_folder = tmp_p / "existing_file.txt"
            file_as_folder.write_text("I am a file")
            with self.assertRaises((FileExistsError, ValueError)):
                service.encrypt_file(pub, inp, file_as_folder)

    # 18. QThread / background processing
    def test_18_qthread_background_processing(self) -> None:
        worker = AIWorker("Explain AES")
        thread = QThread()
        worker.moveToThread(thread)

        events_received = []
        worker.started.connect(lambda: events_received.append("started"))
        worker.finished.connect(lambda: events_received.append("finished"))

        loop = QEventLoop()
        worker.finished.connect(loop.quit)

        dummy_result = AIResult({"action": "chat", "response": "AES CBC"}, "AES CBC")
        with patch.object(AIWorker, "_run_pipeline", return_value=dummy_result):
            thread.started.connect(worker.run)
            thread.start()
            loop.exec()
            thread.quit()
            thread.wait(1000)

        self.assertIn("started", events_received)
        self.assertIn("finished", events_received)

    # 19. Theme switching
    def test_19_theme_switching(self) -> None:
        window = MainWindow()
        window.show()
        # Switch to Light
        window._handle_theme_changed(LIGHT_THEME)
        self.assertEqual(window._theme, LIGHT_THEME)
        # Switch back to Dark
        window._handle_theme_changed(DARK_THEME)
        self.assertEqual(window._theme, DARK_THEME)
        window.close()

    # 20. Navigation between every single page
    def test_20_navigation_between_pages(self) -> None:
        window = MainWindow()
        window.show()

        expected_pages = [
            "dashboard",
            "ai_assistant",
            "aes",
            "rsa",
            "double_des",
            "triple_des",
            "files",
            "settings",
            "about",
        ]

        for page_key in expected_pages:
            window._navigate_to_page(page_key)
            self.assertEqual(window.sidebar._active_key, page_key)
            current_widget = window._pages.currentWidget()
            self.assertIsNotNone(current_widget)

        window.close()

    # Additional UI verification: Dialog readability & contrast
    def test_21_dialog_readability(self) -> None:
        dialog = CyberDialog(
            None,
            "success",
            "Operation Completed",
            "File was encrypted successfully with AES-256.",
            details="C:/storage/encrypted/file.aes.enc",
            theme=DARK_THEME,
        )
        self.assertIn("Operation Completed", dialog.dialog_title)
        self.assertIn("File was encrypted", dialog.message_text)
        self.assertEqual(dialog.details_text, "C:/storage/encrypted/file.aes.enc")
        dialog.close()

    # Additional UI verification: Activity tracker
    def test_22_activity_tracker_and_dashboard_integration(self) -> None:
        tracker = get_activity_tracker()
        tracker.clear()
        self.assertEqual(len(tracker.get_all()), 0)

        tracker.record("File Encryption", "AES-256", "C:/test.aes.enc", "Success")
        items = tracker.get_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].operation, "File Encryption")
        self.assertEqual(items[0].algorithm, "AES-256")
        self.assertEqual(items[0].target_name, "test.aes.enc")
        tracker.clear()


if __name__ == "__main__":
    unittest.main()
