from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from crypto.rsa import RSAService
from gui.theme import DARK_THEME, ThemeName, get_workspace_stylesheet


class RSAPage(QWidget):
    """RSA workspace for key generation and file operations."""

    MILESTONE_MESSAGE = "Functionality will be implemented in Milestone 3."

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("rsaPage")
        self._theme = DARK_THEME
        self.rsa_service = RSAService()
        self._build_layout()
        self._apply_styles()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("rsaScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("rsaContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 42, 48, 42)
        content_layout.setSpacing(24)
        content_layout.setAlignment(Qt.AlignTop)

        title = QLabel("RSA Workspace")
        title.setObjectName("rsaTitle")

        subtitle = QLabel("Generate RSA key pairs and prepare file encryption workflows.")
        subtitle.setObjectName("rsaSubtitle")

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addWidget(self._create_key_generation_group())
        content_layout.addWidget(self._create_encryption_group())
        content_layout.addWidget(self._create_decryption_group())
        content_layout.addStretch()

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

    def _create_key_generation_group(self) -> QGroupBox:
        group = QGroupBox("RSA Key Generation")
        group.setMinimumHeight(188)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        key_size_label = QLabel("Key Size")
        key_size_label.setObjectName("fieldLabel")

        key_size_layout = QHBoxLayout()
        key_size_layout.setContentsMargins(0, 0, 0, 0)
        key_size_layout.setSpacing(34)

        self.key_size_group = QButtonGroup(self)
        for size in ("2048", "3072", "4096"):
            button = QRadioButton(size)
            button.setCursor(Qt.PointingHandCursor)
            button.setChecked(size == "4096")
            button.setFixedWidth(96)
            button.setMinimumHeight(28)
            self.key_size_group.addButton(button)
            key_size_layout.addWidget(button)
        key_size_layout.addStretch()

        self.save_location_input = QLineEdit()
        self.save_location_input.setPlaceholderText("Select folder for generated keys")

        browse_save_button = self._create_browse_button()
        browse_save_button.clicked.connect(
            lambda: self._browse_folder(self.save_location_input)
        )

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(16)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form.addRow(key_size_label, key_size_layout)
        form.addRow(
            "Save Location",
            self._create_path_row(self.save_location_input, browse_save_button),
        )

        generate_button = QPushButton("Generate Keys")
        generate_button.setObjectName("primaryButton")
        generate_button.setCursor(Qt.PointingHandCursor)
        generate_button.clicked.connect(self._generate_keys)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(generate_button)

        layout.addLayout(form)
        layout.addLayout(button_row)
        return group

    def _create_encryption_group(self) -> QGroupBox:
        group = QGroupBox("File Encryption")
        group.setMinimumHeight(212)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.public_key_input = QLineEdit()
        self.public_key_input.setPlaceholderText("Select RSA public key")
        public_key_browse = self._create_browse_button()
        public_key_browse.clicked.connect(lambda: self._browse_file(self.public_key_input))

        self.input_file_input = QLineEdit()
        self.input_file_input.setPlaceholderText("Select file to encrypt")
        input_file_browse = self._create_browse_button()
        input_file_browse.clicked.connect(lambda: self._browse_file(self.input_file_input))

        self.encrypt_output_folder_input = QLineEdit()
        self.encrypt_output_folder_input.setPlaceholderText("Select encrypted output folder")
        encrypt_output_browse = self._create_browse_button()
        encrypt_output_browse.clicked.connect(
            lambda: self._browse_folder(self.encrypt_output_folder_input)
        )

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(16)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form.addRow(
            "Public Key",
            self._create_path_row(self.public_key_input, public_key_browse),
        )
        form.addRow(
            "Input File",
            self._create_path_row(self.input_file_input, input_file_browse),
        )
        form.addRow(
            "Output Folder",
            self._create_path_row(self.encrypt_output_folder_input, encrypt_output_browse),
        )

        encrypt_button = QPushButton("Encrypt")
        encrypt_button.setObjectName("primaryButton")
        encrypt_button.setCursor(Qt.PointingHandCursor)
        encrypt_button.clicked.connect(self._encrypt_file)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(encrypt_button)

        layout.addLayout(form)
        layout.addLayout(button_row)
        return group

    def _create_decryption_group(self) -> QGroupBox:
        group = QGroupBox("File Decryption")
        group.setMinimumHeight(212)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.private_key_input = QLineEdit()
        self.private_key_input.setPlaceholderText("Select RSA private key")
        private_key_browse = self._create_browse_button()
        private_key_browse.clicked.connect(lambda: self._browse_file(self.private_key_input))

        self.encrypted_file_input = QLineEdit()
        self.encrypted_file_input.setPlaceholderText("Select encrypted file")
        encrypted_file_browse = self._create_browse_button()
        encrypted_file_browse.clicked.connect(
            lambda: self._browse_file(self.encrypted_file_input)
        )

        self.decrypt_output_folder_input = QLineEdit()
        self.decrypt_output_folder_input.setPlaceholderText("Select decrypted output folder")
        decrypt_output_browse = self._create_browse_button()
        decrypt_output_browse.clicked.connect(
            lambda: self._browse_folder(self.decrypt_output_folder_input)
        )

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(16)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        form.addRow(
            "Private Key",
            self._create_path_row(self.private_key_input, private_key_browse),
        )
        form.addRow(
            "Encrypted File",
            self._create_path_row(self.encrypted_file_input, encrypted_file_browse),
        )
        form.addRow(
            "Output Folder",
            self._create_path_row(self.decrypt_output_folder_input, decrypt_output_browse),
        )

        decrypt_button = QPushButton("Decrypt")
        decrypt_button.setObjectName("primaryButton")
        decrypt_button.setCursor(Qt.PointingHandCursor)
        decrypt_button.clicked.connect(self._decrypt_file)

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(decrypt_button)

        layout.addLayout(form)
        layout.addLayout(button_row)
        return group

    def _create_path_row(self, line_edit: QLineEdit, browse_button: QPushButton) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(line_edit, stretch=1)
        layout.addWidget(browse_button)
        return row

    def _create_browse_button(self) -> QPushButton:
        button = QPushButton("Browse")
        button.setObjectName("secondaryButton")
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _browse_file(self, target: QLineEdit) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            target.setText(file_path)

    def _browse_folder(self, target: QLineEdit) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            target.setText(folder_path)

    def _generate_keys(self) -> None:
        selected_button = self.key_size_group.checkedButton()
        key_size = int(selected_button.text()) if selected_button else 4096

        save_location = self.save_location_input.text().strip()
        save_directory = Path(save_location) if save_location else None

        try:
            public_key_path, private_key_path = self.rsa_service.generate_key_pair(
                key_size,
                save_directory,
            )
            QMessageBox.information(
                self,
                "RSA Keys Generated",
                f"RSA {key_size}-bit key pair generated successfully.\n\n"
                f"Key Size:\n{key_size}-bit\n\n"
                f"Public Key:\n{public_key_path.resolve()}\n\n"
                f"Private Key:\n{private_key_path.resolve()}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "RSA Key Generation Failed", str(exc))

    def _encrypt_file(self) -> None:
        try:
            saved_path = self.rsa_service.encrypt_file(
                self._path_from_input(self.public_key_input, "Public key"),
                self._path_from_input(self.input_file_input, "Input file"),
                self._path_from_input(self.encrypt_output_folder_input, "Output folder"),
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
        try:
            saved_path = self.rsa_service.decrypt_file(
                self._path_from_input(self.private_key_input, "Private key"),
                self._path_from_input(self.encrypted_file_input, "Encrypted file"),
                self._path_from_input(self.decrypt_output_folder_input, "Output folder"),
            )
            QMessageBox.information(
                self,
                "Decryption Successful",
                "File decrypted successfully.\n\n"
                f"Saved to:\n{saved_path.resolve()}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Decryption Failed", str(exc))

    def _path_from_input(self, line_edit: QLineEdit, field_name: str) -> Path:
        path_text = line_edit.text().strip()
        if not path_text:
            raise ValueError(f"{field_name} is required.")

        return Path(path_text)

    def _show_milestone_message(self) -> None:
        QMessageBox.information(self, "Milestone 3", self.MILESTONE_MESSAGE)

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_workspace_stylesheet(self._theme, "rsa"))
