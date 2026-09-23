from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from crypto.aes import AESService
from gui.theme import DARK_THEME, ThemeName, get_workspace_stylesheet


class AESPage(QWidget):
    """AES workspace for key generation and file operations."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("aesPage")
        self._theme = DARK_THEME
        self.service = AESService()
        self._build_layout()
        self._apply_styles()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("aesScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("aesContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 42, 48, 42)
        content_layout.setSpacing(24)
        content_layout.setAlignment(Qt.AlignTop)

        self.header_label = QLabel("AES Workspace")
        self.header_label.setObjectName("aesTitle")

        self.subtitle_label = QLabel(
            "Generate AES Keys and prepare AES encryption workflows."
        )
        self.subtitle_label.setObjectName("aesSubtitle")

        content_layout.addWidget(self.header_label)
        content_layout.addWidget(self.subtitle_label)
        content_layout.addWidget(self._create_key_generation_group())
        content_layout.addWidget(self._create_encryption_group())
        content_layout.addWidget(self._create_decryption_group())
        content_layout.addStretch()

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

    def _create_key_generation_group(self) -> QGroupBox:
        group = QGroupBox("AES Key Generation")
        group.setMinimumHeight(188)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.key_size_label = QLabel("Key Size")
        self.key_size_label.setObjectName("fieldLabel")

        self.key_size_combo = QComboBox()
        self.key_size_combo.addItems(["128", "192", "256"])
        self.key_size_combo.setCursor(Qt.PointingHandCursor)

        self.save_folder_label = QLabel("Save Location")
        self.save_folder_line_edit = QLineEdit()
        self.save_folder_line_edit.setPlaceholderText("Select folder for generated keys")

        self.save_folder_browse_button = self._create_browse_button()
        self.save_folder_browse_button.clicked.connect(self._browse_generate_key_folder)

        form = self._create_form_layout()
        form.addRow(self.key_size_label, self.key_size_combo)
        form.addRow(
            self.save_folder_label,
            self._create_path_row(
                self.save_folder_line_edit,
                self.save_folder_browse_button,
            ),
        )

        self.generate_key_button = QPushButton("Generate Keys")
        self.generate_key_button.setObjectName("primaryButton")
        self.generate_key_button.setCursor(Qt.PointingHandCursor)
        self.generate_key_button.clicked.connect(self._generate_key)

        layout.addLayout(form)
        layout.addLayout(self._create_action_row(self.generate_key_button))
        return group

    def _create_encryption_group(self) -> QGroupBox:
        group = QGroupBox("File Encryption")
        group.setMinimumHeight(268)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.enc_key_file_label = QLabel("Key File")
        self.enc_key_file_line_edit = QLineEdit()
        self.enc_key_file_line_edit.setPlaceholderText("Select AES key file")
        self.enc_key_file_browse_button = self._create_browse_button()
        self.enc_key_file_browse_button.clicked.connect(self._browse_encryption_key_file)

        self.enc_input_file_label = QLabel("Input File")
        self.enc_input_file_line_edit = QLineEdit()
        self.enc_input_file_line_edit.setPlaceholderText("Select file to encrypt")
        self.enc_input_file_browse_button = self._create_browse_button()
        self.enc_input_file_browse_button.clicked.connect(
            self._browse_encryption_input_file
        )

        self.enc_output_folder_label = QLabel("Output Folder")
        self.enc_output_folder_line_edit = QLineEdit()
        self.enc_output_folder_line_edit.setPlaceholderText(
            "Select encrypted output folder"
        )
        self.enc_output_folder_browse_button = self._create_browse_button()
        self.enc_output_folder_browse_button.clicked.connect(
            self._browse_encryption_output_folder
        )

        self.enc_iv_label = QLabel("Initialization Vector (IV)")
        self.enc_iv_line_edit = QLineEdit()
        self.enc_iv_line_edit.setPlaceholderText("Enter 16-byte IV")
        self.enc_iv_helper_label = QLabel(
            "Optional. Leave empty to generate a secure random IV automatically."
        )
        self.enc_iv_helper_label.setObjectName("helperText")
        self.enc_iv_helper_label.setWordWrap(True)

        form = self._create_form_layout()
        form.addRow(
            self.enc_key_file_label,
            self._create_path_row(
                self.enc_key_file_line_edit,
                self.enc_key_file_browse_button,
            ),
        )
        form.addRow(
            self.enc_input_file_label,
            self._create_path_row(
                self.enc_input_file_line_edit,
                self.enc_input_file_browse_button,
            ),
        )
        form.addRow(
            self.enc_output_folder_label,
            self._create_path_row(
                self.enc_output_folder_line_edit,
                self.enc_output_folder_browse_button,
            ),
        )
        form.addRow(
            self.enc_iv_label,
            self._create_input_with_helper(
                self.enc_iv_line_edit,
                self.enc_iv_helper_label,
            ),
        )

        self.encrypt_file_button = QPushButton("Encrypt")
        self.encrypt_file_button.setObjectName("primaryButton")
        self.encrypt_file_button.setCursor(Qt.PointingHandCursor)
        self.encrypt_file_button.clicked.connect(self._encrypt_file)

        layout.addLayout(form)
        layout.addLayout(self._create_action_row(self.encrypt_file_button))
        return group

    def _create_decryption_group(self) -> QGroupBox:
        group = QGroupBox("File Decryption")
        group.setMinimumHeight(212)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.dec_key_file_label = QLabel("Key File")
        self.dec_key_file_line_edit = QLineEdit()
        self.dec_key_file_line_edit.setPlaceholderText("Select AES key file")
        self.dec_key_file_browse_button = self._create_browse_button()
        self.dec_key_file_browse_button.clicked.connect(self._browse_decryption_key_file)

        self.dec_input_file_label = QLabel("Encrypted File")
        self.dec_input_file_line_edit = QLineEdit()
        self.dec_input_file_line_edit.setPlaceholderText("Select encrypted file")
        self.dec_input_file_browse_button = self._create_browse_button()
        self.dec_input_file_browse_button.clicked.connect(
            self._browse_decryption_input_file
        )

        self.dec_output_folder_label = QLabel("Output Folder")
        self.dec_output_folder_line_edit = QLineEdit()
        self.dec_output_folder_line_edit.setPlaceholderText(
            "Select decrypted output folder"
        )
        self.dec_output_folder_browse_button = self._create_browse_button()
        self.dec_output_folder_browse_button.clicked.connect(
            self._browse_decryption_output_folder
        )

        form = self._create_form_layout()
        form.addRow(
            self.dec_key_file_label,
            self._create_path_row(
                self.dec_key_file_line_edit,
                self.dec_key_file_browse_button,
            ),
        )
        form.addRow(
            self.dec_input_file_label,
            self._create_path_row(
                self.dec_input_file_line_edit,
                self.dec_input_file_browse_button,
            ),
        )
        form.addRow(
            self.dec_output_folder_label,
            self._create_path_row(
                self.dec_output_folder_line_edit,
                self.dec_output_folder_browse_button,
            ),
        )

        self.decrypt_file_button = QPushButton("Decrypt")
        self.decrypt_file_button.setObjectName("primaryButton")
        self.decrypt_file_button.setCursor(Qt.PointingHandCursor)
        self.decrypt_file_button.clicked.connect(self._decrypt_file)

        layout.addLayout(form)
        layout.addLayout(self._create_action_row(self.decrypt_file_button))
        return group

    def _create_form_layout(self) -> QFormLayout:
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(16)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)

        return form

    def _create_path_row(self, line_edit: QLineEdit, browse_button: QPushButton) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(line_edit, stretch=1)
        layout.addWidget(browse_button)

        return row

    def _create_input_with_helper(self, line_edit: QLineEdit, helper_label: QLabel) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(line_edit)
        layout.addWidget(helper_label)

        return wrapper

    def _create_action_row(self, button: QPushButton) -> QHBoxLayout:
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(button)

        return button_row

    def _create_browse_button(self) -> QPushButton:
        button = QPushButton("Browse")
        button.setObjectName("secondaryButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedWidth(92)

        return button

    def _browse_file(self, target: QLineEdit) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            target.setText(file_path)

    def _browse_folder(self, target: QLineEdit) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            target.setText(folder_path)

    def _browse_encryption_key_file(self) -> None:
        self._browse_file(self.enc_key_file_line_edit)

    def _browse_encryption_input_file(self) -> None:
        self._browse_file(self.enc_input_file_line_edit)

    def _browse_encryption_output_folder(self) -> None:
        self._browse_folder(self.enc_output_folder_line_edit)

    def _browse_decryption_key_file(self) -> None:
        self._browse_file(self.dec_key_file_line_edit)

    def _browse_decryption_input_file(self) -> None:
        self._browse_file(self.dec_input_file_line_edit)

    def _browse_decryption_output_folder(self) -> None:
        self._browse_folder(self.dec_output_folder_line_edit)

    def _browse_generate_key_folder(self) -> None:
        self._browse_folder(self.save_folder_line_edit)

    def _generate_key(self) -> None:
        key_size = int(self.key_size_combo.currentText())
        save_directory = self._optional_path_from_input(self.save_folder_line_edit)

        try:
            key_path = self.service.generate_key(key_size, save_directory)
            QMessageBox.information(
                self,
                "AES Key Generated",
                f"AES {key_size}-bit key generated successfully.\n\n"
                f"Key File:\n{key_path.resolve()}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "AES Key Generation Failed", str(exc))

    def _encrypt_file(self) -> None:
        key_path = self._required_path_from_input(
            self.enc_key_file_line_edit,
            "Key file",
        )
        if key_path is None:
            return

        input_file_path = self._required_path_from_input(
            self.enc_input_file_line_edit,
            "Input file",
        )
        if input_file_path is None:
            return

        output_folder = self._optional_path_from_input(
            self.enc_output_folder_line_edit
        )
        iv = self._optional_text_from_input(self.enc_iv_line_edit)

        try:
            saved_path = self.service.encrypt(
                key_path,
                input_file_path,
                output_folder,
                iv,
            )
            QMessageBox.information(
                self,
                "Encryption Successful",
                "File encrypted successfully.\n\n"
                f"Saved to:\n{saved_path.resolve()}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Encryption Failed", str(exc))

    def _decrypt_file(self) -> None:
        key_path = self._required_path_from_input(
            self.dec_key_file_line_edit,
            "Key file",
        )
        if key_path is None:
            return

        encrypted_file_path = self._required_path_from_input(
            self.dec_input_file_line_edit,
            "Encrypted file",
        )
        if encrypted_file_path is None:
            return

        output_folder = self._optional_path_from_input(
            self.dec_output_folder_line_edit
        )

        try:
            saved_path = self.service.decrypt(
                key_path,
                encrypted_file_path,
                output_folder,
            )
            QMessageBox.information(
                self,
                "Decryption Successful",
                "File decrypted successfully.\n\n"
                f"Saved to:\n{saved_path.resolve()}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Decryption Failed", str(exc))

    def _required_path_from_input(
        self,
        line_edit: QLineEdit,
        field_name: str,
    ) -> Path | None:
        path_text = line_edit.text().strip()
        if not path_text:
            QMessageBox.warning(self, "Missing Required Input", f"{field_name} is required.")
            line_edit.setFocus()
            return None

        return Path(path_text)

    def _optional_path_from_input(self, line_edit: QLineEdit) -> Path | None:
        path_text = line_edit.text().strip()
        if not path_text:
            return None

        return Path(path_text)

    def _optional_text_from_input(self, line_edit: QLineEdit) -> str | None:
        text = line_edit.text()
        if not text:
            return None

        return text

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_workspace_stylesheet(self._theme, "aes"))
