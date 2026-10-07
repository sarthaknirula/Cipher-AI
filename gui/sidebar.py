"""Persistent left sidebar navigation for CipherAI."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.components import create_cipher_shield_pixmap
from gui.theme import DARK_THEME, ThemeName, get_palette


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
        ("dashboard", "Dashboard", "⊞", False),
        ("ai_assistant", "AI Assistant", ">_", False),
        ("section_crypto", "CRYPTOGRAPHY", "", True),
        ("aes", "AES", "🔒", False),
        ("rsa", "RSA", "🗝", False),
        ("double_des", "Double DES", "⚏", False),
        ("triple_des", "Triple DES", "☵", False),
        ("section_workspace", "WORKSPACE", "", True),
        ("files", "Files", "📁", False),
        ("settings", "Settings", "⚙", False),
        ("about", "About", "ⓘ", False),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self._buttons: dict[str, NavButton] = {}
        self._active_key = "dashboard"
        self._theme = DARK_THEME

        self._build_ui()
        self.apply_theme(DARK_THEME)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 14)
        layout.setSpacing(4)

        # Brand header: CIPHER [ AI ]
        brand_container = QWidget()
        brand_container.setObjectName("sidebarBrandContainer")
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(6, 4, 6, 16)
        brand_layout.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title_row.setContentsMargins(0, 0, 0, 0)

        self.brand_cipher = QLabel("CIPHER")
        self.brand_cipher.setObjectName("brandCipher")
        self.brand_cipher.setStyleSheet("font-size: 16px; font-weight: 900; letter-spacing: 1px;")

        self.brand_ai_badge = QLabel("AI")
        self.brand_ai_badge.setObjectName("brandAiBadge")
        self.brand_ai_badge.setAlignment(Qt.AlignCenter)
        self.brand_ai_badge.setFixedSize(26, 18)
        self.brand_ai_badge.setStyleSheet(
            "background-color: #F59E0B; color: #000000; font-size: 11px; font-weight: 900; border-radius: 3px;"
        )

        title_row.addWidget(self.brand_cipher)
        title_row.addWidget(self.brand_ai_badge)
        title_row.addStretch()

        self.brand_sub = QLabel("SECURITY SUITE")
        self.brand_sub.setObjectName("brandSub")
        self.brand_sub.setStyleSheet(
            "font-size: 9px; font-weight: 700; color: #6B7280; letter-spacing: 1.5px;"
        )

        brand_layout.addLayout(title_row)
        brand_layout.addWidget(self.brand_sub)
        layout.addWidget(brand_container)

        # Navigation items
        for key, label, icon, is_section in self.NAV_ITEMS:
            if is_section:
                sec_lbl = QLabel(label)
                sec_lbl.setObjectName("sidebarSectionHeader")
                layout.addWidget(sec_lbl)
            else:
                display_text = f"  {icon}   {label}" if icon else label
                btn = NavButton(display_text, self)
                btn.clicked.connect(lambda checked=False, k=key: self._on_nav_click(k))
                self._buttons[key] = btn
                layout.addWidget(btn)

        layout.addStretch()

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

        self.brand_cipher.setStyleSheet(
            f"font-size: 16px; font-weight: 900; color: {colors['text_primary']}; letter-spacing: 1px;"
        )
        self.brand_sub.setStyleSheet(
            f"font-size: 9px; font-weight: 700; color: {colors['text_muted']}; letter-spacing: 1.5px;"
        )
        self.brand_ai_badge.setStyleSheet(
            f"background-color: {colors['primary']}; color: #000000; font-size: 11px; font-weight: 900; border-radius: 3px;"
        )

        active_bg = "#181A1D" if is_dark else "#FEF3C7"
        active_color = colors["primary"]
        active_border = f"3px solid {colors['primary']}"

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
                margin-top: 12px;
                margin-bottom: 2px;
                margin-left: 10px;
                letter-spacing: 0.8px;
            }}
            QPushButton#sidebarNavButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: {colors["text_secondary"]};
                font-size: 13px;
                font-weight: 600;
                text-align: left;
                padding-left: 10px;
            }}
            QPushButton#sidebarNavButton:hover {{
                background-color: {colors["secondary_hover"]};
                color: {colors["text_primary"]};
            }}
            QPushButton#sidebarNavButton[active="true"] {{
                background-color: {active_bg};
                color: {active_color};
                border-left: {active_border};
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
