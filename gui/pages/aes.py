"""AES workspace for symmetric key generation and file operations."""

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
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from crypto.aes import AESService
from gui.activity import get_activity_tracker
from gui.components import (
    CyberCard,
    PageHeader,
    PathPickerRow,
    SegmentedSelector,
    SpecPill,
)
from gui.dialogs import show_error, show_info, show_success, show_warning
from gui.theme import DARK_THEME, ThemeName, get_workspace_stylesheet


class AESPage(QWidget):
    """AES workspace with key generation, encryption, and decryption cards."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("aesPage")
        self._theme = DARK_THEME
        self.service = AESService()

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("aesScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(24)

        # Header
        header = PageHeader(
            "AES Symmetric Workspace",
            "Advanced Encryption Standard (AES-CBC with PKCS#7 padding and 16-byte random IV).",
            badge_text="AES-256 Engine Active",
            badge_status="success",
        )
        layout.addWidget(header)

        # Technical Specifications Bar
        spec_row = QHBoxLayout()
        spec_row.setSpacing(10)
        spec_row.addWidget(SpecPill("Standard", "NIST FIPS 197"))
        spec_row.addWidget(SpecPill("Cipher Mode", "CBC (Cipher Block Chaining)"))
        spec_row.addWidget(SpecPill("Padding", "PKCS#7"))
        spec_row.addWidget(SpecPill("Block Size", "128 bits (16 bytes)"))
        spec_row.addStretch()
        layout.addLayout(spec_row)

        # Card 1: Key Generation
        key_gen_card = CyberCard(
            "AES Key Generation",
            "Generate cryptographically secure symmetric keys in binary format (.key).",
        )
        key_gen_layout = QVBoxLayout()
        key_gen_layout.setSpacing(14)

        # Top inputs row: Key Size on left, Save Folder on right
        top_inputs_row = QHBoxLayout()
        top_inputs_row.setSpacing(20)

        # Key Size Selector
        size_col = QVBoxLayout()
        size_col.setSpacing(6)
        size_lbl = QLabel("Key Size")
        size_lbl.setObjectName("fieldLabel")
        self.key_size_selector = SegmentedSelector(["128", "192", "256"], default_index=2)
        size_col.addWidget(size_lbl)
        size_col.addWidget(self.key_size_selector)

        # Save Directory
        self.key_save_folder = PathPickerRow(
            "Save Folder (Optional)",
            "Leave blank for default storage/keys location",
            is_folder=True,
            required=False,
        )

        top_inputs_row.addLayout(size_col)
        top_inputs_row.addWidget(self.key_save_folder, stretch=1)
        key_gen_layout.addLayout(top_inputs_row)

        # Action button
        gen_btn_row = QHBoxLayout()
        gen_btn_row.addStretch()
        self.gen_key_btn = QPushButton("Generate AES Key")
        self.gen_key_btn.setObjectName("primaryButton")
        self.gen_key_btn.setCursor(Qt.PointingHandCursor)
        self.gen_key_btn.setFixedHeight(36)
        self.gen_key_btn.clicked.connect(self._generate_key)
        gen_btn_row.addWidget(self.gen_key_btn)
        key_gen_layout.addLayout(gen_btn_row)

        # Generated Key Result Display
        self.key_result_frame = self._create_path_result_display("Generated Key Path:")
        key_gen_layout.addWidget(self.key_result_frame)
        self.key_result_frame.hide()

        key_gen_card.add_layout(key_gen_layout)
        layout.addWidget(key_gen_card)

        # Card 2: File Encryption
        enc_card = CyberCard(
            "File Encryption",
            "Encrypt any file using AES in CBC mode with PKCS#7 padding.",
        )
        enc_layout = QVBoxLayout()
        enc_layout.setSpacing(14)

        self.enc_key_picker = PathPickerRow(
            "AES Key File (*.key)",
            "Select key file used for encryption",
            file_filter="Key Files (*.key);;All Files (*.*)",
            required=True,
        )
        self.enc_input_picker = PathPickerRow(
            "Input File to Encrypt",
            "Select plaintext file to encrypt",
            required=True,
        )
        self.enc_output_picker = PathPickerRow(
            "Output Directory",
            "Leave blank for default storage/encrypted location",
            is_folder=True,
            required=False,
        )

        enc_layout.addWidget(self.enc_key_picker)
        enc_layout.addWidget(self.enc_input_picker)
        enc_layout.addWidget(self.enc_output_picker)

        # Optional IV
        iv_col = QVBoxLayout()
        iv_col.setSpacing(4)
        iv_lbl_row = QHBoxLayout()
        iv_lbl_row.setSpacing(6)
        iv_lbl = QLabel("Initialization Vector (IV)")
        iv_lbl.setObjectName("fieldLabel")
        iv_badge = QLabel("[OPTIONAL]")
        iv_badge.setObjectName("optionalBadge")
        iv_lbl_row.addWidget(iv_lbl)
        iv_lbl_row.addWidget(iv_badge)
        iv_lbl_row.addStretch()

        self.enc_iv_input = QLineEdit()
        self.enc_iv_input.setPlaceholderText("Optional: Enter 16-byte hex IV (32 hex characters) or leave blank")
        iv_help = QLabel("Leave empty to generate a cryptographically secure random 16-byte IV automatically.")
        iv_help.setObjectName("helperText")
        iv_col.addLayout(iv_lbl_row)
        iv_col.addWidget(self.enc_iv_input)
        iv_col.addWidget(iv_help)
        enc_layout.addLayout(iv_col)

        enc_btn_row = QHBoxLayout()
        enc_btn_row.addStretch()
        self.enc_btn = QPushButton("🔒 Encrypt File")
        self.enc_btn.setObjectName("primaryButton")
        self.enc_btn.setCursor(Qt.PointingHandCursor)
        self.enc_btn.setFixedHeight(36)
        self.enc_btn.clicked.connect(self._encrypt_file)
        enc_btn_row.addWidget(self.enc_btn)
        enc_layout.addLayout(enc_btn_row)

        enc_card.add_layout(enc_layout)

        # Card 3: File Decryption
        dec_card = CyberCard(
            "File Decryption",
            "Restore encrypted file (.aes.enc) back to original plaintext.",
        )
        dec_layout = QVBoxLayout()
        dec_layout.setSpacing(14)

        self.dec_key_picker = PathPickerRow(
            "AES Key File (*.key)",
            "Select key file used for decryption",
            file_filter="Key Files (*.key);;All Files (*.*)",
            required=True,
        )
        self.dec_input_picker = PathPickerRow(
            "Encrypted Input File (*.aes.enc)",
            "Select ciphertext file to decrypt",
            file_filter="Encrypted Files (*.enc);;All Files (*.*)",
            required=True,
        )
        self.dec_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/decrypted directory",
            is_folder=True,
            required=False,
        )

        dec_layout.addWidget(self.dec_key_picker)
        dec_layout.addWidget(self.dec_input_picker)
        dec_layout.addWidget(self.dec_output_picker)

        dec_btn_row = QHBoxLayout()
        dec_btn_row.addStretch()
        self.dec_btn = QPushButton("🔓 Decrypt File")
        self.dec_btn.setObjectName("primaryButton")
        self.dec_btn.setCursor(Qt.PointingHandCursor)
        self.dec_btn.setFixedHeight(36)
        self.dec_btn.clicked.connect(self._decrypt_file)
        dec_btn_row.addWidget(self.dec_btn)
        dec_layout.addLayout(dec_btn_row)

        dec_card.add_layout(dec_layout)

        # 2-column side-by-side layout matching reference design
        ops_row = QHBoxLayout()
        ops_row.setSpacing(16)
        ops_row.addWidget(enc_card, stretch=1)
        ops_row.addWidget(dec_card, stretch=1)
        layout.addLayout(ops_row)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_path_result_display(self, label_text: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pathResultFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        lbl = QLabel(label_text)
        lbl.setObjectName("pathResultLabel")
        layout.addWidget(lbl)

        frame.path_label = QLabel("")
        frame.path_label.setObjectName("pathResultText")
        frame.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(frame.path_label, stretch=1)

        copy_btn = QPushButton("Copy Path")
        copy_btn.setObjectName("secondaryButton")
        copy_btn.setFixedHeight(28)
        copy_btn.setFixedWidth(84)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda: self._copy_clipboard(frame.path_label.text())
        )
        layout.addWidget(copy_btn)

        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setObjectName("secondaryButton")
        open_folder_btn.setFixedHeight(28)
        open_folder_btn.setFixedWidth(96)
        open_folder_btn.setCursor(Qt.PointingHandCursor)
        open_folder_btn.clicked.connect(
            lambda: self._open_folder(frame.path_label.text())
        )
        layout.addWidget(open_folder_btn)

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

    def _generate_key(self) -> None:
        try:
            key_size = int(self.key_size_selector.current_value())
        except ValueError:
            key_size = 256

        save_dir = self.key_save_folder.path()

        try:
            key_path = self.service.generate_key(key_size, save_dir)
            path_str = str(key_path.resolve())

            self.key_result_frame.path_label.setText(path_str)
            self.key_result_frame.show()

            # Pre-fill encryption/decryption key fields for user convenience
            self.enc_key_picker.set_text(path_str)
            self.dec_key_picker.set_text(path_str)

            get_activity_tracker().record(
                operation="Key Generation",
                algorithm=f"AES-{key_size}",
                target_path=key_path,
                status="Success",
            )

            show_success(
                self,
                "AES Key Generated",
                f"Successfully generated a cryptographically secure {key_size}-bit AES key.",
                details=path_str,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "Key Generation Failed",
                f"Unable to generate AES key: {exc}",
                theme=self._theme,
            )

    def _encrypt_file(self) -> None:
        key_path = self.enc_key_picker.path()
        if not key_path:
            show_warning(
                self,
                "Missing Key File",
                "Please select an AES key file before encrypting.",
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
        iv = self.enc_iv_input.text().strip() or None

        try:
            saved_path = self.service.encrypt(
                key_path=key_path,
                input_file_path=input_path,
                output_folder=output_dir,
                iv=iv,
            )
            path_str = str(saved_path.resolve())

            # Pre-fill decryption encrypted file
            self.dec_input_picker.set_text(path_str)

            get_activity_tracker().record(
                operation="File Encryption",
                algorithm="AES-CBC",
                target_path=saved_path,
                status="Success",
            )

            show_success(
                self,
                "File Encrypted Successfully",
                f"File '{input_path.name}' was encrypted using AES-CBC.",
                details=path_str,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "Encryption Failed",
                f"Failed to encrypt file: {exc}",
                theme=self._theme,
            )

    def _decrypt_file(self) -> None:
        key_path = self.dec_key_picker.path()
        if not key_path:
            show_warning(
                self,
                "Missing Key File",
                "Please select an AES key file before decrypting.",
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

        try:
            saved_path = self.service.decrypt(
                key_path=key_path,
                input_file_path=input_path,
                output_folder=output_dir,
            )
            path_str = str(saved_path.resolve())

            get_activity_tracker().record(
                operation="File Decryption",
                algorithm="AES-CBC",
                target_path=saved_path,
                status="Success",
            )

            show_success(
                self,
                "File Decrypted Successfully",
                f"File '{input_path.name}' was decrypted successfully.",
                details=path_str,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "Decryption Failed",
                f"Failed to decrypt file: {exc}",
                theme=self._theme,
            )

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self.key_size_selector.apply_theme(theme)
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_workspace_stylesheet(self._theme, "aes"))
