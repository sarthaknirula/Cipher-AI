"""Test responsiveness and resizing across 1280x720, 1366x768, and 1920x1080."""

import sys
import unittest
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

APP = QApplication.instance() or QApplication(sys.argv)

from gui.main_window import MainWindow


class ResponsiveResizingTest(unittest.TestCase):
    """Verify application layouts adapt to standard desktop screen resolutions."""

    RESOLUTIONS = [
        (1280, 720),
        (1366, 768),
        (1920, 1080),
    ]

    PAGES = [
        "dashboard",
        "ai_assistant",
        "aes",
        "rsa",
        "double_des",
        "triple_des",
        "files",
        "settings",
        "about",
    ]

    def test_resize_across_resolutions(self) -> None:
        window = MainWindow()
        window.show()

        for width, height in self.RESOLUTIONS:
            window.resize(width, height)
            APP.processEvents()

            self.assertGreaterEqual(window.width(), window.minimumWidth())
            self.assertGreaterEqual(window.height(), window.minimumHeight())

            # Navigate through every page at this resolution
            for page in self.PAGES:
                window._navigate_to_page(page)
                APP.processEvents()
                current_widget = window._pages.currentWidget()
                self.assertIsNotNone(current_widget)
                self.assertTrue(current_widget.isVisible())

        window.close()


if __name__ == "__main__":
    unittest.main()
