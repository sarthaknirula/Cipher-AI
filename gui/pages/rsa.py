"""RSA workspace for asymmetric key pair generation and file operations."""

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from crypto.rsa import RSAService
from gui.activity import get_activity_tracker
from gui.components import (
    CyberCard,
    PageHeader,
    PathPickerRow,
    SegmentedSelector,
)
from gui.dialogs import show_error, show_info, show_success, show_warning
from gui.theme import DARK_THEME, ThemeName, get_workspace_stylesheet

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RSAPage(QWidget):
    """RSA workspace with key pair generation, encryption, and decryption cards."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rsaPage")
        self._theme = DARK_THEME
        self.rsa_service = RSAService()

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("rsaScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(24)

        # Header
        header = PageHeader(
            "RSA Workspace",
            "Asymmetric Key Cryptography (RSA-OAEP with SHA-256 padding).",
            badge_text="RSA-4096 Engine Active",
            badge_status="success",
        )
        layout.addWidget(header)

        # Card 1: Key Pair Generation
        key_gen_card = CyberCard(
            "RSA Key Pair Generation",
            "Generate public and private key pairs (.pem) using Rivest-Shamir-Adleman algorithm.",
        )
        key_gen_layout = QVBoxLayout()
        key_gen_layout.setSpacing(14)

        # Key Size Selector
        size_lbl = QLabel("Key Size (bits)")
        size_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")
        self.key_size_selector = SegmentedSelector(["2048", "3072", "4096"], default_index=2)

        key_gen_layout.addWidget(size_lbl)
        key_gen_layout.addWidget(self.key_size_selector)

        # Save Directory
        self.key_save_folder = PathPickerRow(
            "Save Folder (Optional)",
            "Leave blank for default storage/keys location",
            is_folder=True,
        )
        key_gen_layout.addWidget(self.key_save_folder)

        # Action Button
        gen_btn_row = QHBoxLayout()
        gen_btn_row.addStretch()
        self.gen_key_btn = QPushButton("Generate RSA Key Pair")
        self.gen_key_btn.setObjectName("primaryButton")
        self.gen_key_btn.setCursor(Qt.PointingHandCursor)
        self.gen_key_btn.setFixedHeight(36)
        self.gen_key_btn.clicked.connect(self._generate_keys)
        gen_btn_row.addWidget(self.gen_key_btn)
        key_gen_layout.addLayout(gen_btn_row)

        # Results Frame
        self.key_results_frame = self._create_key_pair_results_display()
        key_gen_layout.addWidget(self.key_results_frame)
        self.key_results_frame.hide()

        key_gen_card.add_layout(key_gen_layout)
        layout.addWidget(key_gen_card)

        # Card 2: File Encryption
        enc_card = CyberCard(
            "File Encryption",
            "Encrypt small documents or payloads using the recipient's RSA public key.",
        )
        enc_layout = QVBoxLayout()
        enc_layout.setSpacing(14)

        self.enc_pubkey_picker = PathPickerRow(
            "RSA Public Key (*.pem)",
            "Select recipient public key file",
            file_filter="PEM Keys (*.pem);;All Files (*.*)",
        )
        self.enc_input_picker = PathPickerRow(
            "Input File to Encrypt",
            "Select plaintext file to encrypt",
        )
        self.enc_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/encrypted location",
            is_folder=True,
        )

        enc_layout.addWidget(self.enc_pubkey_picker)
        enc_layout.addWidget(self.enc_input_picker)
        enc_layout.addWidget(self.enc_output_picker)

        enc_btn_row = QHBoxLayout()
        enc_btn_row.addStretch()
        self.enc_btn = QPushButton("Encrypt File")
        self.enc_btn.setObjectName("primaryButton")
        self.enc_btn.setCursor(Qt.PointingHandCursor)
        self.enc_btn.setFixedHeight(36)
        self.enc_btn.clicked.connect(self._encrypt_file)
        enc_btn_row.addWidget(self.enc_btn)
        enc_layout.addLayout(enc_btn_row)

        enc_card.add_layout(enc_layout)
        layout.addWidget(enc_card)

        # Card 3: File Decryption
        dec_card = CyberCard(
            "File Decryption",
            "Decrypt encrypted payloads using your private key and OAEP padding.",
        )
        dec_layout = QVBoxLayout()
        dec_layout.setSpacing(14)

        self.dec_privkey_picker = PathPickerRow(
            "RSA Private Key (*.pem)",
            "Select your private key file",
            file_filter="PEM Keys (*.pem);;All Files (*.*)",
        )
        self.dec_input_picker = PathPickerRow(
            "Encrypted Input File (*.enc)",
            "Select ciphertext file to decrypt",
            file_filter="Encrypted Files (*.enc);;All Files (*.*)",
        )
        self.dec_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/decrypted location",
            is_folder=True,
        )

        dec_layout.addWidget(self.dec_privkey_picker)
        dec_layout.addWidget(self.dec_input_picker)
        dec_layout.addWidget(self.dec_output_picker)

        dec_btn_row = QHBoxLayout()
        dec_btn_row.addStretch()
        self.dec_btn = QPushButton("Decrypt File")
        self.dec_btn.setObjectName("primaryButton")
        self.dec_btn.setCursor(Qt.PointingHandCursor)
        self.dec_btn.setFixedHeight(36)
        self.dec_btn.clicked.connect(self._decrypt_file)
        dec_btn_row.addWidget(self.dec_btn)
        dec_layout.addLayout(dec_btn_row)

        dec_card.add_layout(dec_layout)
        layout.addWidget(dec_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_key_pair_results_display(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pathResultFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Public Key Row
        pub_row = QHBoxLayout()
        pub_lbl = QLabel("Public Key:")
        pub_lbl.setObjectName("pathResultLabel")
        pub_lbl.setFixedWidth(80)
        frame.pub_path = QLabel("")
        frame.pub_path.setObjectName("pathResultText")
        frame.pub_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        pub_copy = QPushButton("Copy")
        pub_copy.setObjectName("secondaryButton")
        pub_copy.setFixedHeight(24)
        pub_copy.setFixedWidth(54)
        pub_copy.clicked.connect(lambda: self._copy_clipboard(frame.pub_path.text()))

        pub_row.addWidget(pub_lbl)
        pub_row.addWidget(frame.pub_path, stretch=1)
        pub_row.addWidget(pub_copy)
        layout.addLayout(pub_row)

        # Private Key Row
        priv_row = QHBoxLayout()
        priv_lbl = QLabel("Private Key:")
        priv_lbl.setObjectName("pathResultLabel")
        priv_lbl.setFixedWidth(80)
        frame.priv_path = QLabel("")
        frame.priv_path.setObjectName("pathResultText")
        frame.priv_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
        frame.priv_path.setStyleSheet(
            "font-family: 'Consolas', monospace; font-size: 12px; color: #F8FAFC;"
        )
        priv_copy = QPushButton("Copy")
        priv_copy.setObjectName("secondaryButton")
        priv_copy.setFixedHeight(24)
        priv_copy.setFixedWidth(54)
        priv_copy.clicked.connect(lambda: self._copy_clipboard(frame.priv_path.text()))

        priv_row.addWidget(priv_lbl)
        priv_row.addWidget(frame.priv_path, stretch=1)
        priv_row.addWidget(priv_copy)
        layout.addLayout(priv_row)

        # Open Folder Row
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        open_folder_btn = QPushButton("Open Containing Folder")
        open_folder_btn.setObjectName("secondaryButton")
        open_folder_btn.setFixedHeight(26)
        open_folder_btn.clicked.connect(
            lambda: self._open_folder(frame.pub_path.text())
        )
        bottom_row.addWidget(open_folder_btn)
        layout.addLayout(bottom_row)

        return frame

    def _copy_clipboard(self, text: str) -> None:
        if text:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)

    def _open_folder(self, file_path_str: str) -> None:
        if not file_path_str:
            return
        folder = Path(file_path_str).parent
        if folder.exists():
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])

    def _generate_keys(self) -> None:
        try:
            key_size = int(self.key_size_selector.current_value())
        except ValueError:
            key_size = 4096

        save_dir = self.key_save_folder.path()

        try:
            pub_path, priv_path = self.rsa_service.generate_key_pair(key_size, save_dir)
            pub_str = str(pub_path.resolve())
            priv_str = str(priv_path.resolve())

            self.key_results_frame.pub_path.setText(pub_str)
            self.key_results_frame.priv_path.setText(priv_str)
            self.key_results_frame.show()

            # Pre-fill for user
            self.enc_pubkey_picker.set_text(pub_str)
            self.dec_privkey_picker.set_text(priv_str)

            get_activity_tracker().record(
                operation="Key Pair Generation",
                algorithm=f"RSA-{key_size}",
                target_path=pub_path,
                status="Success",
            )

            details_text = f"Public Key:\n{pub_str}\n\nPrivate Key:\n{priv_str}"
            show_success(
                self,
                "RSA Key Pair Generated",
                f"Generated a {key_size}-bit RSA key pair.",
                details=details_text,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "Key Pair Generation Failed",
                f"Unable to generate RSA keys: {exc}",
                theme=self._theme,
            )

    def _encrypt_file(self) -> None:
        pub_path = self.enc_pubkey_picker.path()
        if not pub_path:
            show_warning(
                self,
                "Missing Public Key",
                "Please select an RSA public key file (*.pem).",
                theme=self._theme,
            )
            return

        input_path = self.enc_input_picker.path()
        if not input_path:
            show_warning(
                self,
                "Missing Input File",
                "Please select a file to encrypt.",
                theme=self._theme,
            )
            return

        output_dir = self.enc_output_picker.path()
        if not output_dir:
            output_dir = PROJECT_ROOT / "storage" / "encrypted" / "RSA"

        try:
            saved_path = self.rsa_service.encrypt_file(
                public_key_path=pub_path,
                input_file_path=input_path,
                output_folder=output_dir,
            )
            path_str = str(saved_path.resolve())

            self.dec_input_picker.set_text(path_str)

            get_activity_tracker().record(
                operation="File Encryption",
                algorithm="RSA-OAEP",
                target_path=saved_path,
                status="Success",
            )

            show_success(
                self,
                "RSA Encryption Complete",
                f"Encrypted '{input_path.name}' using RSA-OAEP.",
                details=path_str,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "RSA Encryption Failed",
                f"Unable to encrypt file: {exc}",
                theme=self._theme,
            )

    def _decrypt_file(self) -> None:
        priv_path = self.dec_privkey_picker.path()
        if not priv_path:
            show_warning(
                self,
                "Missing Private Key",
                "Please select an RSA private key file (*.pem).",
                theme=self._theme,
            )
            return

        input_path = self.dec_input_picker.path()
        if not input_path:
            show_warning(
                self,
                "Missing Encrypted File",
                "Please select an encrypted file to decrypt.",
                theme=self._theme,
            )
            return

        output_dir = self.dec_output_picker.path()
        if not output_dir:
            output_dir = PROJECT_ROOT / "storage" / "decrypted" / "RSA"

        try:
            saved_path = self.rsa_service.decrypt_file(
                private_key_path=priv_path,
                encrypted_file_path=input_path,
                output_folder=output_dir,
            )
            path_str = str(saved_path.resolve())

            get_activity_tracker().record(
                operation="File Decryption",
                algorithm="RSA-OAEP",
                target_path=saved_path,
                status="Success",
            )

            show_success(
                self,
                "RSA Decryption Complete",
                f"Decrypted '{input_path.name}' successfully.",
                details=path_str,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "RSA Decryption Failed",
                f"Unable to decrypt file: {exc}",
                theme=self._theme,
            )

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self.key_size_selector.apply_theme(theme)
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_workspace_stylesheet(self._theme, "rsa"))
