"""Reusable UI components for CipherAI cybersecurity workstation."""

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QGuiApplication,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.theme import DARK_THEME, ThemeName, get_palette


def create_cipher_shield_pixmap(size: int = 32, is_dark: bool = True) -> QPixmap:
    """Render a self-contained cybersecurity shield emblem in memory without external asset files."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    scale = size / 32.0

    # Shield outer boundary
    shield_path = QPainterPath()
    shield_path.moveTo(16.0 * scale, 2.0 * scale)
    shield_path.lineTo(28.0 * scale, 6.0 * scale)
    shield_path.quadTo(28.0 * scale, 21.0 * scale, 16.0 * scale, 29.5 * scale)
    shield_path.quadTo(4.0 * scale, 21.0 * scale, 4.0 * scale, 6.0 * scale)
    shield_path.closeSubpath()

    # Outer shield fill & stroke
    shield_color = QColor("#0284C7" if is_dark else "#0369A1")
    shield_fill = QColor("#0E2238" if is_dark else "#E0F2FE")
    painter.setBrush(QBrush(shield_fill))
    painter.setPen(QPen(shield_color, 1.8 * scale))
    painter.drawPath(shield_path)

    # Inner lock / cipher keyhole
    lock_color = QColor("#38BDF8" if is_dark else "#0284C7")
    painter.setBrush(QBrush(lock_color))
    painter.setPen(Qt.NoPen)

    # Keyhole circular top
    painter.drawEllipse(
        QRectF(13.2 * scale, 10.5 * scale, 5.6 * scale, 5.6 * scale)
    )

    # Keyhole trapezoid stem
    stem_path = QPainterPath()
    stem_path.moveTo(14.2 * scale, 14.5 * scale)
    stem_path.lineTo(17.8 * scale, 14.5 * scale)
    stem_path.lineTo(18.6 * scale, 21.0 * scale)
    stem_path.lineTo(13.4 * scale, 21.0 * scale)
    stem_path.closeSubpath()
    painter.drawPath(stem_path)

    painter.end()
    return pixmap


def create_app_icon() -> QIcon:
    """Create a high-resolution multi-size application icon completely in-memory."""
    icon = QIcon()
    for s in (16, 24, 32, 48, 64, 128):
        icon.addPixmap(create_cipher_shield_pixmap(s, is_dark=True))
    return icon


class StatusBadge(QFrame):
    """Clean technical status badge with glowing state dot."""

    def __init__(
        self,
        text: str,
        status: str = "success",  # "success", "warning", "info", "danger", "neutral"
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("statusBadge")
        self.setFixedHeight(24)

        colors = {
            "success": ("#10B981", "rgba(16, 185, 129, 0.12)"),
            "warning": ("#F59E0B", "rgba(245, 158, 11, 0.12)"),
            "info": ("#0EA5E9", "rgba(14, 165, 233, 0.12)"),
            "danger": ("#EF4444", "rgba(239, 68, 68, 0.12)"),
            "neutral": ("#94A3B8", "rgba(148, 163, 184, 0.12)"),
        }
        color, bg = colors.get(status, colors["info"])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)

        dot = QFrame()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(
            f"background-color: {color}; border-radius: 3px;"
        )

        label = QLabel(text.upper())
        label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;"
        )

        layout.addWidget(dot)
        layout.addWidget(label)

        self.setStyleSheet(
            f"""
            QFrame#statusBadge {{
                background-color: {bg};
                border: 1px solid {color};
                border-radius: 12px;
            }}
            """
        )


class SpecPill(QFrame):
    """Compact technical specification pill (e.g., Mode: CBC, Block: 128-bit)."""

    def __init__(
        self,
        key: str,
        value: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("specPill")
        self.setFixedHeight(26)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)

        k_lbl = QLabel(key.upper())
        k_lbl.setObjectName("specPillKey")
        v_lbl = QLabel(value)
        v_lbl.setObjectName("specPillVal")

        layout.addWidget(k_lbl)
        layout.addWidget(v_lbl)


class PageHeader(QWidget):
    """Standardized top header bar across all application workspaces."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        badge_text: str = "Ready",
        badge_status: str = "success",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("pageHeader")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(16)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("headerTitle")

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("headerSubtitle")

        text_col.addWidget(self.title_label)
        text_col.addWidget(self.subtitle_label)

        layout.addLayout(text_col, stretch=1)

        self.badge = StatusBadge(badge_text, badge_status)
        layout.addWidget(self.badge, alignment=Qt.AlignVCenter)

    def set_badge(self, text: str, status: str = "success") -> None:
        self.badge.deleteLater()
        self.badge = StatusBadge(text, status, self)
        self.layout().addWidget(self.badge, alignment=Qt.AlignVCenter)


class CyberCard(QFrame):
    """Technical card container with title, subtitle, and structured content area."""

    def __init__(
        self,
        title: str,
        subtitle: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("cyberCard")

        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(22, 18, 22, 18)
        self.card_layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        header_text.addWidget(self.title_label)

        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("cardSubtitle")
            header_text.addWidget(self.subtitle_label)

        header_row.addLayout(header_text, stretch=1)
        self.card_layout.addLayout(header_row)

    def add_widget(self, widget: QWidget) -> None:
        self.card_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        self.card_layout.addLayout(layout)


class PathPickerRow(QWidget):
    """File or folder selection input with clear indication of required/optional status."""

    path_changed = Signal(str)

    def __init__(
        self,
        label: str,
        placeholder: str,
        is_folder: bool = False,
        file_filter: str = "All Files (*.*)",
        required: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.is_folder = is_folder
        self.file_filter = file_filter
        self.required = required

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label_row = QHBoxLayout()
        label_row.setSpacing(6)

        lbl = QLabel(label)
        lbl.setObjectName("fieldLabel")
        label_row.addWidget(lbl)
        label_row.addStretch()

        layout.addLayout(label_row)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.textChanged.connect(self._on_text_changed)
        row.addWidget(self.line_edit, stretch=1)

        self.clear_btn = QPushButton("✕")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.setToolTip("Clear Path")
        self.clear_btn.setFixedSize(28, 34)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear)
        self.clear_btn.hide()
        row.addWidget(self.clear_btn)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setObjectName("secondaryButton")
        self.browse_btn.setFixedWidth(84)
        self.browse_btn.setFixedHeight(34)
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self._browse)
        row.addWidget(self.browse_btn)

        layout.addLayout(row)

    def _on_text_changed(self, text: str) -> None:
        self.clear_btn.setVisible(bool(text.strip()))
        self.path_changed.emit(text)

    def _browse(self) -> None:
        if self.is_folder:
            folder = QFileDialog.getExistingDirectory(self, "Select Folder")
            if folder:
                self.line_edit.setText(folder)
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File", "", self.file_filter
            )
            if file_path:
                self.line_edit.setText(file_path)

    def text(self) -> str:
        return self.line_edit.text().strip()

    def set_text(self, text: str) -> None:
        self.line_edit.setText(text)

    def path(self) -> Path | None:
        t = self.text()
        return Path(t) if t else None

    def clear(self) -> None:
        self.line_edit.clear()


class SegmentedSelector(QWidget):
    """Segmented toggle button group for discrete technical settings."""

    selection_changed = Signal(str)

    def __init__(
        self,
        options: list[str],
        default_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._theme: ThemeName = DARK_THEME
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.button_group = QButtonGroup(self)
        self.buttons: list[QPushButton] = []

        for index, opt in enumerate(options):
            btn = QPushButton(opt)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.setMinimumWidth(80)
            if index == default_index:
                btn.setChecked(True)

            self.button_group.addButton(btn, index)
            self.buttons.append(btn)
            layout.addWidget(btn)

        self.button_group.idClicked.connect(self._on_click)
        self.apply_theme(DARK_THEME)

    def _on_click(self, btn_id: int) -> None:
        self._update_styles()
        btn = self.button_group.button(btn_id)
        if btn:
            self.selection_changed.emit(btn.text())

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self._update_styles()

    def _update_styles(self) -> None:
        colors = get_palette(self._theme)
        for btn in self.buttons:
            if btn.isChecked():
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {colors["primary"]};
                        color: #FFFFFF;
                        font-weight: 700;
                        border: 1px solid {colors["primary"]};
                        border-radius: 6px;
                    }}
                    """
                )
            else:
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {colors["secondary_bg"]};
                        color: {colors["secondary_text"]};
                        font-weight: 600;
                        border: 1px solid {colors["border_normal"]};
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {colors["secondary_hover"]};
                        color: {colors["text_primary"]};
                        border-color: {colors["border_focus"]};
                    }}
                    """
                )

    def current_value(self) -> str:
        btn = self.button_group.checkedButton()
        return btn.text() if btn else ""


class EmptyState(QFrame):
    """Technical empty state widget without external icons."""

    def __init__(
        self,
        icon: str | None,
        title: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("emptyStateFrame")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 36, 28, 36)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        glyph_lbl = QLabel("◈")
        glyph_lbl.setStyleSheet(
            "font-size: 26px; color: #0284C7; font-weight: 700;"
        )
        glyph_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(glyph_lbl)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("emptyTitle")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("emptyDesc")
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)
