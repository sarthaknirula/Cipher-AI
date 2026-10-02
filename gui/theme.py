from typing import Literal


ThemeName = Literal["Dark", "Light"]

DARK_THEME: ThemeName = "Dark"
LIGHT_THEME: ThemeName = "Light"
THEME_OPTIONS: tuple[ThemeName, ThemeName] = (DARK_THEME, LIGHT_THEME)


def normalize_theme(theme: str | None) -> ThemeName:
    """Return a supported theme name, defaulting to dark."""
    if theme == LIGHT_THEME:
        return LIGHT_THEME

    return DARK_THEME


def get_message_box_stylesheet(theme: ThemeName) -> str:
    """Return readable, theme-matched styling for every Qt message box."""
    if theme == LIGHT_THEME:
        return """
            QMessageBox {
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                color: #1F2933;
            }

            QMessageBox QLabel {
                background-color: transparent;
                color: #1F2933;
            }

            QMessageBox QPushButton {
                background-color: #E8EEF5;
                border: 1px solid #C7D2DE;
                border-radius: 6px;
                color: #1F2933;
                min-width: 72px;
                padding: 6px 12px;
            }

            QMessageBox QPushButton:hover,
            QMessageBox QPushButton:default {
                background-color: #1976D2;
                border-color: #1976D2;
                color: #FFFFFF;
            }
        """

    return """
        QMessageBox {
            background-color: #1B1B1B;
            border: 1px solid #303030;
            color: #FFFFFF;
        }

        QMessageBox QLabel {
            background-color: transparent;
            color: #FFFFFF;
        }

        QMessageBox QPushButton {
            background-color: #2A2A2A;
            border: 1px solid #454545;
            border-radius: 6px;
            color: #FFFFFF;
            min-width: 72px;
            padding: 6px 12px;
        }

        QMessageBox QPushButton:hover,
        QMessageBox QPushButton:default {
            background-color: #1976D2;
            border-color: #1976D2;
            color: #FFFFFF;
        }
    """


def get_app_stylesheet(theme: ThemeName) -> str:
    if theme == LIGHT_THEME:
        return """
            QMainWindow {
                background-color: #F5F7FA;
                color: #1F2933;
            }

            #sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #DDE3EA;
            }

            #sidebarBrand {
                color: #111827;
                font-size: 18px;
                font-weight: 700;
            }

            #navigationButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: #52606D;
                font-size: 15px;
                font-weight: 600;
                padding: 11px 14px;
                text-align: left;
            }

            #navigationButton:hover {
                background-color: #1976D2;
                color: #FFFFFF;
            }

            #navigationButton[active="true"] {
                background-color: #005BBB;
                color: #FFFFFF;
            }

            #contentArea,
            QStackedWidget,
            #placeholderPage {
                background-color: #F5F7FA;
            }

            #placeholderTitle {
                color: #111827;
                font-size: 34px;
                font-weight: 700;
            }

            #placeholderSubtitle {
                color: #52606D;
                font-size: 15px;
            }

            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                color: #1F2933;
            }

            QMenu::item:selected {
                background-color: #1976D2;
                color: #FFFFFF;
            }

            QDialog {
                background-color: #FFFFFF;
                color: #1F2933;
            }

            QTableView,
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #F5F7FA;
                border: 1px solid #DDE3EA;
                color: #1F2933;
                gridline-color: #DDE3EA;
                selection-background-color: #1976D2;
                selection-color: #FFFFFF;
            }

            QHeaderView::section {
                background-color: #E8EEF5;
                border: 1px solid #DDE3EA;
                color: #1F2933;
                font-weight: 700;
                padding: 6px;
            }
        """ + get_message_box_stylesheet(theme)

    return """
        QMainWindow {
            background-color: #121212;
            color: #ffffff;
        }

        #sidebar {
            background-color: #1B1B1B;
            border-right: 1px solid #2d2d2d;
        }

        #sidebarBrand {
            color: #ffffff;
            font-size: 18px;
            font-weight: 700;
        }

        #navigationButton {
            background-color: transparent;
            border: none;
            border-radius: 8px;
            color: #B0B0B0;
            font-size: 15px;
            font-weight: 600;
            padding: 11px 14px;
            text-align: left;
        }

        #navigationButton:hover {
            background-color: #1976D2;
            color: #ffffff;
        }

        #navigationButton[active="true"] {
            background-color: #005BBB;
            color: #ffffff;
        }

        #contentArea,
        QStackedWidget,
        #placeholderPage {
            background-color: #121212;
        }

        #placeholderTitle {
            color: #ffffff;
            font-size: 34px;
            font-weight: 700;
        }

        #placeholderSubtitle {
            color: #B0B0B0;
            font-size: 15px;
        }

        QTableView,
        QTableWidget {
            background-color: #151515;
            alternate-background-color: #1F1F1F;
            border: 1px solid #303030;
            color: #ffffff;
            gridline-color: #303030;
            selection-background-color: #005BBB;
            selection-color: #FFFFFF;
        }

        QHeaderView::section {
            background-color: #232323;
            border: 1px solid #303030;
            color: #ffffff;
            font-weight: 700;
            padding: 6px;
        }
    """ + get_message_box_stylesheet(theme)


def get_home_stylesheet(theme: ThemeName) -> str:
    if theme == LIGHT_THEME:
        return """
            #homePage {
                background-color: #F5F7FA;
            }

            #homeTitle {
                color: #111827;
                font-size: 32px;
                font-weight: 800;
            }

            #homeSubtitle {
                color: #52606D;
                font-size: 16px;
            }

            #chatScrollArea {
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                border-radius: 10px;
            }

            #chatContent {
                background-color: #FFFFFF;
            }

            #suggestionScrollArea,
            #suggestionContent {
                background-color: transparent;
                border: none;
            }

            #suggestionScrollArea {
                max-height: 48px;
            }

            #chatInputPanel {
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                border-radius: 10px;
            }

            #chatInput {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                color: #1F2933;
                font-size: 14px;
                padding: 10px 12px;
            }

            #chatInput:focus {
                border: 1px solid #1976D2;
            }

            #sendButton {
                background-color: #1976D2;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
                padding: 0 16px;
            }

            #sendButton:hover {
                background-color: #1565C0;
            }

            #sendButton:disabled {
                background-color: #A0AEC0;
                color: #F8FAFC;
            }

            #suggestionButton {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 16px;
                color: #1976D2;
                font-size: 13px;
                font-weight: 600;
                padding: 0 12px;
                text-align: center;
            }

            #suggestionButton:hover {
                background-color: #E8F1FB;
                border-color: #90CDF4;
            }

            #suggestionButton:disabled {
                background-color: #EDF2F7;
                color: #94A3B8;
            }

            #userMessage {
                background-color: #1976D2;
                border: 1px solid #1565C0;
                border-radius: 14px;
                padding: 12px 15px;
            }

            #assistantMessage {
                background-color: #F8FAFC;
                border: 1px solid #DDE3EA;
                border-radius: 14px;
                padding: 12px 15px;
            }

            #welcomeMessage {
                background-color: #FFFFFF;
                border: 1px solid #D7E3F1;
                border-radius: 14px;
                padding: 18px 20px;
            }

            #thinkingMessage {
                background-color: #EFF4F8;
                border: 1px solid #DDE3EA;
                border-radius: 14px;
                padding: 12px 15px;
            }

            #toolMessage {
                background-color: #EDF7F0;
                border: 1px solid #B7DFC3;
                border-radius: 14px;
                padding: 12px 15px;
            }

            #errorMessage {
                background-color: #FFF5F5;
                border: 1px solid #F4B5B5;
                border-radius: 14px;
                padding: 12px 15px;
            }

            #assistantMessageTitle {
                color: #111827;
                font-size: 17px;
                font-weight: 800;
            }

            #welcomeMessageTitle {
                color: #111827;
                font-size: 18px;
                font-weight: 800;
            }

            #assistantMessageText,
            #welcomeMessageText {
                color: #1F2933;
                font-size: 14px;
            }

            #userMessageText {
                color: #FFFFFF;
                font-size: 14px;
            }

            #thinkingMessageText {
                color: #52606D;
                font-size: 14px;
            }

            #toolMessageText {
                color: #1E5631;
                font-size: 14px;
            }

            #errorMessageText {
                color: #9B2C2C;
                font-size: 14px;
            }

            #messageMeta {
                color: #7B8794;
                font-size: 11px;
            }

            #toolResultCard {
                background-color: #EDF7F0;
                border: 1px solid #B7DFC3;
                border-radius: 14px;
                padding: 16px 18px;
            }

            #toolResultTitle {
                color: #1E5631;
                font-size: 16px;
                font-weight: 800;
            }

            #toolResultLabel {
                color: #52606D;
                font-size: 11px;
                font-weight: 700;
            }

            #toolResultValue {
                color: #1F2933;
                font-size: 14px;
            }

            QScrollBar:vertical {
                background-color: #EEF2F6;
                border: none;
                margin: 2px;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background-color: #C1CAD4;
                border-radius: 5px;
                min-height: 24px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #A5B3C2;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
                border: none;
            }

            QScrollBar:horizontal {
                background-color: transparent;
                border: none;
                height: 8px;
                margin: 0;
            }

            QScrollBar::handle:horizontal {
                background-color: #C1CAD4;
                border-radius: 4px;
                min-width: 32px;
            }
        """

    return """
        #homePage {
            background-color: #121212;
        }

        #homeTitle {
            color: #FFFFFF;
            font-size: 32px;
            font-weight: 800;
        }

        #homeSubtitle {
            color: #B0B0B0;
            font-size: 16px;
        }

        #chatScrollArea {
            background-color: #1B1B1B;
            border: 1px solid #303030;
            border-radius: 10px;
        }

        #chatContent {
            background-color: #1B1B1B;
        }

        #suggestionScrollArea,
        #suggestionContent {
            background-color: transparent;
            border: none;
        }

        #suggestionScrollArea {
            max-height: 48px;
        }

        #chatInputPanel {
            background-color: #1B1B1B;
            border: 1px solid #303030;
            border-radius: 10px;
        }

        #chatInput {
            background-color: #151515;
            border: 1px solid #3A3A3A;
            border-radius: 8px;
            color: #FFFFFF;
            font-size: 14px;
            padding: 10px 12px;
        }

        #chatInput:focus {
            border: 1px solid #39C2D7;
        }

        #sendButton {
            background-color: #1976D2;
            border: none;
            border-radius: 8px;
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 700;
            padding: 0 16px;
        }

        #sendButton:hover {
            background-color: #1565C0;
        }

        #sendButton:disabled {
            background-color: #4A5568;
            color: #CBD5E0;
        }

        #suggestionButton {
            background-color: #232323;
            border: 1px solid #3A3A3A;
            border-radius: 16px;
            color: #8AB4F8;
            font-size: 13px;
            font-weight: 600;
            padding: 0 12px;
            text-align: center;
        }

        #suggestionButton:hover {
            background-color: #2C3642;
            border-color: #5B708B;
        }

        #suggestionButton:disabled {
            background-color: #1A1A1A;
            color: #6B7280;
        }

        #userMessage {
            background-color: #0F4C81;
            border: 1px solid #1663A6;
            border-radius: 14px;
            padding: 12px 15px;
        }

        #assistantMessage {
            background-color: #232323;
            border: 1px solid #303030;
            border-radius: 14px;
            padding: 12px 15px;
        }

        #welcomeMessage {
            background-color: #232323;
            border: 1px solid #354456;
            border-radius: 14px;
            padding: 18px 20px;
        }

        #thinkingMessage {
            background-color: #1F1F1F;
            border: 1px solid #353535;
            border-radius: 14px;
            padding: 12px 15px;
        }

        #toolMessage {
            background-color: #173021;
            border: 1px solid #2B5B3B;
            border-radius: 14px;
            padding: 12px 15px;
        }

        #errorMessage {
            background-color: #432020;
            border: 1px solid #7A3838;
            border-radius: 14px;
            padding: 12px 15px;
        }

        #assistantMessageTitle {
            color: #FFFFFF;
            font-size: 17px;
            font-weight: 800;
        }

        #welcomeMessageTitle {
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 800;
        }

        #assistantMessageText,
        #welcomeMessageText {
            color: #F5F5F5;
            font-size: 14px;
        }

        #userMessageText {
            color: #FFFFFF;
            font-size: 14px;
        }

        #thinkingMessageText {
            color: #B0B0B0;
            font-size: 14px;
        }

        #toolMessageText {
            color: #D7F4DC;
            font-size: 14px;
        }

        #errorMessageText {
            color: #FFD7D7;
            font-size: 14px;
        }

        #messageMeta {
            color: #8A8A8A;
            font-size: 11px;
        }

        #toolResultCard {
            background-color: #173021;
            border: 1px solid #2B5B3B;
            border-radius: 14px;
            padding: 16px 18px;
        }

        #toolResultTitle {
            color: #D7F4DC;
            font-size: 16px;
            font-weight: 800;
        }

        #toolResultLabel {
            color: #A7B3C2;
            font-size: 11px;
            font-weight: 700;
        }

        #toolResultValue {
            color: #F5F5F5;
            font-size: 14px;
        }

        QScrollBar:vertical {
            background-color: #151515;
            border: none;
            margin: 2px;
            width: 10px;
        }

        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 5px;
            min-height: 24px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #707070;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical,
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {
            background: transparent;
            border: none;
        }

        QScrollBar:horizontal {
            background-color: transparent;
            border: none;
            height: 8px;
            margin: 0;
        }

        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 4px;
            min-width: 32px;
        }
    """


def get_settings_stylesheet(theme: ThemeName) -> str:
    if theme == LIGHT_THEME:
        return """
            #settingsPage {
                background-color: #F5F7FA;
            }

            #settingsCard {
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                border-radius: 8px;
            }

            #settingsTitle {
                color: #111827;
                font-size: 32px;
                font-weight: 800;
            }

            #settingsSubtitle {
                color: #52606D;
                font-size: 15px;
            }

            QLabel {
                color: #1F2933;
                font-size: 14px;
                font-weight: 500;
            }

            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                color: #1F2933;
                font-size: 14px;
                min-height: 38px;
                padding: 0 12px;
            }

            QComboBox:focus {
                border: 1px solid #1976D2;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                color: #1F2933;
                selection-background-color: #1976D2;
                selection-color: #FFFFFF;
            }
        """

    return """
        #settingsPage {
            background-color: #121212;
        }

        #settingsCard {
            background-color: #1F1F1F;
            border: 1px solid #303030;
            border-radius: 8px;
        }

        #settingsTitle {
            color: #ffffff;
            font-size: 32px;
            font-weight: 800;
        }

        #settingsSubtitle {
            color: #B0B0B0;
            font-size: 15px;
        }

        QLabel {
            color: #D8D8D8;
            font-size: 14px;
            font-weight: 500;
        }

        QComboBox {
            background-color: #151515;
            border: 1px solid #3A3A3A;
            border-radius: 6px;
            color: #ffffff;
            font-size: 14px;
            min-height: 38px;
            padding: 0 12px;
        }

        QComboBox:focus {
            border: 1px solid #39C2D7;
        }

        QComboBox QAbstractItemView {
            background-color: #151515;
            border: 1px solid #3A3A3A;
            color: #ffffff;
            selection-background-color: #005BBB;
            selection-color: #FFFFFF;
        }
    """


def get_workspace_stylesheet(theme: ThemeName, prefix: str) -> str:
    if theme == LIGHT_THEME:
        return f"""
            #{prefix}Page {{
                background-color: #F5F7FA;
                color: #1F2933;
            }}

            #{prefix}ScrollArea,
            #{prefix}ScrollArea > QWidget > QWidget,
            #{prefix}Content {{
                background-color: #F5F7FA;
            }}

            #{prefix}Title {{
                color: #111827;
                font-size: 32px;
                font-weight: 800;
            }}

            #{prefix}Subtitle {{
                color: #52606D;
                font-size: 15px;
            }}

            QGroupBox {{
                background-color: #FFFFFF;
                border: 1px solid #DDE3EA;
                border-radius: 8px;
                color: #111827;
                font-size: 17px;
                font-weight: 700;
                margin-top: 14px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                padding: 0 8px;
            }}

            QLabel,
            QRadioButton {{
                color: #1F2933;
                font-size: 14px;
                font-weight: 500;
            }}

            #fieldLabel {{
                color: #1F2933;
            }}

            #helperText {{
                color: #6B7280;
                font-size: 12px;
                font-weight: 400;
            }}

            QLineEdit,
            QComboBox {{
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                color: #1F2933;
                font-size: 14px;
                min-height: 38px;
                padding: 0 12px;
            }}

            QLineEdit:focus,
            QComboBox:focus {{
                border: 1px solid #1976D2;
            }}

            QLineEdit::placeholder {{
                color: #8A97A6;
            }}

            QComboBox QAbstractItemView {{
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                color: #1F2933;
                selection-background-color: #1976D2;
                selection-color: #FFFFFF;
            }}

            QRadioButton {{
                spacing: 9px;
                padding-right: 10px;
            }}

            QRadioButton::indicator {{
                height: 16px;
                width: 16px;
            }}

            QRadioButton::indicator:unchecked {{
                border: 2px solid #9AA6B2;
                border-radius: 8px;
                background-color: #FFFFFF;
            }}

            QRadioButton::indicator:checked {{
                border: 2px solid #1976D2;
                border-radius: 8px;
                background-color: #1976D2;
            }}

            #primaryButton,
            #secondaryButton {{
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 700;
                min-height: 38px;
                padding: 0 18px;
            }}

            #primaryButton {{
                background-color: #005BBB;
                color: #FFFFFF;
                min-width: 138px;
            }}

            #primaryButton:hover {{
                background-color: #1976D2;
            }}

            #secondaryButton {{
                background-color: #E8EEF5;
                border: 1px solid #CBD5E1;
                color: #1F2933;
                min-width: 92px;
            }}

            #secondaryButton:hover {{
                background-color: #DDE6F0;
            }}

            QScrollBar:vertical {{
                background-color: #F5F7FA;
                border: none;
                width: 12px;
                margin: 0;
            }}

            QScrollBar::handle:vertical {{
                background-color: #CBD5E1;
                border-radius: 6px;
                min-height: 32px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: #9AA6B2;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """ + get_message_box_stylesheet(theme)

    return f"""
        #{prefix}Page {{
            background-color: #121212;
            color: #ffffff;
        }}

        #{prefix}ScrollArea,
        #{prefix}ScrollArea > QWidget > QWidget,
        #{prefix}Content {{
            background-color: #121212;
        }}

        #{prefix}Title {{
            color: #ffffff;
            font-size: 32px;
            font-weight: 800;
        }}

        #{prefix}Subtitle {{
            color: #B0B0B0;
            font-size: 15px;
        }}

        QGroupBox {{
            background-color: #1F1F1F;
            border: 1px solid #303030;
            border-radius: 8px;
            color: #ffffff;
            font-size: 17px;
            font-weight: 700;
            margin-top: 14px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 16px;
            padding: 0 8px;
        }}

        QLabel,
        QRadioButton {{
            color: #D8D8D8;
            font-size: 14px;
            font-weight: 500;
        }}

        #fieldLabel {{
            color: #D8D8D8;
        }}

        #helperText {{
            color: #8F8F8F;
            font-size: 12px;
            font-weight: 400;
        }}

        QLineEdit,
        QComboBox {{
            background-color: #151515;
            border: 1px solid #3A3A3A;
            border-radius: 6px;
            color: #ffffff;
            font-size: 14px;
            min-height: 38px;
            padding: 0 12px;
        }}

        QLineEdit:focus,
        QComboBox:focus {{
            border: 1px solid #39C2D7;
        }}

        QLineEdit::placeholder {{
            color: #7F7F7F;
        }}

        QComboBox QAbstractItemView {{
            background-color: #151515;
            border: 1px solid #3A3A3A;
            color: #ffffff;
            selection-background-color: #005BBB;
            selection-color: #FFFFFF;
        }}

        QRadioButton {{
            spacing: 9px;
            padding-right: 10px;
        }}

        QRadioButton::indicator {{
            height: 16px;
            width: 16px;
        }}

        QRadioButton::indicator:unchecked {{
            border: 2px solid #6A6A6A;
            border-radius: 8px;
            background-color: #151515;
        }}

        QRadioButton::indicator:checked {{
            border: 2px solid #39C2D7;
            border-radius: 8px;
            background-color: #39C2D7;
        }}

        #primaryButton,
        #secondaryButton {{
            border: none;
            border-radius: 6px;
            color: #ffffff;
            font-size: 14px;
            font-weight: 700;
            min-height: 38px;
            padding: 0 18px;
        }}

        #primaryButton {{
            background-color: #005BBB;
            min-width: 138px;
        }}

        #primaryButton:hover {{
            background-color: #1976D2;
        }}

        #secondaryButton {{
            background-color: #2D2D2D;
            min-width: 92px;
        }}

        #secondaryButton:hover {{
            background-color: #3A3A3A;
        }}
    """ + get_message_box_stylesheet(theme)
