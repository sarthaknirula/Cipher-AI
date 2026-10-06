"""Main application window for CipherAI."""

from pathlib import Path
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from gui.pages.about import AboutPage
from gui.pages.aes import AESPage
from gui.pages.dashboard import DashboardPage
from gui.pages.des import DESPage
from gui.pages.files import FilesPage
from gui.pages.home import HomePage
from gui.pages.rsa import RSAPage
from gui.pages.settings import SettingsPage
from gui.sidebar import Sidebar
from gui.theme import DARK_THEME, ThemeName, get_app_stylesheet, normalize_theme

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MainWindow(QMainWindow):
    """Main application shell for CipherAI."""

    WINDOW_TITLE = "CipherAI - Cyber Cryptographic Suite"
    INITIAL_WIDTH = 1400
    INITIAL_HEIGHT = 860
    MIN_WIDTH = 1080
    MIN_HEIGHT = 680
    SETTINGS_ORGANIZATION = "CipherAI"
    SETTINGS_APPLICATION = "CipherAI"
    THEME_SETTING_KEY = "appearance/theme"

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.INITIAL_WIDTH, self.INITIAL_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Set window icon
        logo_path = PROJECT_ROOT / "assets" / "logo" / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self._settings = QSettings(
            self.SETTINGS_ORGANIZATION,
            self.SETTINGS_APPLICATION,
        )
        self._theme = self._load_theme()
        self._pages = QStackedWidget()
        self._page_map: dict[str, int] = {}
        self._page_widgets: list[QWidget] = []

        self._build_layout()
        self._register_pages()
        self._apply_theme(self._theme, save=False)

    def _load_theme(self) -> ThemeName:
        theme = self._settings.value(self.THEME_SETTING_KEY, DARK_THEME)
        return normalize_theme(theme if isinstance(theme, str) else None)

    def _build_layout(self) -> None:
        root = QWidget()
        root.setObjectName("centralRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar(self)
        self.sidebar.page_selected.connect(self._navigate_to_page)

        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._pages)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(content_area, stretch=1)

        self.setCentralWidget(root)

    def _register_pages(self) -> None:
        pages_to_register = [
            ("dashboard", DashboardPage),
            ("ai_assistant", HomePage),
            ("aes", AESPage),
            ("rsa", RSAPage),
            ("double_des", lambda: DESPage("Double DES")),
            ("triple_des", lambda: DESPage("Triple DES")),
            ("files", FilesPage),
            ("settings", SettingsPage),
            ("about", AboutPage),
        ]

        for index, (key, factory) in enumerate(pages_to_register):
            page = factory()
            self._pages.addWidget(page)
            self._page_widgets.append(page)
            self._page_map[key] = index

            # Connect dashboard quick actions
            if isinstance(page, DashboardPage):
                page.navigate_requested.connect(self._navigate_to_page)

            # Connect settings theme changes
            if isinstance(page, SettingsPage):
                page.theme_changed.connect(self._handle_theme_changed)

        self._navigate_to_page("dashboard")

    def _navigate_to_page(self, key: str) -> None:
        index = self._page_map.get(key)
        if index is not None:
            self._pages.setCurrentIndex(index)
            self.sidebar.set_active(key)

    def _handle_theme_changed(self, theme: str) -> None:
        self._apply_theme(normalize_theme(theme))

    def _apply_theme(self, theme: ThemeName, save: bool = True) -> None:
        self._theme = theme
        if save:
            self._settings.setValue(self.THEME_SETTING_KEY, theme)
            self._settings.sync()

        self.setStyleSheet(get_app_stylesheet(theme))
        self.sidebar.apply_theme(theme)

        for page in self._page_widgets:
            apply_func = getattr(page, "apply_theme", None)
            if callable(apply_func):
                apply_func(theme)
