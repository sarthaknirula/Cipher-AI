"""Modal dialogs with clean high-contrast styling and theme support."""

from typing import Literal
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.theme import DARK_THEME, ThemeName, get_palette

DialogType = Literal["success", "error", "warning", "info"]


class CyberDialog(QDialog):
    """Modern modal dialog with high-contrast text, technical tag, and theme support."""

    TAGS = {
        "success": ("SUCCESS", "#10B981", "rgba(16, 185, 129, 0.12)"),
        "error": ("ERROR", "#EF4444", "rgba(239, 68, 68, 0.12)"),
        "warning": ("WARNING", "#F59E0B", "rgba(245, 158, 11, 0.12)"),
        "info": ("INFO", "#0EA5E9", "rgba(14, 165, 233, 0.12)"),
    }

    def __init__(
        self,
        parent: QWidget | None,
        dialog_type: DialogType,
        title: str,
        message: str,
        details: str | None = None,
        theme: ThemeName = DARK_THEME,
    ) -> None:
        super().__init__(parent)
        self.dialog_type = dialog_type
        self.dialog_title = title
        self.message_text = message
        self.details_text = details
        self.theme = theme

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setMaximumWidth(600)
        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        header_row.setAlignment(Qt.AlignVCenter)

        tag_text, color, bg_color = self.TAGS.get(
            self.dialog_type, self.TAGS["info"]
        )

        tag_badge = QLabel(tag_text)
        tag_badge.setFixedHeight(24)
        tag_badge.setAlignment(Qt.AlignCenter)
        tag_badge.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg_color};
                color: {color};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                border-radius: 4px;
                border: 1px solid {color};
                padding: 0px 8px;
            }}
            """
        )
        header_row.addWidget(tag_badge)

        self.title_label = QLabel(self.dialog_title)
        self.title_label.setObjectName("dialogTitleLabel")
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        self.title_label.setWordWrap(True)
        header_row.addWidget(self.title_label, stretch=1)

        layout.addLayout(header_row)

        # Message body
        self.body_label = QLabel(self.message_text)
        self.body_label.setObjectName("dialogBodyLabel")
        self.body_label.setWordWrap(True)
        self.body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.body_label.setStyleSheet("font-size: 13px; line-height: 1.5;")
        layout.addWidget(self.body_label)

        # Optional details area
        if self.details_text:
            details_frame = QFrame()
            details_frame.setObjectName("dialogDetailsFrame")
            details_layout = QVBoxLayout(details_frame)
            details_layout.setContentsMargins(14, 10, 14, 10)
            details_layout.setSpacing(6)

            details_header = QHBoxLayout()
            details_title = QLabel("OUTPUT / PATH DETAILS")
            details_title.setStyleSheet(
                "font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #64748B;"
            )
            details_header.addWidget(details_title)
            details_header.addStretch()

            copy_btn = QPushButton("Copy Details")
            copy_btn.setObjectName("secondaryButton")
            copy_btn.setFixedHeight(26)
            copy_btn.setFixedWidth(88)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.clicked.connect(self._copy_details)
            details_header.addWidget(copy_btn)

            details_layout.addLayout(details_header)

            details_box = QTextEdit()
            details_box.setReadOnly(True)
            details_box.setPlainText(self.details_text)
            details_box.setFixedHeight(76)
            details_box.setStyleSheet(
                "font-family: 'Consolas', 'Courier New', monospace; font-size: 12px;"
            )
            details_layout.addWidget(details_box)

            layout.addWidget(details_frame)

        # Button row
        button_row = QHBoxLayout()
        button_row.addStretch()

        ok_button = QPushButton("OK")
        ok_button.setObjectName("primaryButton")
        ok_button.setCursor(Qt.PointingHandCursor)
        ok_button.setMinimumWidth(94)
        ok_button.setFixedHeight(34)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        button_row.addWidget(ok_button)

        layout.addLayout(button_row)

    def _copy_details(self) -> None:
        if self.details_text:
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(self.details_text)

    def _apply_styles(self) -> None:
        colors = get_palette(self.theme)
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {colors["bg_surface"]};
                border: 1px solid {colors["border_normal"]};
                border-radius: 8px;
            }}
            QLabel#dialogTitleLabel {{
                color: {colors["text_primary"]};
            }}
            QLabel#dialogBodyLabel {{
                color: {colors["text_secondary"]};
            }}
            QFrame#dialogDetailsFrame {{
                background-color: {colors["bg_input"]};
                border: 1px solid {colors["border_subtle"]};
                border-radius: 6px;
            }}
            QTextEdit {{
                background-color: transparent;
                color: {colors["text_primary"]};
                border: none;
            }}
            QPushButton#primaryButton {{
                background-color: {colors["primary"]};
                color: #FFFFFF;
                border: 1px solid {colors["primary"]};
                border-radius: 6px;
                font-weight: 700;
                padding: 6px 16px;
            }}
            QPushButton#primaryButton:hover {{
                background-color: {colors["primary_hover"]};
                border-color: {colors["primary_hover"]};
            }}
            QPushButton#secondaryButton {{
                background-color: {colors["secondary_bg"]};
                color: {colors["secondary_text"]};
                border: 1px solid {colors["border_normal"]};
                border-radius: 6px;
                font-weight: 600;
                padding: 6px 14px;
            }}
            QPushButton#secondaryButton:hover {{
                background-color: {colors["secondary_hover"]};
                color: {colors["text_primary"]};
                border-color: {colors["border_focus"]};
            }}
            """
        )


def show_success(
    parent: QWidget | None,
    title: str,
    message: str,
    details: str | None = None,
    theme: ThemeName = DARK_THEME,
) -> None:
    dialog = CyberDialog(parent, "success", title, message, details, theme)
    dialog.exec()


def show_error(
    parent: QWidget | None,
    title: str,
    message: str,
    details: str | None = None,
    theme: ThemeName = DARK_THEME,
) -> None:
    dialog = CyberDialog(parent, "error", title, message, details, theme)
    dialog.exec()


def show_warning(
    parent: QWidget | None,
    title: str,
    message: str,
    details: str | None = None,
    theme: ThemeName = DARK_THEME,
) -> None:
    dialog = CyberDialog(parent, "warning", title, message, details, theme)
    dialog.exec()


def show_info(
    parent: QWidget | None,
    title: str,
    message: str,
    details: str | None = None,
    theme: ThemeName = DARK_THEME,
) -> None:
    dialog = CyberDialog(parent, "info", title, message, details, theme)
    dialog.exec()
