"""Centralized design system and theming for CipherAI."""

from typing import Literal

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

ThemeName = Literal["Dark", "Light"]

DARK_THEME: ThemeName = "Dark"
LIGHT_THEME: ThemeName = "Light"
THEME_OPTIONS: tuple[ThemeName, ThemeName] = (DARK_THEME, LIGHT_THEME)


def normalize_theme(theme: str | None) -> ThemeName:
    """Return a supported theme name, defaulting to Dark."""
    if theme == LIGHT_THEME:
        return LIGHT_THEME
    return DARK_THEME


# Technical cybersecurity design tokens matching the Amber-Gold & Matte Pitch Black aesthetic
PALETTES: dict[ThemeName, dict[str, str]] = {
    DARK_THEME: {
        "bg_app": "#0C0D0E",
        "bg_sidebar": "#08090A",
        "bg_surface": "#131416",
        "bg_surface_elevated": "#1A1B1E",
        "bg_input": "#0E0F11",
        "border_subtle": "#1E2024",
        "border_normal": "#2A2D33",
        "border_focus": "#F59E0B",
        "primary": "#F59E0B",
        "primary_hover": "#FBBF24",
        "primary_pressed": "#D97706",
        "primary_subtle": "rgba(245, 158, 11, 0.12)",
        "primary_text": "#000000",
        "secondary_bg": "#181A1D",
        "secondary_hover": "#22252B",
        "secondary_text": "#D1D5DB",
        "text_primary": "#F9FAFB",
        "text_secondary": "#9CA3AF",
        "text_muted": "#6B7280",
        "success": "#10B981",
        "success_bg": "rgba(16, 185, 129, 0.12)",
        "warning": "#F59E0B",
        "warning_bg": "rgba(245, 158, 11, 0.10)",
        "danger": "#EF4444",
        "danger_bg": "rgba(239, 68, 68, 0.12)",
        "info": "#F59E0B",
        "info_bg": "rgba(245, 158, 11, 0.12)",
        "scrollbar_bg": "#0C0D0E",
        "scrollbar_handle": "#22252B",
        "scrollbar_handle_hover": "#323740",
        "table_header_bg": "#101113",
        "table_row_alt": "#0E0F11",
        "table_row_hover": "#181A1D",
        "tag_bg": "#181A1D",
        "tag_text": "#F59E0B",
    },
    LIGHT_THEME: {
        "bg_app": "#F8FAFC",
        "bg_sidebar": "#FFFFFF",
        "bg_surface": "#FFFFFF",
        "bg_surface_elevated": "#F1F5F9",
        "bg_input": "#FFFFFF",
        "border_subtle": "#E2E8F0",
        "border_normal": "#CBD5E1",
        "border_focus": "#D97706",
        "primary": "#D97706",
        "primary_hover": "#B45309",
        "primary_pressed": "#92400E",
        "primary_subtle": "#FEF3C7",
        "primary_text": "#FFFFFF",
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
        "info": "#D97706",
        "info_bg": "rgba(217, 119, 6, 0.10)",
        "scrollbar_bg": "#F8FAFC",
        "scrollbar_handle": "#CBD5E1",
        "scrollbar_handle_hover": "#94A3B8",
        "table_header_bg": "#F1F5F9",
        "table_row_alt": "#F8FAFC",
        "table_row_hover": "#F1F5F9",
        "tag_bg": "#FEF3C7",
        "tag_text": "#B45309",
    },
}


def get_palette(theme: ThemeName) -> dict[str, str]:
    """Return color dictionary for specified theme."""
    return PALETTES.get(normalize_theme(theme), PALETTES[DARK_THEME])


def apply_application_palette(theme: ThemeName) -> None:
    """Apply unified high-fidelity Qt application palette for native controls and viewports."""
    app = QApplication.instance()
    if not app:
        return

    colors = get_palette(theme)
    is_dark = normalize_theme(theme) == DARK_THEME
    palette = QPalette()

    if is_dark:
        palette.setColor(QPalette.Window, QColor(colors["bg_app"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Base, QColor(colors["bg_input"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["bg_surface"]))
        palette.setColor(QPalette.ToolTipBase, QColor(colors["bg_surface_elevated"]))
        palette.setColor(QPalette.ToolTipText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Button, QColor(colors["bg_surface"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.BrightText, QColor(colors["primary"]))
        palette.setColor(QPalette.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("#000000"))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(colors["text_muted"]))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(colors["text_muted"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(colors["text_muted"]))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(colors["border_subtle"]))
    else:
        palette.setColor(QPalette.Window, QColor(colors["bg_app"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Base, QColor(colors["bg_input"]))
        palette.setColor(QPalette.AlternateBase, QColor(colors["bg_surface_elevated"]))
        palette.setColor(QPalette.ToolTipBase, QColor(colors["bg_surface"]))
        palette.setColor(QPalette.ToolTipText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Text, QColor(colors["text_primary"]))
        palette.setColor(QPalette.Button, QColor(colors["bg_surface"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["text_primary"]))
        palette.setColor(QPalette.BrightText, QColor(colors["primary"]))
        palette.setColor(QPalette.Link, QColor(colors["primary"]))
        palette.setColor(QPalette.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(colors["text_muted"]))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(colors["text_muted"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(colors["text_muted"]))

    app.setPalette(palette)


def get_app_stylesheet(theme: ThemeName) -> str:
    """Generate global application stylesheet matching a modern cybersecurity workstation."""
    colors = get_palette(theme)
    is_dark = theme == DARK_THEME

    return f"""
        QMainWindow,
        QWidget#centralRoot,
        QFrame#contentArea,
        QStackedWidget,
        QScrollArea,
        QScrollArea > QWidget,
        QScrollArea > QWidget > QWidget,
        QScrollArea::viewport,
        QWidget#dashboardPage,
        QWidget#filesPage,
        QWidget#aboutPage,
        QWidget#settingsPage,
        QWidget#homePage,
        QWidget#aiChatPage,
        QWidget#aesPage,
        QWidget#rsaPage,
        QWidget#double_desPage,
        QWidget#triple_desPage,
        QWidget#desPage {{
            background-color: {colors["bg_app"]};
            color: {colors["text_primary"]};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            font-size: 13px;
        }}

        /* Scroll Area canvas background */
        QScrollArea {{
            background-color: {colors["bg_app"]};
            border: none;
        }}
        QScrollArea > QWidget {{
            background-color: {colors["bg_app"]};
        }}
        QScrollArea > QWidget > QWidget {{
            background-color: {colors["bg_app"]};
        }}
        QScrollArea::viewport {{
            background-color: {colors["bg_app"]};
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
            color: {"#000000" if is_dark else "#FFFFFF"};
            border: 1px solid {colors["primary"]};
            font-weight: 700;
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
            background-color: {"#24272D" if is_dark else "#E2E8F0"};
            color: {"#6B7280" if is_dark else "#94A3B8"};
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

        QPushButton#dangerButton {{
            background-color: {colors["danger"]};
            color: #FFFFFF;
            border: 1px solid {colors["danger"]};
            font-weight: 600;
        }}
        QPushButton#dangerButton:hover {{
            background-color: {"#DC2626" if is_dark else "#B91C1C"};
            border-color: {"#DC2626" if is_dark else "#B91C1C"};
        }}
        QPushButton#dangerButton:pressed {{
            background-color: {"#991B1B" if is_dark else "#7F1D1D"};
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
            background-color: {"#101726" if is_dark else "#FFFFFF"};
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
            padding: 7px 32px 7px 12px;
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
            width: 26px;
            border-left: 1px solid {colors["border_subtle"]};
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            background-color: {colors["secondary_bg"]};
        }}
        QComboBox::down-arrow {{
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {colors["text_secondary"]};
            margin-top: 1px;
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
        QTableCornerButton::section {{
            background-color: {colors["table_header_bg"]};
            border: none;
        }}
        QHeaderView::section {{
            background-color: {colors["table_header_bg"]};
            color: {colors["text_secondary"]};
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding: 8px 12px;
            border: none;
            border-bottom: 1px solid {colors["border_subtle"]};
        }}

        /* Header Labels */
        QLabel#headerTitle {{
            font-size: 20px;
            font-weight: 700;
            color: {colors["text_primary"]};
            letter-spacing: -0.3px;
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
            color: {colors["info"] if is_dark else colors["primary"]};
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
            font-size: 16px;
            color: {colors["primary"]};
            background-color: transparent;
            padding: 0px 4px;
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
            color: {colors["text_primary"]};
        }}
        QLabel#algoSpecs {{
            font-size: 12px;
            font-weight: 600;
            color: {colors["primary"]};
        }}
        QLabel#algoDesc {{
            font-size: 12px;
            color: {colors["text_secondary"]};
            line-height: 1.4;
        }}

        /* Welcome Banner & Heroes */
        QFrame#welcomeBanner, QFrame#aboutHero {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
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

        /* Top Control Bar */
        QFrame#topControlBar {{
            background-color: {colors["bg_app"]};
            border-bottom: 1px solid {colors["border_subtle"]};
            min-height: 38px;
            max-height: 38px;
        }}
        QLabel#topControlTitle {{
            color: {colors["text_muted"]};
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 0.3px;
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

        /* Advisory Banner / Security Notice */
        QFrame#advisoryFrame {{
            background-color: {colors["warning_bg"]};
            border: 1px solid {colors["warning"]};
            border-radius: 6px;
        }}
        QLabel#advisoryText {{
            font-size: 12px;
            color: {colors["text_primary"]};
            line-height: 1.4;
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
        QLabel#requiredBadge {{
            color: {colors["primary"]};
            font-size: 11px;
            font-weight: 700;
            padding-left: 4px;
        }}
        QLabel#optionalBadge {{
            color: {colors["text_muted"]};
            font-size: 11px;
            font-weight: 500;
            padding-left: 4px;
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

        /* Technical Specification Pill */
        QFrame#specPill {{
            background-color: {colors["bg_surface_elevated"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 4px;
            padding: 2px 8px;
        }}
        QLabel#specPillKey {{
            color: {colors["text_muted"]};
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        QLabel#specPillVal {{
            color: {colors["text_primary"]};
            font-size: 11px;
            font-weight: 700;
            font-family: "Consolas", monospace;
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
        QWidget#homePage,
        QWidget#aiChatPage,
        QScrollArea#chatScrollArea,
        QScrollArea#chatScrollArea > QWidget,
        QWidget#chatContent,
        QScrollArea#chatScrollArea::viewport {{
            background-color: {colors["bg_app"]};
            border: none;
        }}
        QLabel#homeTitle, QLabel#aiChatTitle {{
            color: {colors["text_primary"]};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.3px;
        }}
        QLabel#homeSubtitle, QLabel#aiChatSubtitle {{
            color: {colors["text_secondary"]};
            font-size: 13px;
        }}
        QFrame#chatInputPanel {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_normal"]};
            border-radius: 10px;
        }}
        QTextEdit#chatInput {{
            background-color: transparent;
            color: {colors["text_primary"]};
            border: none;
            font-size: 13px;
        }}
        QPushButton#pauseButton {{
            background-color: {"rgba(245, 158, 11, 0.12)" if is_dark else "#FEF3C7"};
            color: {colors["primary"]};
            border: 1px solid {colors["primary"]};
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            padding: 6px 14px;
        }}
        QPushButton#pauseButton:hover {{
            background-color: {colors["primary"]};
            color: {colors["primary_text"]};
        }}
        QPushButton#pauseButton:disabled {{
            background-color: transparent;
            color: {colors["text_muted"]};
            border-color: {colors["border_subtle"]};
        }}
        QPushButton#newChatButton {{
            background-color: transparent;
            border: 1px solid {colors["border_normal"]};
            border-radius: 6px;
            color: {colors["text_primary"]};
            font-size: 12px;
            font-weight: 600;
            padding: 6px 14px;
        }}
        QPushButton#newChatButton:hover {{
            background-color: {colors["secondary_hover"]};
            border-color: {colors["border_focus"]};
        }}
        QLabel#chatDisclaimer {{
            color: {colors["text_muted"]};
            font-size: 11px;
        }}
        QPushButton#suggestionButton {{
            background-color: {colors["secondary_bg"]};
            color: {colors["secondary_text"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 14px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        QPushButton#suggestionButton:hover {{
            background-color: {colors["primary_subtle"]};
            color: {colors["info"] if is_dark else colors["primary"]};
            border-color: {colors["primary"]};
        }}
        QFrame#userMessage {{
            background-color: {"#1E2024" if is_dark else "#E2E8F0"};
            border: 1px solid {"#2B2D33" if is_dark else "#CBD5E1"};
            border-radius: 10px;
            padding: 10px 14px;
        }}
        QLabel#userMessageTitle {{
            color: {colors["text_muted"]};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        QLabel#userMessageText {{
            color: {colors["text_primary"]};
            font-size: 13px;
            line-height: 1.4;
        }}
        QFrame#assistantMessage {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
            padding: 12px 16px;
        }}
        QLabel#assistantMessageTitle {{
            color: {colors["info"] if is_dark else colors["primary"]};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        QLabel#assistantMessageText {{
            color: {colors["text_primary"]};
            font-size: 13px;
            line-height: 1.4;
        }}
        QFrame#welcomeMessage {{
            background-color: {colors["bg_surface"]};
            border: 1px solid {colors["border_subtle"]};
            border-radius: 8px;
            padding: 14px 18px;
        }}
        QLabel#welcomeMessageTitle {{
            color: {colors["info"] if is_dark else colors["primary"]};
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
            color: {colors["info"] if is_dark else colors["primary"]};
            font-size: 13px;
            font-style: italic;
        }}
        QFrame#errorMessage {{
            background-color: {colors["danger_bg"]};
            border: 1px solid {colors["danger"]};
            border-left: 4px solid {colors["danger"]};
            border-radius: 8px;
            padding: 12px 16px;
        }}
        QLabel#errorMessageText {{
            color: {colors["text_primary"]};
            font-size: 13px;
            line-height: 1.4;
        }}
        QFrame#pausedMessage {{
            background-color: {"rgba(245, 158, 11, 0.08)" if is_dark else "#FFFBEB"};
            border: 1px solid {colors["primary"]};
            border-left: 4px solid {colors["primary"]};
            border-radius: 8px;
            padding: 12px 16px;
        }}
        QLabel#pausedMessageText {{
            color: {colors["primary"]};
            font-size: 13px;
            font-weight: 600;
        }}
        QFrame#toolResultCard {{
            background-color: {colors["bg_surface"]};
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
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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
    is_dark = theme == DARK_THEME
    return f"""
        QWidget#settingsPage,
        QScrollArea,
        QScrollArea > QWidget,
        QScrollArea > QWidget > QWidget,
        QScrollArea::viewport {{
            background-color: {colors["bg_app"]};
            border: none;
        }}
        QLabel#settingsTitle {{
            color: {colors["text_primary"]};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.3px;
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
            color: {colors["info"] if is_dark else colors["primary"]};
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
            color: {colors["info"] if is_dark else colors["primary"]};
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
        QWidget#aboutPage,
        QScrollArea,
        QScrollArea > QWidget,
        QScrollArea > QWidget > QWidget,
        QScrollArea::viewport {{
            background-color: {colors["bg_app"]};
            border: none;
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
            line-height: 1.4;
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
            font-size: 14px;
            font-weight: 700;
            color: {colors["info"] if is_dark else colors["primary"]};
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
        QWidget#filesPage,
        QScrollArea,
        QScrollArea > QWidget,
        QScrollArea > QWidget > QWidget,
        QScrollArea::viewport {{
            background-color: {colors["bg_app"]};
            border: none;
        }}
    """


def get_workspace_stylesheet(theme: ThemeName, prefix: str) -> str:
    """Return stylesheet for crypto workspace pages (AES, RSA, DES)."""
    colors = get_palette(theme)

    return f"""
        QWidget#{prefix}Page,
        QScrollArea,
        QScrollArea > QWidget,
        QScrollArea > QWidget > QWidget,
        QScrollArea::viewport {{
            background-color: {colors["bg_app"]};
            border: none;
        }}
        QLabel#{prefix}Title {{
            color: {colors["text_primary"]};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.3px;
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
            font-size: 11px;
        }}
    """
