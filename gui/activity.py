"""Session activity tracking for cryptographic operations and workspace files."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Signal


@dataclass
class ActivityItem:
    """Single cryptographic operation record."""

    operation: str  # e.g. "Key Generation", "Encryption", "Decryption"
    algorithm: str  # e.g. "AES-256", "RSA-4096", "Double DES", "Triple DES"
    target_name: str  # e.g. "aes.key", "secret.txt.aes.enc"
    target_path: str  # full path string
    status: str  # "Success", "Failed"
    timestamp: str  # "HH:MM:SS"


class ActivityTracker(QObject):
    """Singleton tracker for session operations."""

    activity_recorded = Signal(object)
    activities_cleared = Signal()

    _instance: "ActivityTracker | None" = None

    def __init__(self) -> None:
        super().__init__()
        self._items: list[ActivityItem] = []

    @classmethod
    def instance(cls) -> "ActivityTracker":
        if cls._instance is None:
            cls._instance = ActivityTracker()
        return cls._instance

    def record(
        self,
        operation: str,
        algorithm: str,
        target_path: Path | str,
        status: str = "Success",
    ) -> ActivityItem:
        path_obj = Path(target_path)
        item = ActivityItem(
            operation=operation,
            algorithm=algorithm,
            target_name=path_obj.name,
            target_path=str(path_obj.resolve()),
            status=status,
            timestamp=datetime.now().strftime("%H:%M:%S"),
        )
        self._items.insert(0, item)
        self.activity_recorded.emit(item)
        return item

    def get_recent(self, limit: int = 10) -> list[ActivityItem]:
        return self._items[:limit]

    def get_all(self) -> list[ActivityItem]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()
        self.activities_cleared.emit()


def get_activity_tracker() -> ActivityTracker:
    return ActivityTracker.instance()
