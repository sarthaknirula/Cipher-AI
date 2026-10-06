import sys
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

# Ensure environment variables from .env (e.g. GEMINI_API_KEY) are loaded
load_dotenv()


def main() -> int:
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
