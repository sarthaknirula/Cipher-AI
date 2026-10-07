"""About page detailing CipherAI architecture, cryptographic algorithms, and security guidelines."""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.components import (
    CyberCard,
    PageHeader,
    StatusBadge,
    create_cipher_shield_pixmap,
)
from gui.theme import DARK_THEME, ThemeName, get_about_stylesheet


class AboutPage(QWidget):
    """About page for CipherAI application architecture and cryptographic details."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("aboutPage")
        self._theme = DARK_THEME

        self._build_ui()
        self._apply_styles()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("aboutScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(24)

        # Header
        header = PageHeader(
            "About CipherAI",
            "Next-generation AI-powered cryptographic workstation.",
            badge_text="V2.0 ENTERPRISE",
            badge_status="info",
        )
        layout.addWidget(header)

        # Hero Brand Banner
        hero = QFrame()
        hero.setObjectName("aboutHero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(22, 18, 22, 18)
        hero_layout.setSpacing(6)

        title = QLabel("CipherAI Cryptographic Suite")
        title.setObjectName("heroTitle")

        desc = QLabel(
            "CipherAI pairs industry-standard cryptographic primitives with natural-language AI "
            "reasoning to streamline encryption, key management, and cryptographic workflows."
        )
        desc.setObjectName("heroSub")
        desc.setWordWrap(True)

        hero_layout.addWidget(title)
        hero_layout.addWidget(desc)
        layout.addWidget(hero)

        # Card 1: Architectural Pipeline
        pipe_card = CyberCard(
            "AI Cryptographic Pipeline",
            "Non-blocking multi-stage execution hierarchy operating outside the GUI thread.",
        )
        pipe_layout = QVBoxLayout()
        pipe_layout.setSpacing(10)

        pipe_desc = QLabel(
            "CipherAI utilizes an asynchronous QThread worker architecture to ensure the GUI remains fluid "
            "during complex cryptographic operations and AI reasoning:\n\n"
            "  GUI Layer (PySide6 / Qt)\n"
            "    ↓ (Dispatched via QThread worker)\n"
            "  AI Service (Google Gemini client with session memory)\n"
            "    ↓ (Structured JSON contract)\n"
            "  AI Parser (Strict schema validation & intent routing)\n"
            "    ↓\n"
            "  AI Dispatcher (Safe parameter binding & validation)\n"
            "    ↓\n"
            "  Tool Layer (AES, RSA, Double DES, Triple DES Adapters)\n"
            "    ↓\n"
            "  Cryptographic Services (Hazmat OpenSSL primitives)\n"
            "    ↓\n"
            "  File & Validation Layer (Atomic file writes & verification)"
        )
        pipe_desc.setObjectName("archCodeText")
        pipe_desc.setWordWrap(True)
        pipe_layout.addWidget(pipe_desc)
        pipe_card.add_layout(pipe_layout)
        layout.addWidget(pipe_card)

        # Card 2: Algorithms & Standards
        algo_card = CyberCard(
            "Cryptographic Algorithms & Standards Profile",
            "Specifications and security profiles implemented within the suite.",
        )
        algo_layout = QVBoxLayout()
        algo_layout.setSpacing(12)

        algos = [
            (
                "AES (Advanced Encryption Standard)",
                "Standard: NIST FIPS 197 | Mode: CBC | Padding: PKCS#7\n"
                "Key Sizes: 128, 192, 256 bits | IV: 16-byte cryptographically secure random bytes.\n"
                "Status: Recommended for all production symmetric data protection.",
            ),
            (
                "RSA (Rivest-Shamir-Adleman)",
                "Standard: PKCS#1 v2.2 | Padding: OAEP with SHA-256 and MGF1\n"
                "Key Sizes: 2048, 3072, 4096 bits | Exponent: 65537\n"
                "Status: Recommended for secure asymmetric payload exchange and digital key distribution.",
            ),
            (
                "Double DES (2-Key 2DES)",
                "Standard: ANSI X3.92 Cascade | Mode: CBC | 2 Distinct 56-bit DES Keys\n"
                "Status: Legacy / Compatibility only. Susceptible to meet-in-the-middle attacks.",
            ),
            (
                "Triple DES (3DES-EDE)",
                "Standard: NIST SP 800-67 Rev 2 | Mode: CBC | 3 Distinct 56-bit DES Keys (168-bit total)\n"
                "Status: Legacy / Compatibility only. Phased out in modern cryptographic suites.",
            ),
        ]

        for name, spec in algos:
            box = QFrame()
            box.setObjectName("algoCard")
            b_lay = QVBoxLayout(box)
            b_lay.setContentsMargins(14, 12, 14, 12)
            b_lay.setSpacing(4)

            n_lbl = QLabel(name)
            n_lbl.setObjectName("algoName")
            s_lbl = QLabel(spec)
            s_lbl.setObjectName("algoSpecs")

            b_lay.addWidget(n_lbl)
            b_lay.addWidget(s_lbl)
            algo_layout.addWidget(box)

        algo_card.add_layout(algo_layout)
        layout.addWidget(algo_card)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def apply_theme(self, theme: ThemeName) -> None:
        self._theme = theme
        is_dark = theme == DARK_THEME
        if hasattr(self, "logo_label"):
            self.logo_label.setPixmap(create_cipher_shield_pixmap(54, is_dark=is_dark))
        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(get_about_stylesheet(self._theme))
