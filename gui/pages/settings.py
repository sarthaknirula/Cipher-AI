from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from gui.theme import DARK_THEME, THEME_OPTIONS, ThemeName, get_settings_stylesheet


class SettingsPage(QWidget):
    """Application settings page."""

    theme_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("settingsPage")
        self._theme = DARK_THEME
        self._build_layout()
        self._apply_styles()

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(18)

        title = QLabel("Settings")
        title.setObjectName("settingsTitle")

        subtitle = QLabel("Configure application preferences.")
        subtitle.setObjectName("settingsSubtitle")

        card = QFrame()
        card.setObjectName("settingsCard")
        card.setMaximumWidth(620)

        card_layout = QFormLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setHorizontalSpacing(18)
        card_layout.setVerticalSpacing(16)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEME_OPTIONS)
        self.theme_combo.setCursor(Qt.PointingHandCursor)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(12)
        card_layout.addRow("Theme", self.theme_combo)
        layout.addWidget(card)
        layout.addStretch()

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(theme)
        self.theme_combo.blockSignals(False)
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_settings_stylesheet(self._theme))

    def _on_theme_changed(self, theme: str) -> None:
        self.theme_changed.emit(theme)
