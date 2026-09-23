from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.pages.aes import AESPage
from gui.pages.des import DESPage
from gui.pages.home import HomePage
from gui.pages.rsa import RSAPage
from gui.pages.settings import SettingsPage
from gui.theme import DARK_THEME, ThemeName, get_app_stylesheet, normalize_theme


class MainWindow(QMainWindow):
    """Main application shell for Cipher AI."""

    WINDOW_TITLE = "Cipher AI"
    INITIAL_WIDTH = 1400
    INITIAL_HEIGHT = 850
    SIDEBAR_WIDTH = 220
    SETTINGS_ORGANIZATION = "Cipher AI"
    SETTINGS_APPLICATION = "CipherAI"
    THEME_SETTING_KEY = "appearance/theme"

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.INITIAL_WIDTH, self.INITIAL_HEIGHT)

        self._settings = QSettings(
            self.SETTINGS_ORGANIZATION,
            self.SETTINGS_APPLICATION,
        )
        self._theme = self._load_theme()
        self._pages = QStackedWidget()
        self._page_widgets: list[QWidget] = []
        self._navigation_buttons: dict[str, QPushButton] = {}

        self._configure_window()
        self._build_layout()
        self._register_pages()
        self._apply_theme(self._theme, save=False)

    def _load_theme(self) -> ThemeName:
        theme = self._settings.value(self.THEME_SETTING_KEY, DARK_THEME)
        return normalize_theme(theme if isinstance(theme, str) else None)

    def _configure_window(self) -> None:
        self.setMinimumSize(1000, 650)

    def _build_layout(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._create_sidebar())
        root_layout.addWidget(self._create_content_area(), stretch=1)

        self.setCentralWidget(root)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(self.SIDEBAR_WIDTH)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 24, 18, 24)
        layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(10)

        brand = QLabel("Cipher AI")
        brand.setObjectName("sidebarBrand")
        brand.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        brand_row.addWidget(brand, stretch=1)

        layout.addLayout(brand_row)
        layout.addSpacing(22)

        for label in (
            "Home",
            "RSA",
            "Double DES",
            "Triple DES",
            "AES",
            "Settings",
        ):
            button = self._create_navigation_button(label)
            layout.addWidget(button)
            self._navigation_buttons[label] = button

        layout.addStretch()
        return sidebar

    def _create_navigation_button(self, label: str) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName("navigationButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(46)
        button.setIconSize(QSize(18, 18))
        return button

    def _create_content_area(self) -> QFrame:
        content = QFrame()
        content.setObjectName("contentArea")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._pages)

        return content

    def _register_pages(self) -> None:
        page_factories = (
            ("Home", HomePage),
            ("RSA", RSAPage),
            ("Double DES", lambda: DESPage("Double DES")),
            ("Triple DES", lambda: DESPage("Triple DES")),
            ("AES", AESPage),
            ("Settings", SettingsPage),
        )

        for index, (label, page_factory) in enumerate(page_factories):
            page = page_factory()
            self._pages.addWidget(page)
            self._page_widgets.append(page)
            if isinstance(page, SettingsPage):
                page.theme_changed.connect(self._handle_theme_changed)

            button = self._navigation_buttons.get(label)
            if button is not None:
                button.clicked.connect(lambda checked=False, i=index: self._show_page(i))

        self._pages.setCurrentIndex(0)
        self._set_active_button(0)

    def _show_page(self, index: int) -> None:
        self._pages.setCurrentIndex(index)
        self._set_active_button(index)

    def _set_active_button(self, active_index: int) -> None:
        for index, button in enumerate(self._navigation_buttons.values()):
            button.setProperty("active", index == active_index)
            button.style().unpolish(button)
            button.style().polish(button)

    def _handle_theme_changed(self, theme: str) -> None:
        self._apply_theme(normalize_theme(theme))

    def _apply_theme(self, theme: ThemeName, save: bool = True) -> None:
        self._theme = theme
        if save:
            self._settings.setValue(self.THEME_SETTING_KEY, theme)
            self._settings.sync()

        self.setStyleSheet(get_app_stylesheet(theme))
        for page in self._page_widgets:
            apply_theme = getattr(page, "apply_theme", None)
            if callable(apply_theme):
                apply_theme(theme)

        for button in self._navigation_buttons.values():
            button.style().unpolish(button)
            button.style().polish(button)
