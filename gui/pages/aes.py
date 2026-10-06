"""AES workspace for symmetric key generation and file operations."""

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
            "AES Workspace",
            "Advanced Encryption Standard (AES-CBC with PKCS#7 padding).",
            badge_text="AES-256 Engine Active",
            badge_status="success",
        )
        layout.addWidget(header)

        # Card 1: Key Generation
        key_gen_card = CyberCard(
            "AES Key Generation",
            "Generate cryptographically secure symmetric keys in binary format (.key).",
        )
        key_gen_layout = QVBoxLayout()
        key_gen_layout.setSpacing(14)

        # Key Size Selector
        size_lbl = QLabel("Key Size")
        size_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")
        self.key_size_selector = SegmentedSelector(["128", "192", "256"], default_index=2)

        key_gen_layout.addWidget(size_lbl)
        key_gen_layout.addWidget(self.key_size_selector)

        # Save Directory
        self.key_save_folder = PathPickerRow(
            "Save Folder (Optional)",
            "Leave blank for default storage/keys location",
            is_folder=True,
        )
        key_gen_layout.addWidget(self.key_save_folder)

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
        )
        self.enc_input_picker = PathPickerRow(
            "Input File to Encrypt",
            "Select plaintext file to encrypt",
        )
        self.enc_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/encrypted directory",
            is_folder=True,
        )

        enc_layout.addWidget(self.enc_key_picker)
        enc_layout.addWidget(self.enc_input_picker)
        enc_layout.addWidget(self.enc_output_picker)

        # Optional IV
        iv_col = QVBoxLayout()
        iv_col.setSpacing(4)
        iv_lbl = QLabel("Initialization Vector (IV) - Optional")
        iv_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #94A3B8;")
        self.enc_iv_input = QLineEdit()
        self.enc_iv_input.setPlaceholderText("Optional: Enter 16-byte hex IV (32 characters) or leave blank")
        iv_help = QLabel("Leave empty to generate a cryptographically secure random IV automatically.")
        iv_help.setStyleSheet("font-size: 11px; color: #64748B;")
        iv_col.addWidget(iv_lbl)
        iv_col.addWidget(self.enc_iv_input)
        iv_col.addWidget(iv_help)
        enc_layout.addLayout(iv_col)

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
            "Restore encrypted file (.aes.enc) back to original plaintext.",
        )
        dec_layout = QVBoxLayout()
        dec_layout.setSpacing(14)

        self.dec_key_picker = PathPickerRow(
            "AES Key File (*.key)",
            "Select key file used for decryption",
            file_filter="Key Files (*.key);;All Files (*.*)",
        )
        self.dec_input_picker = PathPickerRow(
            "Encrypted Input File (*.aes.enc)",
            "Select ciphertext file to decrypt",
            file_filter="Encrypted Files (*.enc);;All Files (*.*)",
        )
        self.dec_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/decrypted directory",
            is_folder=True,
        )

        dec_layout.addWidget(self.dec_key_picker)
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

    def _create_path_result_display(self, label_text: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pathResultFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
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
        copy_btn.setFixedHeight(26)
        copy_btn.setFixedWidth(84)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(
            lambda: self._copy_clipboard(frame.path_label.text())
        )
        layout.addWidget(copy_btn)

        return frame

    def _copy_clipboard(self, text: str) -> None:
        if text:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)

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
