"""DES workspace for Double DES and Triple DES legacy cryptographic operations."""

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

from crypto.double_des import DoubleDESService
from crypto.triple_des import TripleDESService
from gui.activity import get_activity_tracker
from gui.components import (
    CyberCard,
    PageHeader,
    PathPickerRow,
    StatusBadge,
)
from gui.dialogs import show_error, show_info, show_success, show_warning
from gui.theme import DARK_THEME, ThemeName, get_workspace_stylesheet

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class DESPage(QWidget):
    """Workspace for Double DES or Triple DES legacy encryption."""

    SERVICES = {
        "Double DES": (DoubleDESService, 2),
        "Triple DES": (TripleDESService, 3),
    }

    def __init__(self, algorithm_name: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if algorithm_name not in self.SERVICES:
            raise ValueError(f"Unsupported DES algorithm: {algorithm_name}")

        self.algorithm_name = algorithm_name
        service_factory, self.key_count = self.SERVICES[algorithm_name]
        self.des_service = service_factory()

        self.setObjectName("desPage")
        self._theme = DARK_THEME

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("desScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(24)

        # Header
        header = PageHeader(
            f"{self.algorithm_name} Workspace",
            "Legacy / Compatibility Algorithm (56-bit DES key cascade).",
            badge_text="Legacy Engine",
            badge_status="warning",
        )
        layout.addWidget(header)

        # Security Advisory Callout
        advisory = QFrame()
        advisory.setObjectName("advisoryFrame")
        adv_layout = QHBoxLayout(advisory)
        adv_layout.setContentsMargins(16, 12, 16, 12)
        adv_layout.setSpacing(10)

        adv_icon = QLabel("Notice:")
        adv_icon.setObjectName("statTitle")
        adv_layout.addWidget(adv_icon)

        adv_text = QLabel(
            f"<b>Compatibility Algorithm:</b> {self.algorithm_name} uses 56-bit DES building blocks "
            "and is maintained for compatibility and analysis. For modern protection, use AES-256."
        )
        adv_text.setObjectName("advisoryText")
        adv_text.setWordWrap(True)
        adv_layout.addWidget(adv_text, stretch=1)
        layout.addWidget(advisory)

        # Card 1: Key Generation
        key_gen_card = CyberCard(
            f"{self.algorithm_name} Key Generation",
            f"Generate {self.key_count} independent 56-bit DES keys (.key).",
        )
        key_gen_layout = QVBoxLayout()
        key_gen_layout.setSpacing(14)

        self.key_save_folder = PathPickerRow(
            "Save Folder (Optional)",
            "Leave blank for default storage/keys location",
            is_folder=True,
        )
        key_gen_layout.addWidget(self.key_save_folder)

        gen_btn_row = QHBoxLayout()
        gen_btn_row.addStretch()
        self.gen_key_btn = QPushButton(f"Generate {self.key_count} Keys")
        self.gen_key_btn.setObjectName("primaryButton")
        self.gen_key_btn.setCursor(Qt.PointingHandCursor)
        self.gen_key_btn.setFixedHeight(36)
        self.gen_key_btn.clicked.connect(self._generate_keys)
        gen_btn_row.addWidget(self.gen_key_btn)
        key_gen_layout.addLayout(gen_btn_row)

        self.key_results_frame = self._create_keys_result_display()
        key_gen_layout.addWidget(self.key_results_frame)
        self.key_results_frame.hide()

        key_gen_card.add_layout(key_gen_layout)
        layout.addWidget(key_gen_card)

        # Card 2: File Encryption
        enc_card = CyberCard(
            "File Encryption",
            f"Encrypt file using sequential {self.algorithm_name} passes in CBC mode.",
        )
        enc_layout = QVBoxLayout()
        enc_layout.setSpacing(14)

        self.enc_key_pickers: list[PathPickerRow] = []
        for i in range(1, self.key_count + 1):
            p = PathPickerRow(
                f"Key {i} File (*.key)",
                f"Select DES key {i}",
                file_filter="Key Files (*.key);;All Files (*.*)",
            )
            self.enc_key_pickers.append(p)
            enc_layout.addWidget(p)

        self.enc_input_picker = PathPickerRow(
            "Input File to Encrypt",
            "Select plaintext file to encrypt",
        )
        self.enc_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/encrypted directory",
            is_folder=True,
        )

        enc_layout.addWidget(self.enc_input_picker)
        enc_layout.addWidget(self.enc_output_picker)

        # Optional IV (8-byte for DES)
        iv_col = QVBoxLayout()
        iv_col.setSpacing(4)
        iv_lbl = QLabel("Initialization Vector (IV) - Optional (8 bytes / 16 hex chars)")
        iv_lbl.setObjectName("fieldLabel")
        self.enc_iv_input = QLineEdit()
        self.enc_iv_input.setPlaceholderText("Optional: Enter 8-byte hex IV or leave blank")
        iv_help = QLabel("Leave empty to generate a random 8-byte IV automatically.")
        iv_help.setObjectName("helperText")
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
            f"Decrypt file encrypted with {self.algorithm_name}.",
        )
        dec_layout = QVBoxLayout()
        dec_layout.setSpacing(14)

        self.dec_key_pickers: list[PathPickerRow] = []
        for i in range(1, self.key_count + 1):
            p = PathPickerRow(
                f"Key {i} File (*.key)",
                f"Select DES key {i}",
                file_filter="Key Files (*.key);;All Files (*.*)",
            )
            self.dec_key_pickers.append(p)
            dec_layout.addWidget(p)

        self.dec_input_picker = PathPickerRow(
            "Encrypted Input File (*.enc)",
            "Select ciphertext file to decrypt",
            file_filter="Encrypted Files (*.enc);;All Files (*.*)",
        )
        self.dec_output_picker = PathPickerRow(
            "Output Directory (Optional)",
            "Leave blank for default storage/decrypted directory",
            is_folder=True,
        )

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

    def _create_keys_result_display(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("pathResultFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        frame.key_labels: list[QLabel] = []
        for i in range(1, self.key_count + 1):
            row = QHBoxLayout()
            lbl = QLabel(f"Key {i}:")
            lbl.setFixedWidth(60)
            lbl.setObjectName("pathResultLabel")
            val = QLabel("")
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            val.setObjectName("pathResultText")
            copy_btn = QPushButton("Copy")
            copy_btn.setObjectName("secondaryButton")
            copy_btn.setFixedHeight(24)
            copy_btn.setFixedWidth(54)
            copy_btn.clicked.connect(lambda checked=False, v=val: self._copy_clipboard(v.text()))

            row.addWidget(lbl)
            row.addWidget(val, stretch=1)
            row.addWidget(copy_btn)
            layout.addLayout(row)
            frame.key_labels.append(val)

        return frame

    def _copy_clipboard(self, text: str) -> None:
        if text:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)

    def _generate_keys(self) -> None:
        save_dir = self.key_save_folder.path()

        try:
            key_paths = self.des_service.generate_key(save_dir)
            path_strs = [str(p.resolve()) for p in key_paths]

            for i, p_str in enumerate(path_strs):
                self.key_results_frame.key_labels[i].setText(p_str)
                # Pre-fill encryption/decryption keys
                self.enc_key_pickers[i].set_text(p_str)
                self.dec_key_pickers[i].set_text(p_str)

            self.key_results_frame.show()

            get_activity_tracker().record(
                operation="Key Generation",
                algorithm=self.algorithm_name,
                target_path=key_paths[0],
                status="Success",
            )

            details_text = "\n".join(
                f"Key {i+1}: {p_str}" for i, p_str in enumerate(path_strs)
            )
            show_success(
                self,
                f"{self.algorithm_name} Keys Generated",
                f"Successfully generated {self.key_count} keys for {self.algorithm_name}.",
                details=details_text,
                theme=self._theme,
            )
        except Exception as exc:
            show_error(
                self,
                "Key Generation Failed",
                f"Unable to generate keys: {exc}",
                theme=self._theme,
            )

    def _encrypt_file(self) -> None:
        key_paths = [p.path() for p in self.enc_key_pickers]
        for i, kp in enumerate(key_paths, start=1):
            if not kp:
                show_warning(
                    self,
                    "Missing Key File",
                    f"Please select Key {i} before encrypting.",
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
            prefix = "DOUBLE_DES" if self.key_count == 2 else "TRIPLE_DES"
            output_dir = PROJECT_ROOT / "storage" / "encrypted" / prefix

        iv = self.enc_iv_input.text().strip() or None

        try:
            saved_path = self.des_service.encrypt(
                *key_paths,
                input_file_path=input_path,
                output_folder=output_dir,
                iv=iv,
            )
            path_str = str(saved_path.resolve())

            self.dec_input_picker.set_text(path_str)

            get_activity_tracker().record(
                operation="File Encryption",
                algorithm=self.algorithm_name,
                target_path=saved_path,
                status="Success",
            )

            show_success(
                self,
                "Encryption Successful",
                f"File '{input_path.name}' was encrypted using {self.algorithm_name}.",
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
        key_paths = [p.path() for p in self.dec_key_pickers]
        for i, kp in enumerate(key_paths, start=1):
            if not kp:
                show_warning(
                    self,
                    "Missing Key File",
                    f"Please select Key {i} before decrypting.",
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
            prefix = "DOUBLE_DES" if self.key_count == 2 else "TRIPLE_DES"
            output_dir = PROJECT_ROOT / "storage" / "decrypted" / prefix

        try:
            saved_path = self.des_service.decrypt(
                *key_paths,
                encrypted_file_path=input_path,
                output_folder=output_dir,
            )
            path_str = str(saved_path.resolve())

            get_activity_tracker().record(
                operation="File Decryption",
                algorithm=self.algorithm_name,
                target_path=saved_path,
                status="Success",
            )

            show_success(
                self,
                "Decryption Successful",
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
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_workspace_stylesheet(self._theme, "des"))
