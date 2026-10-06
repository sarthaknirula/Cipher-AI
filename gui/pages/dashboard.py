"""Executive dashboard for CipherAI."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gui.activity import ActivityItem, get_activity_tracker
from gui.components import EmptyState, PageHeader, StatusBadge
from gui.theme import DARK_THEME, ThemeName, get_palette


class StatCard(QFrame):
    """Metric card showing system component status."""

    def __init__(
        self,
        title: str,
        value: str,
        sub: str,
        status: str = "success",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setFixedHeight(94)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(3)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        lbl = QLabel(title.upper())
        lbl.setObjectName("statTitle")
        header_row.addWidget(lbl)
        header_row.addStretch()

        badge = StatusBadge("ACTIVE", status)
        header_row.addWidget(badge)
        layout.addLayout(header_row)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("statValue")
        layout.addWidget(val_lbl)

        sub_lbl = QLabel(sub)
        sub_lbl.setObjectName("statSub")
        layout.addWidget(sub_lbl)


class QuickActionCard(QPushButton):
    """Clickable quick action tile without emojis."""

    def __init__(
        self,
        tag: str,
        title: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("quickActionBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(78)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        tag_lbl = QLabel(tag)
        tag_lbl.setObjectName("qaTag")
        tag_lbl.setFixedHeight(22)
        tag_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(tag_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setAlignment(Qt.AlignVCenter)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("qaTitle")

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("qaDesc")

        text_col.addWidget(title_lbl)
        text_col.addWidget(desc_lbl)
        layout.addLayout(text_col, stretch=1)


class AlgorithmCard(QFrame):
    """Card displaying a supported crypto algorithm with launch button."""

    action_clicked = Signal(str)

    def __init__(
        self,
        tag: str,
        name: str,
        specs: str,
        description: str,
        page_key: str,
        is_legacy: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("algoCard")
        self.page_key = page_key

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setObjectName("algoName")
        header_row.addWidget(name_lbl)
        header_row.addStretch()

        badge_status = "warning" if is_legacy else "success"
        badge_text = "Legacy" if is_legacy else tag
        badge = StatusBadge(badge_text, badge_status)
        header_row.addWidget(badge)
        layout.addLayout(header_row)

        specs_lbl = QLabel(specs)
        specs_lbl.setObjectName("algoSpecs")
        layout.addWidget(specs_lbl)

        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("algoDesc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl, stretch=1)

        btn = QPushButton(f"Open {name} Workspace")
        btn.setObjectName("secondaryButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(32)
        btn.clicked.connect(lambda: self.action_clicked.emit(self.page_key))
        layout.addWidget(btn)


class DashboardPage(QWidget):
    """Central overview dashboard."""

    navigate_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboardPage")
        self._theme = DARK_THEME

        self._build_ui()
        self._tracker = get_activity_tracker()
        self._tracker.activity_recorded.connect(self._refresh_activity)
        self._tracker.activities_cleared.connect(self._refresh_activity)
        self._refresh_activity()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("dashboardScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 28, 36, 36)
        layout.setSpacing(22)

        # Header
        header = PageHeader(
            "Dashboard",
            "Cryptographic workspace, active engines, and session operations.",
            badge_text="System Ready",
            badge_status="success",
        )
        layout.addWidget(header)

        # Welcome Banner
        welcome_banner = QFrame()
        welcome_banner.setObjectName("welcomeBanner")
        banner_layout = QVBoxLayout(welcome_banner)
        banner_layout.setContentsMargins(22, 18, 22, 18)
        banner_layout.setSpacing(4)

        hero_title = QLabel("Welcome to CipherAI")
        hero_title.setObjectName("heroTitle")

        hero_sub = QLabel(
            "Cryptographic operations and key management from a single workspace."
        )
        hero_sub.setObjectName("heroSub")

        banner_layout.addWidget(hero_title)
        banner_layout.addWidget(hero_sub)
        layout.addWidget(welcome_banner)

        # Status Cards Row
        status_row = QHBoxLayout()
        status_row.setSpacing(12)
        status_row.addWidget(
            StatCard("AES Engine", "AES-CBC Active", "128 / 192 / 256-bit PKCS#7")
        )
        status_row.addWidget(
            StatCard("RSA Engine", "RSA-OAEP Active", "2048 / 3072 / 4096-bit Keys")
        )
        status_row.addWidget(
            StatCard("Legacy DES", "2DES / 3DES Ready", "Compatibility Cascade")
        )
        status_row.addWidget(
            StatCard("AI Assistant", "Gemini 3.5 Flash", "Natural Language Engine")
        )
        layout.addLayout(status_row)

        # Quick Actions Section
        qa_label = QLabel("QUICK ACTIONS")
        qa_label.setObjectName("sidebarSectionHeader")
        layout.addWidget(qa_label)

        qa_grid = QGridLayout()
        qa_grid.setSpacing(10)

        btn_aes_key = QuickActionCard("AES", "Generate AES Key", "Create 128, 192, or 256-bit symmetric key")
        btn_aes_key.clicked.connect(lambda: self.navigate_requested.emit("aes"))

        btn_rsa_key = QuickActionCard("RSA", "Generate RSA Keys", "Create 2048, 3072, or 4096-bit key pair")
        btn_rsa_key.clicked.connect(lambda: self.navigate_requested.emit("rsa"))

        btn_enc = QuickActionCard("ENC", "Encrypt File", "Encrypt file using AES-CBC encryption")
        btn_enc.clicked.connect(lambda: self.navigate_requested.emit("aes"))

        btn_dec = QuickActionCard("DEC", "Decrypt File", "Restore encrypted file to original plaintext")
        btn_dec.clicked.connect(lambda: self.navigate_requested.emit("aes"))

        btn_ai = QuickActionCard("AI", "AI Assistant", "Execute crypto commands via natural language")
        btn_ai.clicked.connect(lambda: self.navigate_requested.emit("ai_assistant"))

        qa_grid.addWidget(btn_aes_key, 0, 0)
        qa_grid.addWidget(btn_rsa_key, 0, 1)
        qa_grid.addWidget(btn_enc, 0, 2)
        qa_grid.addWidget(btn_dec, 1, 0)
        qa_grid.addWidget(btn_ai, 1, 1)

        layout.addLayout(qa_grid)

        # Supported Algorithms Cards
        algo_title = QLabel("SUPPORTED ALGORITHMS")
        algo_title.setObjectName("sidebarSectionHeader")
        layout.addWidget(algo_title)

        algo_grid = QGridLayout()
        algo_grid.setSpacing(12)

        card_aes = AlgorithmCard(
            "Standard",
            "AES",
            "CBC Mode • PKCS#7 Padding • 16-byte IV",
            "Advanced Encryption Standard approved by NIST. Fast, high-assurance symmetric encryption.",
            "aes",
        )
        card_aes.action_clicked.connect(self.navigate_requested.emit)

        card_rsa = AlgorithmCard(
            "Asymmetric",
            "RSA",
            "OAEP Padding • SHA-256 • 2048-4096 bit",
            "Rivest-Shamir-Adleman asymmetric cryptosystem for secure key exchange and payload protection.",
            "rsa",
        )
        card_rsa.action_clicked.connect(self.navigate_requested.emit)

        card_ddes = AlgorithmCard(
            "Legacy",
            "Double DES",
            "CBC Mode • 2 Distinct 56-bit Keys",
            "Sequential double-pass Data Encryption Standard cascade. Maintained for backward compatibility.",
            "double_des",
            is_legacy=True,
        )
        card_ddes.action_clicked.connect(self.navigate_requested.emit)

        card_tdes = AlgorithmCard(
            "Legacy",
            "Triple DES",
            "3DES-EDE • 3 Distinct 56-bit Keys",
            "Triple Data Encryption Standard in Encrypt-Decrypt-Encrypt mode with three independent keys.",
            "triple_des",
            is_legacy=True,
        )
        card_tdes.action_clicked.connect(self.navigate_requested.emit)

        algo_grid.addWidget(card_aes, 0, 0)
        algo_grid.addWidget(card_rsa, 0, 1)
        algo_grid.addWidget(card_ddes, 1, 0)
        algo_grid.addWidget(card_tdes, 1, 1)

        layout.addLayout(algo_grid)

        # Recent Activity Section
        recent_title = QLabel("RECENT OPERATIONS")
        recent_title.setObjectName("sidebarSectionHeader")
        layout.addWidget(recent_title)

        self.activity_container = QWidget()
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.activity_container)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _refresh_activity(self) -> None:
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        items = self._tracker.get_recent(10)
        if not items:
            empty = EmptyState(
                None,
                "No Recent Activity",
                "Operations executed during your session (key generation, encryption, decryption) will appear here.",
            )
            self.activity_layout.addWidget(empty)
            return

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ["Operation", "Algorithm", "Target / File", "Status", "Time"]
        )
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(items))
        table.setFixedHeight(min(320, 38 * len(items) + 38))

        for row, item in enumerate(items):
            op_item = QTableWidgetItem(item.operation)
            algo_item = QTableWidgetItem(item.algorithm)
            target_item = QTableWidgetItem(item.target_name)
            target_item.setToolTip(item.target_path)
            status_item = QTableWidgetItem(item.status)
            time_item = QTableWidgetItem(item.timestamp)

            for it in (op_item, algo_item, target_item, status_item, time_item):
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            table.setItem(row, 0, op_item)
            table.setItem(row, 1, algo_item)
            table.setItem(row, 2, target_item)
            table.setItem(row, 3, status_item)
            table.setItem(row, 4, time_item)

        self.activity_layout.addWidget(table)

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self._refresh_activity()
