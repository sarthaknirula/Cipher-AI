"""Files workspace showing processed files and session audit logs."""

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
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
from gui.components import EmptyState, PageHeader
from gui.dialogs import show_info
from gui.theme import DARK_THEME, ThemeName, get_files_stylesheet


class FilesPage(QWidget):
    """Files and cryptographic audit workspace."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("filesPage")
        self._theme = DARK_THEME
        self._tracker = get_activity_tracker()

        self._build_ui()
        self._apply_styles()
        self._tracker.activity_recorded.connect(self._refresh_table)
        self._tracker.activities_cleared.connect(self._refresh_table)
        self._refresh_table()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("filesScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(20)

        # Header with actions
        header_row = QHBoxLayout()
        header = PageHeader(
            "Workspace Files & Session Audit",
            "Real-time audit log of all keys generated, files encrypted, and files decrypted during this session.",
            badge_text="Session Active",
            badge_status="info",
        )
        header_row.addWidget(header, stretch=1)

        self.clear_btn = QPushButton("Clear Session Log")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self._tracker.clear)
        header_row.addWidget(self.clear_btn, alignment=Qt.AlignVCenter)

        layout.addLayout(header_row)

        # Container for Table or Empty State
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table_container, stretch=1)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _refresh_table(self) -> None:
        while self.table_layout.count():
            item = self.table_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        items = self._tracker.get_all()
        if not items:
            empty = EmptyState(
                None,
                "No Processed Files in Current Session",
                "Files encrypted, decrypted, or keys generated during your session will appear here with location and status details.",
            )
            self.table_layout.addWidget(empty)
            return

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(
            ["Target Name", "Operation", "Algorithm", "Absolute Location", "Status", "Timestamp"]
        )
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(items))

        for row, item in enumerate(items):
            file_item = QTableWidgetItem(item.target_name)
            op_item = QTableWidgetItem(item.operation)
            algo_item = QTableWidgetItem(item.algorithm)
            loc_item = QTableWidgetItem(item.target_path)
            loc_item.setToolTip(item.target_path)
            status_item = QTableWidgetItem(item.status)
            time_item = QTableWidgetItem(item.timestamp)

            for it in (file_item, op_item, algo_item, loc_item, status_item, time_item):
                it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            table.setItem(row, 0, file_item)
            table.setItem(row, 1, op_item)
            table.setItem(row, 2, algo_item)
            table.setItem(row, 3, loc_item)
            table.setItem(row, 4, status_item)
            table.setItem(row, 5, time_item)

        # Controls under table
        btn_bar = QHBoxLayout()
        btn_bar.setContentsMargins(0, 10, 0, 0)
        btn_bar.setSpacing(10)

        copy_btn = QPushButton("Copy Selected Path")
        copy_btn.setObjectName("secondaryButton")
        copy_btn.setFixedHeight(34)
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: self._copy_selected_path(table))
        btn_bar.addWidget(copy_btn)

        open_folder_btn = QPushButton("Open Containing Folder")
        open_folder_btn.setObjectName("secondaryButton")
        open_folder_btn.setFixedHeight(34)
        open_folder_btn.setCursor(Qt.PointingHandCursor)
        open_folder_btn.clicked.connect(lambda: self._open_selected_folder(table))
        btn_bar.addWidget(open_folder_btn)

        btn_bar.addStretch()

        self.table_layout.addWidget(table, stretch=1)
        self.table_layout.addLayout(btn_bar)

    def _copy_selected_path(self, table: QTableWidget) -> None:
        row = table.currentRow()
        if row >= 0:
            item = table.item(row, 3)
            if item:
                clipboard = QGuiApplication.clipboard()
                if clipboard:
                    clipboard.setText(item.text())
                    show_info(self, "Path Copied", "File path copied to clipboard.", item.text())

    def _open_selected_folder(self, table: QTableWidget) -> None:
        row = table.currentRow()
        if row >= 0:
            item = table.item(row, 3)
            if item:
                folder = Path(item.text()).parent
                if folder.exists():
                    if sys.platform == "win32":
                        os.startfile(folder)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", str(folder)])
                    else:
                        subprocess.Popen(["xdg-open", str(folder)])

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        self._apply_styles()
        self._refresh_table()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_files_stylesheet(self._theme))
