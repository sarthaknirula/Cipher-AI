"""Main application window for CipherAI."""

from pathlib import Path
from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
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
from gui.theme import (
    DARK_THEME,
    ThemeName,
    apply_application_palette,
    get_app_stylesheet,
    get_palette,
    normalize_theme,
)

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

        # Set in-memory window icon (no external asset files required)
        from gui.components import create_app_icon
        self.setWindowIcon(create_app_icon())

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

        # Top Control Bar across all pages
        self.top_bar = QFrame()
        self.top_bar.setObjectName("topControlBar")
        self.top_bar.setFixedHeight(46)
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(28, 0, 28, 0)
        top_bar_layout.setSpacing(12)

        self.top_bar_title = QLabel("CipherAI  <span style='color: #6B7280; font-weight: 500;'>Cryptographic Suite Control Panel</span>")
        self.top_bar_title.setObjectName("topControlTitle")
        self.top_bar_title.setTextFormat(Qt.RichText)

        self.top_ai_status = QLabel("●  AI ASSISTANT READY")
        self.top_ai_status.setObjectName("topAiStatus")

        top_bar_layout.addWidget(self.top_bar_title)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.top_ai_status)

        content_layout.addWidget(self.top_bar)
        content_layout.addWidget(self._pages, stretch=1)

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

            # Connect AI assistant busy state to top bar status
            if isinstance(page, HomePage):
                page.busy_state_changed.connect(self._handle_ai_busy_changed)

        self._navigate_to_page("dashboard")

    def _handle_ai_busy_changed(self, is_busy: bool) -> None:
        if is_busy:
            self.top_ai_status.setText("●  AI ASSISTANT BUSY")
            self.top_ai_status.setStyleSheet(
                "background-color: rgba(245, 158, 11, 0.1); color: #F59E0B; "
                "border: 1px solid #78350F; border-radius: 4px; padding: 4px 10px; "
                "font-size: 11px; font-weight: 800; letter-spacing: 0.5px;"
            )
        else:
            self.top_ai_status.setText("●  AI ASSISTANT READY")
            colors = get_palette(self._theme)
            is_dark = self._theme == DARK_THEME
            bg = "rgba(16, 185, 129, 0.08)" if is_dark else "#ECFDF5"
            border = "#064E3B" if is_dark else "#A7F3D0"
            color = "#10B981" if is_dark else "#059669"
            self.top_ai_status.setStyleSheet(
                f"background-color: {bg}; color: {color}; border: 1px solid {border}; "
                "border-radius: 4px; padding: 4px 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.5px;"
            )

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

        apply_application_palette(theme)
        self.setStyleSheet(get_app_stylesheet(theme))
        self.sidebar.apply_theme(theme)

        # Style top bar
        colors = get_palette(theme)
        is_dark = theme == DARK_THEME
        self.top_bar.setStyleSheet(
            f"QFrame#topControlBar {{ background-color: {colors['bg_app']}; border-bottom: 1px solid {colors['border_subtle']}; }}"
        )
        self.top_bar_title.setStyleSheet(
            f"font-size: 12px; font-weight: 700; color: {colors['text_primary']}; letter-spacing: 0.4px;"
        )
        self._handle_ai_busy_changed(False)

        for page in self._page_widgets:
            apply_func = getattr(page, "apply_theme", None)
            if callable(apply_func):
                apply_func(theme)
