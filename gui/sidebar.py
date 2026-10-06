"""Persistent left sidebar navigation for CipherAI."""

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.theme import DARK_THEME, ThemeName, get_palette

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NavButton(QPushButton):
    """Clean navigation button with active state."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("sidebarNavButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(38)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class Sidebar(QFrame):
    """Left navigation panel with brand header, categorized pages, and system status."""

    page_selected = Signal(str)

    NAV_ITEMS = [
        ("dashboard", "Dashboard", False),
        ("ai_assistant", "AI Assistant", False),
        ("section_crypto", "CRYPTOGRAPHY", True),
        ("aes", "AES", False),
        ("rsa", "RSA", False),
        ("double_des", "Double DES", False),
        ("triple_des", "Triple DES", False),
        ("section_system", "WORKSPACE", True),
        ("files", "Files", False),
        ("settings", "Settings", False),
        ("about", "About", False),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self._buttons: dict[str, NavButton] = {}
        self._active_key = "dashboard"
        self._theme = DARK_THEME

        self._build_ui()
        self.apply_theme(DARK_THEME)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(4)

        # Brand header
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(4, 2, 4, 12)
        brand_row.setSpacing(10)

        logo_path = PROJECT_ROOT / "assets" / "logo" / "logo.png"
        logo_label = QLabel()
        logo_label.setFixedSize(28, 28)
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(
                28,
                28,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("C")
            logo_label.setStyleSheet("font-weight: 800; font-size: 16px; color: #0EA5E9;")

        brand_text_col = QVBoxLayout()
        brand_text_col.setSpacing(1)

        self.brand_title = QLabel("CipherAI")
        self.brand_title.setObjectName("brandTitle")
        self.brand_title.setStyleSheet("font-size: 16px; font-weight: 800; letter-spacing: 0.5px;")

        self.brand_sub = QLabel("Security Workstation")
        self.brand_sub.setObjectName("brandSub")
        self.brand_sub.setStyleSheet("font-size: 11px;")

        brand_text_col.addWidget(self.brand_title)
        brand_text_col.addWidget(self.brand_sub)

        brand_row.addWidget(logo_label)
        brand_row.addLayout(brand_text_col, stretch=1)
        layout.addLayout(brand_row)

        # Navigation items
        for key, label, is_section in self.NAV_ITEMS:
            if is_section:
                sec_lbl = QLabel(label)
                sec_lbl.setObjectName("sidebarSectionHeader")
                layout.addWidget(sec_lbl)
            else:
                btn = NavButton(label, self)
                btn.clicked.connect(lambda checked=False, k=key: self._on_nav_click(k))
                self._buttons[key] = btn
                layout.addWidget(btn)

        layout.addStretch()

        # Bottom System Status Widget
        self.status_box = QFrame()
        self.status_box.setObjectName("sidebarStatusBox")
        status_layout = QVBoxLayout(self.status_box)
        status_layout.setContentsMargins(10, 10, 10, 10)
        status_layout.setSpacing(3)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)

        dot = QFrame()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet("background-color: #10B981; border-radius: 3px;")

        status_text = QLabel("System Ready")
        status_text.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 700;")

        status_row.addWidget(dot)
        status_row.addWidget(status_text)
        status_row.addStretch()

        engine_text = QLabel("Crypto Engine Active")
        engine_text.setObjectName("engineStatusText")
        engine_text.setStyleSheet("font-size: 10px;")

        status_layout.addLayout(status_row)
        status_layout.addWidget(engine_text)

        layout.addWidget(self.status_box)

    def _on_nav_click(self, key: str) -> None:
        self.set_active(key)
        self.page_selected.emit(key)

    def set_active(self, key: str) -> None:
        self._active_key = key
        for k, btn in self._buttons.items():
            is_active = k == key
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        colors = get_palette(theme)
        is_dark = theme == DARK_THEME

        self.brand_title.setStyleSheet(
            f"font-size: 16px; font-weight: 800; color: {colors['text_primary']}; letter-spacing: 0.5px;"
        )
        self.brand_sub.setStyleSheet(
            f"font-size: 11px; color: {colors['text_muted']};"
        )

        self.setStyleSheet(
            f"""
            QFrame#sidebar {{
                background-color: {colors["bg_sidebar"]};
                border-right: 1px solid {colors["border_subtle"]};
            }}
            QLabel#sidebarSectionHeader {{
                font-size: 10px;
                font-weight: 700;
                color: {colors["text_muted"]};
                margin-top: 10px;
                margin-bottom: 2px;
                margin-left: 10px;
                letter-spacing: 0.5px;
            }}
            QPushButton#sidebarNavButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: {colors["text_secondary"]};
                font-size: 13px;
                font-weight: 600;
                text-align: left;
                padding-left: 12px;
            }}
            QPushButton#sidebarNavButton:hover {{
                background-color: {colors["secondary_hover"]};
                color: {colors["text_primary"]};
            }}
            QPushButton#sidebarNavButton[active="true"] {{
                background-color: {colors["primary_subtle"]};
                color: {colors["primary"] if not is_dark else colors["primary_hover"]};
                border-left: 3px solid {colors["primary"]};
                font-weight: 700;
            }}
            QFrame#sidebarStatusBox {{
                background-color: {colors["bg_surface"]};
                border: 1px solid {colors["border_subtle"]};
                border-radius: 6px;
            }}
            QLabel#engineStatusText {{
                color: {colors["text_muted"]};
            }}
            """
        )
