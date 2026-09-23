from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

from crypto.double_des import DoubleDESService
from crypto.triple_des import TripleDESService
from gui.theme import DARK_THEME, ThemeName, get_workspace_stylesheet


class DESPage(QWidget):
    """DES workspace for key generation and file operations."""

    SERVICES = {
        "Double DES": (DoubleDESService, 2),
        "Triple DES": (TripleDESService, 3),
    }

    def __init__(self, algorithm_name: str) -> None:
        super().__init__()
        if algorithm_name not in self.SERVICES:
            raise ValueError(f"Unsupported DES algorithm: {algorithm_name}")

        self.algorithm_name = algorithm_name
        service_factory, self.key_count = self.SERVICES[algorithm_name]
        self.des_service = service_factory()

        self.setObjectName("desPage")
        self._theme = DARK_THEME
        self._build_layout()
        self._apply_styles()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("desScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("desContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 42, 48, 42)
        content_layout.setSpacing(24)
        content_layout.setAlignment(Qt.AlignTop)

        title = QLabel(f"{self.algorithm_name} Workspace")
        title.setObjectName("desTitle")

        subtitle = QLabel(
            f"Generate {self.algorithm_name} keys and prepare file encryption workflows."
        )
        subtitle.setObjectName("desSubtitle")

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addWidget(self._create_key_generation_group())
        content_layout.addWidget(self._create_encryption_group())
        content_layout.addWidget(self._create_decryption_group())
        content_layout.addStretch()

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

    def _create_key_generation_group(self) -> QGroupBox:
        group = QGroupBox(f"{self.algorithm_name} Key Generation")
        group.setMinimumHeight(144)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

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
        group.setMinimumHeight(268 + (self.key_count - 1) * 54)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.encrypt_key_inputs = self._create_key_inputs()

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

        self.iv_input = QLineEdit()
        self.iv_input.setPlaceholderText("Enter 8-byte IV")
        self.iv_helper = QLabel(
            "Optional. Leave empty to generate a secure random IV automatically."
        )
        self.iv_helper.setObjectName("helperText")
        self.iv_helper.setWordWrap(True)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(16)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)

        self._add_key_rows(form, self.encrypt_key_inputs)
        form.addRow(
            "Input File",
            self._create_path_row(self.input_file_input, input_file_browse),
        )
        form.addRow(
            "Output Folder",
            self._create_path_row(self.encrypt_output_folder_input, encrypt_output_browse),
        )
        form.addRow(
            "Initialization Vector (IV)",
            self._create_input_with_helper(self.iv_input, self.iv_helper),
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
        group.setMinimumHeight(212 + (self.key_count - 1) * 54)
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(22, 28, 22, 22)
        layout.setSpacing(18)

        self.decrypt_key_inputs = self._create_key_inputs()

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

        self._add_key_rows(form, self.decrypt_key_inputs)
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

    def _create_key_inputs(self) -> list[QLineEdit]:
        key_inputs = []
        for index in range(1, self.key_count + 1):
            key_input = QLineEdit()
            key_input.setPlaceholderText(f"Select {self.algorithm_name} key {index}")
            key_inputs.append(key_input)

        return key_inputs

    def _add_key_rows(self, form: QFormLayout, key_inputs: list[QLineEdit]) -> None:
        for index, key_input in enumerate(key_inputs, start=1):
            key_browse = self._create_browse_button()
            key_browse.clicked.connect(
                lambda checked=False, target=key_input: self._browse_file(target)
            )
            form.addRow(
                f"Key {index}",
                self._create_path_row(key_input, key_browse),
            )

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
        save_location = self.save_location_input.text().strip()
        save_directory = Path(save_location) if save_location else None

        try:
            key_paths = self.des_service.generate_key(save_directory)
            key_details = "\n\n".join(
                f"Key {index}:\n{key_path.resolve()}"
                for index, key_path in enumerate(key_paths, start=1)
            )
            QMessageBox.information(
                self,
                f"{self.algorithm_name} Keys Generated",
                f"{self.algorithm_name} keys generated successfully.\n\n"
                f"{key_details}",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                f"{self.algorithm_name} Key Generation Failed",
                str(exc),
            )

    def _encrypt_file(self) -> None:
        try:
            saved_path = self.des_service.encrypt(
                *self._key_paths_from_inputs(self.encrypt_key_inputs),
                self._path_from_input(self.input_file_input, "Input file"),
                self._path_from_input(self.encrypt_output_folder_input, "Output folder"),
                self._optional_text_from_input(self.iv_input),
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
            saved_path = self.des_service.decrypt(
                *self._key_paths_from_inputs(self.decrypt_key_inputs),
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

    def _key_paths_from_inputs(self, key_inputs: list[QLineEdit]) -> list[Path]:
        return [
            self._path_from_input(key_input, f"Key {index}")
            for index, key_input in enumerate(key_inputs, start=1)
        ]

    def _path_from_input(self, line_edit: QLineEdit, field_name: str) -> Path:
        path_text = line_edit.text().strip()
        if not path_text:
            raise ValueError(f"{field_name} is required.")

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
        self.setStyleSheet(get_workspace_stylesheet(self._theme, "des"))
