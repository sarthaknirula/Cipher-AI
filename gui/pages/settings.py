"""Application settings and diagnostics page."""

import os
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core import settings as core_settings
from gui.components import CyberCard, PageHeader, StatusBadge
from gui.theme import (
    DARK_THEME,
    LIGHT_THEME,
    THEME_OPTIONS,
    ThemeName,
    get_settings_stylesheet,
)


class SettingsPage(QWidget):
    """Settings and system diagnostics page."""

    theme_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self._theme = DARK_THEME

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(24)

        # Header
        header = PageHeader(
            "Settings & Diagnostics",
            "Configure appearance, view AI pipeline status, and check cryptographic engines.",
            badge_text="Ready",
            badge_status="success",
        )
        layout.addWidget(header)

        # 1. Appearance Card
        app_card = CyberCard(
            "Appearance & Interface",
            "Choose your preferred visual theme for high-contrast operation.",
        )
        app_layout = QFormLayout()
        app_layout.setSpacing(14)

        theme_lbl = QLabel("Application Theme")
        theme_lbl.setObjectName("fieldLabel")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([DARK_THEME, LIGHT_THEME])
        self.theme_combo.setCursor(Qt.PointingHandCursor)
        self.theme_combo.setFixedWidth(200)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

        app_layout.addRow(theme_lbl, self.theme_combo)
        app_card.add_layout(app_layout)
        layout.addWidget(app_card)

        # 2. AI Engine Status Card
        has_key = bool(os.getenv("GEMINI_API_KEY"))
        ai_card = CyberCard(
            "AI Assistant Configuration",
            "Status and configuration parameters for Google Gemini integration.",
        )
        ai_layout = QFormLayout()
        ai_layout.setSpacing(14)

        status_badge = StatusBadge(
            "CONFIGURED & READY" if has_key else "KEY NOT CONFIGURED IN .ENV",
            "success" if has_key else "warning",
        )
        ai_layout.addRow("Gemini API Status", status_badge)

        model_lbl = QLabel(getattr(core_settings, "GEMINI_MODEL", "gemini-3.5-flash-lite"))
        model_lbl.setObjectName("codeTag")
        ai_layout.addRow("Active Model", model_lbl)

        temp_lbl = QLabel(str(getattr(core_settings, "GEMINI_TEMPERATURE", 0.2)))
        temp_lbl.setObjectName("codeText")
        ai_layout.addRow("Sampling Temperature", temp_lbl)

        sec_note = QLabel(
            "Security policy: The application loads credentials from the local environment (.env). "
            "Secret API keys are never displayed on screen or logged."
        )
        sec_note.setObjectName("helperText")
        sec_note.setWordWrap(True)
        ai_layout.addRow("", sec_note)

        ai_card.add_layout(ai_layout)
        layout.addWidget(ai_card)

        # 3. Cryptographic Engines & Environment Card
        sys_card = CyberCard(
            "Cryptographic Stack & Environment",
            "Core security libraries, runtime environment, and supported cipher specs.",
        )
        sys_layout = QFormLayout()
        sys_layout.setSpacing(12)

        sys_layout.addRow("Application", QLabel("CipherAI Desktop Suite v2.0 Enterprise"))
        sys_layout.addRow("Python Runtime", QLabel(f"Python {sys.version.split()[0]}"))
        sys_layout.addRow("GUI Framework", QLabel("PySide6 / Qt 6.11"))
        sys_layout.addRow("Cryptography Provider", QLabel("cryptography (OpenSSL Hazmat)"))
        sys_layout.addRow("AES Specification", QLabel("AES-CBC (128/192/256-bit) with PKCS#7"))
        sys_layout.addRow("RSA Specification", QLabel("RSA-OAEP (2048/3072/4096-bit) with SHA-256"))
        sys_layout.addRow("DES Specifications", QLabel("Double DES & Triple DES (3DES-EDE)"))

        sys_card.add_layout(sys_layout)
        layout.addWidget(sys_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _on_theme_changed(self, theme: str) -> None:
        self.theme_changed.emit(theme)

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(theme)
        self.theme_combo.blockSignals(False)
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_settings_stylesheet(self._theme))
