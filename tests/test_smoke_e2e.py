"""End-to-end smoke verification test for CipherAI UI workspaces."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

APP = QApplication.instance() or QApplication(sys.argv)

from gui.activity import get_activity_tracker
from gui.dialogs import CyberDialog
from gui.main_window import MainWindow
from gui.pages.aes import AESPage
from gui.pages.dashboard import DashboardPage
from gui.pages.des import DESPage
from gui.pages.files import FilesPage
from gui.pages.home import HomePage
from gui.pages.rsa import RSAPage
from gui.pages.settings import SettingsPage
from gui.theme import DARK_THEME, LIGHT_THEME


class SmokeE2ETest(unittest.TestCase):
    """End-to-end verification of all GUI workspaces."""

    def test_full_application_smoke(self) -> None:
        window = MainWindow()
        window.show()
        APP.processEvents()

        with TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)

            # 1. AES Workspace E2E
            aes_page = window._page_widgets[window._page_map["aes"]]
            aes_page.key_save_folder.set_text(str(tmp / "aes_keys"))
            with patch("gui.pages.aes.show_success"), patch("gui.pages.aes.show_error"):
                aes_page._generate_key()
                APP.processEvents()

            key_path = Path(aes_page.enc_key_picker.text())
            self.assertTrue(key_path.exists())

            plain_file = tmp / "document.txt"
            secret_text = "CipherAI Modern Cybersecurity Suite - Top Secret Payload"
            plain_file.write_text(secret_text)

            aes_page.enc_input_picker.set_text(str(plain_file))
            aes_page.enc_output_picker.set_text(str(tmp / "aes_encrypted"))
            with patch("gui.pages.aes.show_success"), patch("gui.pages.aes.show_error"):
                aes_page._encrypt_file()
                APP.processEvents()

            enc_path = Path(aes_page.dec_input_picker.text())
            self.assertTrue(enc_path.exists())

            aes_page.dec_output_picker.set_text(str(tmp / "aes_decrypted"))
            with patch("gui.pages.aes.show_success"), patch("gui.pages.aes.show_error"):
                aes_page._decrypt_file()
                APP.processEvents()

            dec_files = list((tmp / "aes_decrypted").glob("*"))
            self.assertGreater(len(dec_files), 0)
            self.assertEqual(dec_files[0].read_text(), secret_text)

            # 2. RSA Workspace E2E
            rsa_page = window._page_widgets[window._page_map["rsa"]]
            rsa_page.key_save_folder.set_text(str(tmp / "rsa_keys"))
            with patch("gui.pages.rsa.show_success"), patch("gui.pages.rsa.show_error"):
                rsa_page._generate_keys()
                APP.processEvents()

            pub_path = Path(rsa_page.enc_pubkey_picker.text())
            priv_path = Path(rsa_page.dec_privkey_picker.text())
            self.assertTrue(pub_path.exists())
            self.assertTrue(priv_path.exists())

            rsa_plain = tmp / "rsa_secret.txt"
            rsa_secret_text = "Asymmetric RSA Secret"
            rsa_plain.write_text(rsa_secret_text)

            rsa_page.enc_input_picker.set_text(str(rsa_plain))
            rsa_page.enc_output_picker.set_text(str(tmp / "rsa_encrypted"))
            with patch("gui.pages.rsa.show_success"), patch("gui.pages.rsa.show_error"):
                rsa_page._encrypt_file()
                APP.processEvents()

            rsa_enc = Path(rsa_page.dec_input_picker.text())
            self.assertTrue(rsa_enc.exists())

            rsa_page.dec_output_picker.set_text(str(tmp / "rsa_decrypted"))
            with patch("gui.pages.rsa.show_success"), patch("gui.pages.rsa.show_error"):
                rsa_page._decrypt_file()
                APP.processEvents()

            rsa_dec_files = list((tmp / "rsa_decrypted").glob("*"))
            self.assertGreater(len(rsa_dec_files), 0)
            self.assertEqual(rsa_dec_files[0].read_text(), rsa_secret_text)

            # 3. Double DES Workspace E2E
            ddes_page = window._page_widgets[window._page_map["double_des"]]
            ddes_page.key_save_folder.set_text(str(tmp / "ddes_keys"))
            with patch("gui.pages.des.show_success"), patch("gui.pages.des.show_error"):
                ddes_page._generate_keys()
                APP.processEvents()

            k1_path = Path(ddes_page.enc_key_pickers[0].text())
            k2_path = Path(ddes_page.enc_key_pickers[1].text())
            self.assertTrue(k1_path.exists() and k2_path.exists())

            ddes_plain = tmp / "ddes_plain.txt"
            ddes_plain.write_text("Double DES secret")
            ddes_page.enc_input_picker.set_text(str(ddes_plain))
            ddes_page.enc_output_picker.set_text(str(tmp / "ddes_enc"))
            with patch("gui.pages.des.show_success"), patch("gui.pages.des.show_error"):
                ddes_page._encrypt_file()
                APP.processEvents()

            ddes_enc = Path(ddes_page.dec_input_picker.text())
            self.assertTrue(ddes_enc.exists())

            ddes_page.dec_output_picker.set_text(str(tmp / "ddes_dec"))
            with patch("gui.pages.des.show_success"), patch("gui.pages.des.show_error"):
                ddes_page._decrypt_file()
                APP.processEvents()

            ddes_dec_files = list((tmp / "ddes_dec").glob("*"))
            self.assertGreater(len(ddes_dec_files), 0)
            self.assertEqual(ddes_dec_files[0].read_text(), "Double DES secret")

            # 4. Triple DES Workspace E2E
            tdes_page = window._page_widgets[window._page_map["triple_des"]]
            tdes_page.key_save_folder.set_text(str(tmp / "tdes_keys"))
            with patch("gui.pages.des.show_success"), patch("gui.pages.des.show_error"):
                tdes_page._generate_keys()
                APP.processEvents()

            t_k1 = Path(tdes_page.enc_key_pickers[0].text())
            t_k2 = Path(tdes_page.enc_key_pickers[1].text())
            t_k3 = Path(tdes_page.enc_key_pickers[2].text())
            self.assertTrue(t_k1.exists() and t_k2.exists() and t_k3.exists())

            tdes_plain = tmp / "tdes_plain.txt"
            tdes_plain.write_text("Triple DES secret")
            tdes_page.enc_input_picker.set_text(str(tdes_plain))
            tdes_page.enc_output_picker.set_text(str(tmp / "tdes_enc"))
            with patch("gui.pages.des.show_success"), patch("gui.pages.des.show_error"):
                tdes_page._encrypt_file()
                APP.processEvents()

            tdes_enc = Path(tdes_page.dec_input_picker.text())
            self.assertTrue(tdes_enc.exists())

            tdes_page.dec_output_picker.set_text(str(tmp / "tdes_dec"))
            with patch("gui.pages.des.show_success"), patch("gui.pages.des.show_error"):
                tdes_page._decrypt_file()
                APP.processEvents()

            tdes_dec_files = list((tmp / "tdes_dec").glob("*"))
            self.assertGreater(len(tdes_dec_files), 0)
            self.assertEqual(tdes_dec_files[0].read_text(), "Triple DES secret")

            # 5. Activity Tracker
            tracker = get_activity_tracker()
            items = tracker.get_all()
            self.assertGreaterEqual(len(items), 8)

            # 6. Dashboard & Files Rendering
            dashboard_page: DashboardPage = window._page_widgets[window._page_map["dashboard"]]
            dashboard_page._refresh_activity()
            APP.processEvents()

            files_page: FilesPage = window._page_widgets[window._page_map["files"]]
            files_page._refresh_table()
            APP.processEvents()

            # 7. Theme Switching
            window._handle_theme_changed(LIGHT_THEME)
            APP.processEvents()
            self.assertEqual(window._theme, LIGHT_THEME)
            window._handle_theme_changed(DARK_THEME)
            APP.processEvents()
            self.assertEqual(window._theme, DARK_THEME)

            # 8. Dialog
            dlg = CyberDialog(
                window,
                "success",
                "Verification Complete",
                "All cryptographic suites operational.",
                details=str(enc_path),
                theme=DARK_THEME,
            )
            self.assertEqual(dlg.dialog_title, "Verification Complete")
            self.assertEqual(dlg.details_text, str(enc_path))
            dlg.close()

        window.close()


if __name__ == "__main__":
    unittest.main()
