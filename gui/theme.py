"""Centralized design system and theming for CipherAI."""

from typing import Literal

ThemeName = Literal["Dark", "Light"]

DARK_THEME: ThemeName = "Dark"
LIGHT_THEME: ThemeName = "Light"
THEME_OPTIONS: tuple[ThemeName, ThemeName] = (DARK_THEME, LIGHT_THEME)


def normalize_theme(theme: str | None) -> ThemeName:
    """Return a supported theme name, defaulting to Dark."""
    if theme == LIGHT_THEME:
        return LIGHT_THEME
    return DARK_THEME


# Design tokens for balanced, clean desktop interface
PALETTES: dict[ThemeName, dict[str, str]] = {
    DARK_THEME: {
        "bg_app": "#0B0F17",
        "bg_sidebar": "#101622",
        "bg_surface": "#161E2E",
        "bg_surface_elevated": "#1E293B",
        "bg_input": "#0F172A",
        "border_subtle": "#1E293B",
        "border_normal": "#2E3B52",
        "border_focus": "#0284C7",
        "primary": "#0284C7",
        "primary_hover": "#0369A1",
        "primary_pressed": "#075985",
        "primary_subtle": "rgba(2, 132, 199, 0.15)",
        "secondary_bg": "#1E293B",
        "secondary_hover": "#2A384F",
        "secondary_text": "#CBD5E1",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "success": "#10B981",
        "success_bg": "rgba(16, 185, 129, 0.12)",
        "warning": "#F59E0B",
        "warning_bg": "rgba(245, 158, 11, 0.12)",
        "danger": "#EF4444",
        "danger_bg": "rgba(239, 68, 68, 0.12)",
        "info": "#38BDF8",
        "info_bg": "rgba(56, 189, 248, 0.12)",
        "scrollbar_bg": "#101622",
        "scrollbar_handle": "#28354A",
        "scrollbar_handle_hover": "#3B4D6B",
        "table_header_bg": "#1A2334",
        "table_row_alt": "#121927",
        "table_row_hover": "#1E293B",
        "tag_bg": "#1E293B",
        "tag_text": "#38BDF8",
    },
    LIGHT_THEME: {
        "bg_app": "#F8FAFC",
        "bg_sidebar": "#FFFFFF",
        "bg_surface": "#FFFFFF",
        "bg_surface_elevated": "#F1F5F9",
        "bg_input": "#FFFFFF",
        "border_subtle": "#E2E8F0",
        "border_normal": "#CBD5E1",
        "border_focus": "#0284C7",
        "primary": "#0284C7",
        "primary_hover": "#0369A1",
        "primary_pressed": "#075985",
        "primary_subtle": "#E0F2FE",
        "secondary_bg": "#F1F5F9",
        "secondary_hover": "#E2E8F0",
        "secondary_text": "#334155",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#94A3B8",
        "success": "#059669",
        "success_bg": "rgba(5, 150, 105, 0.10)",
        "warning": "#D97706",
        "warning_bg": "rgba(217, 119, 6, 0.10)",
        "danger": "#DC2626",
        "danger_bg": "rgba(220, 38, 38, 0.10)",
        "info": "#0284C7",
        "info_bg": "rgba(2, 132, 199, 0.10)",
        "scrollbar_bg": "#F8FAFC",
        "scrollbar_handle": "#CBD5E1",
        "scrollbar_handle_hover": "#94A3B8",
        "table_header_bg": "#F1F5F9",
        "table_row_alt": "#F8FAFC",
        "table_row_hover": "#F1F5F9",
        "tag_bg": "#E0F2FE",
        "tag_text": "#0369A1",
    },
}


def get_palette(theme: ThemeName) -> dict[str, str]:
    """Return color dictionary for specified theme."""
    return PALETTES.get(normalize_theme(theme), PALETTES[DARK_THEME])


def get_app_stylesheet(theme: ThemeName) -> str:
    """Generate global application stylesheet matching a modern desktop application."""
    colors = get_palette(theme)
    is_dark = theme == DARK_THEME

    return f"""
        QMainWindow, QWidget#centralRoot, QWidget#dashboardPage, QWidget#filesPage, QWidget#aboutPage, QWidget#settingsPage {{
            background-color: {colors["bg_app"]};
            color: {colors["text_primary"]};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            background: {colors["scrollbar_bg"]};
            width: 8px;
            margin: 0px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {colors["scrollbar_handle"]};
            min-height: 28px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {colors["scrollbar_handle_hover"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {colors["scrollbar_bg"]};
            height: 8px;
            margin: 0px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {colors["scrollbar_handle"]};
            min-width: 28px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {colors["scrollbar_handle_hover"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* General Labels */
        QLabel {{
            color: {colors["text_primary"]};
            background-color: transparent;
        }}

        /* Buttons */
        QPushButton {{
            font-weight: 600;
            font-size: 13px;
            border-radius: 6px;
            padding: 8px 16px;
            border: 1px solid transparent;
        }}

        QPushButton#primaryButton {{
            background-color: {colors["primary"]};
            color: #FFFFFF;
            border: 1px solid {colors["primary"]};
        }}
        QPushButton#primaryButton:hover {{
            background-color: {colors["primary_hover"]};
            border-color: {colors["primary_hover"]};
        }}
        QPushButton#primaryButton:pressed {{
            background-color: {colors["primary_pressed"]};
            border-color: {colors["primary_pressed"]};
        }}
        QPushButton#primaryButton:disabled {{
            background-color: {"#1E293B" if is_dark else "#E2E8F0"};
            color: {"#64748B" if is_dark else "#94A3B8"};
            border-color: transparent;
        }}

        QPushButton#secondaryButton {{
            background-color: {colors["secondary_bg"]};
            color: {colors["secondary_text"]};
            border: 1px solid {colors["border_normal"]};
        }}
        QPushButton#secondaryButton:hover {{
            background-color: {colors["secondary_hover"]};
            color: {colors["text_primary"]};
            border-color: {colors["border_focus"]};
        }}
        QPushButton#secondaryButton:pressed {{
            background-color: {colors["border_subtle"]};
        }}

        /* Line Inputs */
        QLineEdit {{
            background-color: {colors["bg_input"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: {colors["primary"]};
            selection-color: #FFFFFF;
        }}
        QLineEdit:focus {{
            border: 1px solid {colors["border_focus"]};
            background-color: {"#131B2E" if is_dark else "#FFFFFF"};
        }}
        QLineEdit:disabled {{
            background-color: {colors["bg_surface"]};
            color: {colors["text_muted"]};
            border-color: {colors["border_subtle"]};
        }}

        /* Text Area */
        QTextEdit, QPlainTextEdit {{
            background-color: {colors["bg_input"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: {colors["primary"]};
            selection-color: #FFFFFF;
        }}
        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {colors["border_focus"]};
        }}

        /* Combo Box */
        QComboBox {{
            background-color: {colors["bg_input"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 6px;
            padding: 7px 12px;
            font-size: 13px;
            min-height: 20px;
        }}
        QComboBox:hover {{
            border-color: {colors["border_focus"]};
        }}
        QComboBox:focus {{
            border-color: {colors["border_focus"]};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left-width: 0px;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {colors["bg_surface"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 6px;
            selection-background-color: {colors["primary"]};
            selection-color: #FFFFFF;
            padding: 4px;
        }}

        /* Radio Buttons */
        QRadioButton {{
            color: {colors["text_primary"]};
            font-size: 13px;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 1px solid {colors["border_normal"]};
            background-color: {colors["bg_input"]};
        }}
        QRadioButton::indicator:checked {{
            background-color: {colors["primary"]};
            border-color: {colors["primary"]};
        }}
        QRadioButton::indicator:hover {{
            border-color: {colors["border_focus"]};
        }}

        /* Table Widget */
        QTableWidget {{
            background-color: {colors["bg_surface"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
            gridline-color: {colors["border_subtle"]};
            selection-background-color: {colors["primary_subtle"]};
            selection-color: {colors["text_primary"]};
        }}
        QHeaderView::section {{
            background-color: {colors["table_header_bg"]};
            color: {colors["text_secondary"]};
            font-weight: 600;
            font-size: 12px;
            padding: 8px 12px;
            border: none;
            border-bottom: 1px solid {colors["border_subtle"]};
        }}

        /* Header Labels */
        QLabel#headerTitle {{
            font-size: 20px;
            font-weight: 700;
            color: {colors["text_primary"]};
        }}
        QLabel#headerSubtitle {{
            font-size: 13px;
            color: {colors["text_secondary"]};
        }}

        /* Cards & Frames */
        QFrame#cyberCard, QFrame#toolResultCard, QFrame#settingsCard {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
        }}
        QFrame#cyberCard:hover {{
            border-color: {colors["border_normal"]};
        }}
        QLabel#cardTitle {{
            font-size: 14px;
            font-weight: 700;
            color: {colors["primary"] if not is_dark else colors["primary_hover"]};
        }}
        QLabel#cardSubtitle {{
            font-size: 12px;
            color: {colors["text_muted"]};
        }}

        /* Dashboard Stat Cards */
        QFrame#statCard {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
        }}
        QLabel#statTitle {{
            font-size: 11px;
            font-weight: 700;
            color: {colors["text_muted"]};
            letter-spacing: 0.5px;
        }}
        QLabel#statValue {{
            font-size: 15px;
            font-weight: 700;
            color: {colors["text_primary"]};
        }}
        QLabel#statSub {{
            font-size: 11px;
            color: {colors["text_secondary"]};
        }}

        /* Quick Action Buttons */
        QPushButton#quickActionBtn {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
            text-align: left;
        }}
        QPushButton#quickActionBtn:hover {{
            background-color: {colors["bg_surface_elevated"]};
            border-color: {colors["border_focus"]};
        }}
        QLabel#qaTag {{
            font-size: 10px;
            font-weight: 700;
            color: {colors["primary"]};
            background-color: {colors["primary_subtle"]};
            border-radius: 4px;
            padding: 2px 6px;
        }}
        QLabel#qaTitle {{
            font-size: 13px;
            font-weight: 700;
            color: {colors["text_primary"]};
        }}
        QLabel#qaDesc {{
            font-size: 11px;
            color: {colors["text_secondary"]};
        }}

        /* Algorithm Overview Cards */
        QFrame#algoCard {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
        }}
        QFrame#algoCard:hover {{
            border-color: {colors["border_normal"]};
        }}
        QLabel#algoName {{
            font-size: 15px;
            font-weight: 700;
            color: {colors["primary"] if not is_dark else colors["primary_hover"]};
        }}
        QLabel#algoSpecs {{
            font-size: 12px;
            font-weight: 600;
            color: {colors["text_secondary"]};
        }}
        QLabel#algoDesc {{
            font-size: 12px;
            color: {colors["text_muted"]};
            line-height: 1.4;
        }}

        /* Welcome Banner & Heroes */
        QFrame#welcomeBanner, QFrame#aboutHero {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-left: 4px solid {colors["primary"]};
            border-radius: 8px;
        }}
        QLabel#heroTitle {{
            font-size: 18px;
            font-weight: 700;
            color: {colors["text_primary"]};
        }}
        QLabel#heroSub {{
            font-size: 13px;
            color: {colors["text_secondary"]};
        }}

        /* Empty State */
        QFrame#emptyStateFrame {{
            background-color: {colors["bg_surface_elevated"]};
            border: 1px dashed {colors["border_normal"]};
            border-radius: 8px;
        }}
        QLabel#emptyTitle {{
            font-size: 14px;
            font-weight: 700;
            color: {colors["text_primary"]};
        }}
        QLabel#emptyDesc {{
            font-size: 12px;
            color: {colors["text_secondary"]};
        }}

        /* Advisory Banner */
        QFrame#advisoryFrame {{
            background-color: {colors["warning_bg"]};
            border: 1px solid {colors["warning"]};
            border-radius: 6px;
        }}
        QLabel#advisoryText {{
            font-size: 12px;
            color: {colors["text_primary"]};
        }}

        /* Path Results Display */
        QFrame#pathResultFrame {{
            background-color: {colors["bg_input"]};
            border: 1px solid {colors["success"]};
            border-radius: 6px;
        }}
        QLabel#pathResultLabel {{
            font-size: 11px;
            font-weight: 700;
            color: {colors["success"]};
        }}
        QLabel#pathResultText {{
            font-family: "Consolas", "Courier New", monospace;
            font-size: 12px;
            color: {colors["text_primary"]};
        }}

        /* Code & Technical Blocks */
        QFrame#archCodeFrame, QLabel#archCodeText {{
            background-color: {colors["bg_input"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 6px;
            color: {colors["text_primary"]};
            font-family: "Consolas", "Courier New", monospace;
            font-size: 12px;
            padding: 12px;
        }}

        /* Form Labels & Helpers */
        QLabel#fieldLabel {{
            color: {colors["text_secondary"]};
            font-weight: 600;
            font-size: 13px;
        }}
        QLabel#helperText {{
            color: {colors["text_muted"]};
            font-size: 11px;
        }}
        QLabel#codeTag {{
            color: {colors["primary"]};
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
            font-weight: 600;
        }}
        QLabel#codeText {{
            color: {colors["text_primary"]};
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
        }}
        QLabel#logoFallback {{
            font-size: 20px;
            font-weight: 800;
            color: {colors["primary"]};
            background-color: {colors["primary_subtle"]};
            border-radius: 8px;
            padding: 8px;
        }}

        /* Tooltip */
        QToolTip {{
            background-color: {colors["bg_surface_elevated"]};
            color: {colors["text_primary"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 12px;
        }}

        /* Menu */
        QMenu {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 6px;
            padding: 4px;
            color: {colors["text_primary"]};
        }}
        QMenu::item {{
            padding: 6px 24px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {colors["primary"]};
            color: #FFFFFF;
        }}
    """


def get_message_box_stylesheet(theme: ThemeName) -> str:
    """Return crisp, high-contrast stylesheet for QMessageBox to eliminate light-gray/white illegibility."""
    colors = get_palette(theme)

    return f"""
        QMessageBox {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 8px;
            color: {colors["text_primary"]};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        QMessageBox QLabel {{
            background-color: transparent;
            color: {colors["text_primary"]};
            font-size: 13px;
            font-weight: 400;
            min-width: 280px;
            padding: 6px;
        }}
        QMessageBox QPushButton {{
            background-color: {colors["primary"]};
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 600;
            border-radius: 6px;
            border: 1px solid {colors["primary"]};
            min-width: 84px;
            min-height: 32px;
            padding: 6px 16px;
        }}
        QMessageBox QPushButton:hover {{
            background-color: {colors["primary_hover"]};
            border-color: {colors["primary_hover"]};
        }}
        QMessageBox QPushButton:pressed {{
            background-color: {colors["primary_pressed"]};
        }}
    """


def get_dialog_stylesheet(theme: ThemeName) -> str:
    """Return stylesheet for custom dialogs."""
    return get_message_box_stylesheet(theme)


def get_home_stylesheet(theme: ThemeName) -> str:
    """Return stylesheet for AI Assistant / Home page."""
    colors = get_palette(theme)
    is_dark = theme == DARK_THEME

    return f"""
        QWidget#homePage, QWidget#aiChatPage {{
            background-color: {colors["bg_app"]};
        }}
        QLabel#homeTitle, QLabel#aiChatTitle {{
            color: {colors["text_primary"]};
            font-size: 20px;
            font-weight: 700;
        }}
        QLabel#homeSubtitle, QLabel#aiChatSubtitle {{
            color: {colors["text_secondary"]};
            font-size: 13px;
        }}
        QFrame#chatInputPanel {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
        }}
        QTextEdit#chatInput {{
            background-color: transparent;
            color: {colors["text_primary"]};
            border: none;
            font-size: 13px;
        }}
        QPushButton#suggestionButton {{
            background-color: {colors["secondary_bg"]};
            color: {colors["secondary_text"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 14px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        QPushButton#suggestionButton:hover {{
            background-color: {colors["primary_subtle"]};
            color: {colors["primary"]};
            border-color: {colors["primary"]};
        }}
        QFrame#userMessage {{
            background-color: {colors["primary"]};
            border-radius: 8px;
            padding: 10px 14px;
        }}
        QLabel#userMessageText {{
            color: #FFFFFF;
            font-size: 13px;
            line-height: 1.4;
        }}
        QFrame#assistantMessage {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
            padding: 12px 16px;
        }}
        QLabel#assistantMessageText {{
            color: {colors["text_primary"]};
            font-size: 13px;
            line-height: 1.4;
        }}
        QFrame#welcomeMessage {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_normal"]};
            border-left: 4px solid {colors["primary"]};
            border-radius: 8px;
            padding: 14px 18px;
        }}
        QLabel#welcomeMessageTitle {{
            color: {colors["primary"] if not is_dark else colors["primary_hover"]};
            font-size: 14px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        QLabel#welcomeMessageText {{
            color: {colors["text_primary"]};
            font-size: 13px;
            line-height: 1.4;
        }}
        QFrame#thinkingMessage {{
            background-color: {colors["bg_surface"]};
            border: 1px dashed {colors["primary"]};
            border-radius: 8px;
            padding: 10px 16px;
        }}
        QLabel#thinkingMessageText {{
            color: {colors["primary"]};
            font-size: 13px;
            font-style: italic;
        }}
        QFrame#toolResultCard {{
            background-color: {colors["bg_surface_elevated"]};
            border: 1px solid {colors["border_normal"]};
            border-left: 4px solid {colors["success"]};
            border-radius: 8px;
            padding: 12px 16px;
        }}
        QLabel#toolResultTitle {{
            color: {colors["success"]};
            font-size: 13px;
            font-weight: 700;
        }}
        QLabel#toolResultLabel {{
            color: {colors["text_muted"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        QLabel#toolResultValue {{
            color: {colors["text_primary"]};
            font-size: 13px;
            font-family: "Consolas", "Courier New", monospace;
        }}
        QLabel#messageMeta {{
            color: {colors["text_muted"]};
            font-size: 11px;
        }}
    """


def get_settings_stylesheet(theme: ThemeName) -> str:
    """Return stylesheet for Settings page."""
    colors = get_palette(theme)
    return f"""
        QWidget#settingsPage {{
            background-color: {colors["bg_app"]};
        }}
        QLabel#settingsTitle {{
            color: {colors["text_primary"]};
            font-size: 20px;
            font-weight: 700;
        }}
        QLabel#settingsSubtitle {{
            color: {colors["text_secondary"]};
            font-size: 13px;
        }}
        QFrame#settingsCard {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
        }}
        QLabel#cardSectionTitle {{
            color: {colors["primary"]};
            font-size: 14px;
            font-weight: 700;
        }}
        QLabel#fieldLabel {{
            color: {colors["text_secondary"]};
            font-weight: 600;
            font-size: 13px;
        }}
        QLabel#helperText {{
            color: {colors["text_muted"]};
            font-size: 11px;
        }}
        QLabel#codeTag {{
            color: {colors["primary"]};
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
            font-weight: 600;
        }}
        QLabel#codeText {{
            color: {colors["text_primary"]};
            font-family: "Consolas", "Courier New", monospace;
            font-size: 13px;
        }}
    """


def get_about_stylesheet(theme: ThemeName) -> str:
    """Return stylesheet for About page."""
    colors = get_palette(theme)
    is_dark = theme == DARK_THEME

    return f"""
        QWidget#aboutPage {{
            background-color: {colors["bg_app"]};
        }}
        QFrame#aboutHero {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-left: 4px solid {colors["primary"]};
            border-radius: 8px;
        }}
        QLabel#heroTitle {{
            font-size: 18px;
            font-weight: 700;
            color: {colors["text_primary"]};
        }}
        QLabel#heroSub {{
            font-size: 13px;
            color: {colors["text_secondary"]};
        }}
        QLabel#archCodeText {{
            font-family: "Consolas", "Courier New", monospace;
            font-size: 12px;
            color: {colors["text_primary"]};
            background-color: {colors["bg_input"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 6px;
            padding: 14px;
        }}
        QFrame#algoCard {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
        }}
        QFrame#algoCard:hover {{
            border-color: {colors["border_normal"]};
        }}
        QLabel#algoName {{
            font-size: 13px;
            font-weight: 700;
            color: {colors["primary"] if not is_dark else colors["primary_hover"]};
        }}
        QLabel#algoSpecs {{
            font-size: 12px;
            color: {colors["text_secondary"]};
            line-height: 1.4;
        }}
    """


def get_files_stylesheet(theme: ThemeName) -> str:
    """Return stylesheet for Files page."""
    colors = get_palette(theme)
    return f"""
        QWidget#filesPage {{
            background-color: {colors["bg_app"]};
        }}
    """


def get_workspace_stylesheet(theme: ThemeName, prefix: str) -> str:
    """Return stylesheet for crypto workspace pages (AES, RSA, DES)."""
    colors = get_palette(theme)
    is_dark = theme == DARK_THEME

    return f"""
        QWidget#{prefix}Page {{
            background-color: {colors["bg_app"]};
        }}
        QLabel#{prefix}Title {{
            color: {colors["text_primary"]};
            font-size: 20px;
            font-weight: 700;
        }}
        QLabel#{prefix}Subtitle {{
            color: {colors["text_secondary"]};
            font-size: 13px;
        }}
        QLabel#fieldLabel {{
            color: {colors["text_secondary"]};
            font-weight: 600;
            font-size: 13px;
        }}
        QLabel#helperText {{
            color: {colors["text_muted"]};
            font-size: 12px;
        }}
    """
