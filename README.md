# Cipher AI — Cryptographic Security Workstation & AI Copilot

Cipher AI is an enterprise-grade desktop cybersecurity workstation built with **Python 3.12**, **PySide6 (Qt6)**, and **cryptography (OpenSSL Hazmat)**, integrated with an AI Copilot powered by Google Gemini.

The workstation combines hardened, non-blocking cryptographic engines with an AI assistant that serves a dual role: an automated workstation operator for local cryptographic workflows and an unrestricted domain expert across theoretical and applied cryptography.

---

## Table of Contents

- [Core Capabilities](#core-capabilities)
- [Cryptographic Specifications](#cryptographic-specifications)
- [AI Copilot & Domain Specialist](#ai-copilot--domain-specialist)
- [System Architecture](#system-architecture)
- [Application Workspaces](#application-workspaces)
- [Safety, Validation & Anti-Tampering](#safety-validation--anti-tampering)
- [Installation & Quickstart](#installation--quickstart)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Test Suite & Quality Assurance](#test-suite--quality-assurance)
- [Repository Structure](#repository-structure)

---

## Core Capabilities

- **Authenticated Symmetric Encryption (AES-GCM)**: Modern Galois/Counter Mode with 128-bit authentication tags and 12-byte initialization vectors/nonces to detect ciphertext tampering.
- **Legacy Symmetric Encryption (AES-CBC)**: Cipher Block Chaining with PKCS#7 padding and 16-byte random IVs.
- **Mandatory Passphrase-Protected Asymmetric Keys (RSA)**: Standard 2048, 3072, and 4096-bit key pair generation strictly requiring PKCS#8 BestAvailableEncryption with user passphrases (unencrypted private key export is completely disabled).
- **Hybrid RSA-OAEP File Encryption**: Automatic envelope encryption combining RSA-OAEP (SHA-256 / MGF1) for ephemeral key exchange and AES-256-GCM for arbitrary-sized file payloads.
- **Stream-Chunked Processing**: Buffered 64 KB memory chunks for symmetric ciphers and hashing, enabling encryption of multi-gigabyte files with negligible memory overhead.
- **Cascade DES Implementations**: Double DES (2DES with secondary derived IV) and Triple DES (3-pass file-level CBC cascade) for legacy compatibility, cryptanalysis demonstration, and educational analysis.
- **Cryptographic Hashing & Keyed HMAC**: SHA-256, SHA-512, SHA-3, BLAKE2 digests, and constant-time keyed HMAC message authentication.
- **Non-Blocking Multithreaded GUI & TaskBridge**: Asynchronous background operations managed via `CryptoTaskWorker`, `QThread`, and `TaskBridge` with `Qt.QueuedConnection`, preventing UI freezing during heavy 4096-bit key generation or file encryption while eliminating Qt cross-thread violations.
- **Interactive Passphrase Visibility Toggle**: `PasswordLineEdit` with integrated trailing eye glyphs for instant masked/unmasked viewing of private key passphrases.
- **Smart Path Conflict Resolution & Timestamped Storage**: Built-in path resolution that prevents accidental file overwrites by appending incrementing numeric suffixes, along with automated timestamped folder creation (`storage/<category>/<algorithm_name>_%Y-%m-%d_%H-%M-%S/`).
- **Cybersecurity Telemetry & Activity Auditing**: In-memory telemetry engine that logs every operation, cryptographic algorithm, outcome, and timestamp across workspaces.
- **Dynamic Theming**: Multi-palette styling engine supporting Dark Mode, Light Mode, and Cyberpunk high-contrast themes.

---

## Cryptographic Specifications

| Algorithm | Primitive | Supported Key Sizes | Modes / Padding | Nonce / IV | Key Format & Security Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AES** | Symmetric Block Cipher | 128, 192, 256 bits | **GCM** (AEAD, Default)<br>CBC (PKCS#7) | 12 bytes (GCM)<br>16 bytes (CBC) | **Raw Binary File (`.key`)**.<br>**High Assurance**: Recommended NIST FIPS 197 standard for general file encryption. Streaming 64 KB chunks. |
| **RSA** | Asymmetric Key Pair | 2048, 3072, 4096 bits | OAEP (SHA-256 / MGF1)<br>Hybrid AES-256-GCM | N/A (OAEP)<br>12 bytes (Hybrid) | **PKCS#8 PEM (`.pem`)**.<br>**High Assurance**: Mandatory passphrase encryption via PKCS#8 `BestAvailableEncryption`. Auto-hybrid for files > OAEP limit. |
| **Double DES** | Symmetric Cascade | 112 bits (2x 56-bit keys) | Cascade CBC | 8 bytes | **Raw Binary Files (`key1.key`, `key2.key`)**.<br>**Legacy / Educational**: Vulnerable to Meet-in-the-Middle attacks (effective strength ~57 bits). Derived secondary IV. |
| **Triple DES** | Symmetric Cascade | 168 bits (3x 56-bit keys) | 3-Pass CBC Cascade | 8 bytes | **Raw Binary Files (`key1.key`..`key3.key`)**.<br>**Legacy Cascade (Non-Interoperable)**: 3-pass file-level cascade ($E \rightarrow D \rightarrow E$). Non-interoperable with per-block ANSI X9.52 3DES. Vulnerable to Sweet32. |
| **Hashing & HMAC** | Cryptographic Digests & MAC | 256, 512 bits | SHA-2, SHA-3, BLAKE2b | N/A | **Integrity & Verification**: Unkeyed file/byte hashing and keyed HMAC with secret key verification using `hmac.compare_digest()`. |

---

## AI Copilot & Domain Specialist

The AI module is powered by the Google Gemini API with a dual-mode operational contract defined in `ai/prompts.py`:

### 1. Workstation Operator (`action: "tool"`)
When natural language requests describe actions on the local filesystem (such as generating keys or encrypting files), the AI constructs validated JSON tool payloads. Tool execution is strictly guarded by the application dispatcher:
- **Engine Scoping**: Execution is restricted strictly to the 4 implemented engines: `AES`, `RSA`, `DOUBLE_DES`, `TRIPLE_DES`.
- **Mandatory Parameter Validation**: If required parameters (e.g., input file path, key file path, or mandatory RSA passphrase) are missing, the AI immediately pauses and returns a clarification question (`action: "clarify"`).
- **Mandatory RSA Passphrase Contract**: The RSA prompt contract strictly requires a passphrase when generating key pairs or decrypting files; unencrypted private key requests are rejected.
- **Path Sanitization**: Target filepaths and directory structures are validated before any cryptographic Hazmat service is invoked.

### 2. Universal Cryptography Domain Expert (`action: "chat"`)
When users ask theoretical, architectural, or educational questions, the AI responds in conversational chat mode (`action: "chat"`). In this mode, the assistant has no algorithm restrictions and covers the full breadth of modern and historical cryptology across 6 primary domains defined in `DOMAIN_SCOPE`:
- **Symmetric & Stream Ciphers**: ChaCha20-Poly1305, Serpent, Twofish, Camellia, modes of operation (GCM, CTR, SIV).
- **Elliptic Curve Cryptography**: Curve25519, Ed25519, NIST P-256, secp256k1, pairing-friendly curves.
- **Post-Quantum Cryptography (PQC)**: NIST standards including ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), and lattice foundations.
- **Protocols & Architectures**: TLS 1.3, Signal Protocol (Double Ratchet), WireGuard, SSHv2, PGP/GPG, WebAuthn/FIDO2.
- **Advanced Primitives**: Zero-Knowledge Proofs (zk-SNARKs, zk-STARKs), Fully Homomorphic Encryption (FHE), Shamir's Secret Sharing.
- **Cryptanalysis & Attacks**: Side-channel analysis, timing attacks, padding oracle exploits, and quantum threat models (Shor's and Grover's).

### 3. Prompt Architecture & Rules Contract
- **General Rules (`RULES`)**: 8 concise operational constraints governing intent recognition, security recommendations, and anti-hallucination.
- **Response Rules (`RESPONSE_RULES`)**: 10 strict format directives ensuring valid, unfenced JSON responses for tool actions while granting unconstrained natural language response mode for chat.

---

## System Architecture

The application implements a strict layered architecture with clear separation of concerns:

```
┌────────────────────────────────────────────────────────┐
│                   Presentation Layer                   │
│  PySide6 Workstations: Dashboard, AES, RSA, DES, Chat  │
└───────────────────────────┬────────────────────────────┘
                            │ Dispatches tasks
┌───────────────────────────▼────────────────────────────┐
│                    Controller Layer                    │
│      AIDispatcher, ActivityTracker, CryptoTaskWorker   │
└─────────────┬────────────────────────────┬─────────────┘
              │ Direct Tool Calls          │ Background QThread
┌─────────────▼─────────────┐┌─────────────▼─────────────┐
│      AI Service Layer     ││    Cryptographic Services │
│  AIService, Parser, Tools ││ AES, RSA, DoubleDES, 3DES │
└─────────────┬─────────────┘└─────────────┬─────────────┘
              │ API Transport              │ Cryptographic Primitives
┌─────────────▼─────────────┐┌─────────────▼─────────────┐
│     Google Gemini API     ││ cryptography (OpenSSL)    │
└───────────────────────────┘└───────────────────────────┘
```

---

## Application Workspaces

1. **Cybersecurity Dashboard**:
   - High-level telemetry displaying total operations, success rates, and engine status badges.
   - Quick action launcher for instant navigation to encryption tasks (AES, RSA, File Encryption, Decryption, AI, Files).
   - Live activity log detailing operation types, algorithm variants, targets, and execution status.
   - Cryptographic environment viewer showing runtime provider information and OpenSSL versions.

2. **AES Symmetric Workspace**:
   - Cryptographically secure key generator for 128, 192, and 256-bit raw binary keys (`.key`).
   - Authenticated GCM mode (default) with 12-byte nonce input and tampering detection.
   - Standard CBC mode with PKCS#7 padding and 16-byte IV input.
   - Independent 2-column side-by-side file encryption and decryption panels.

3. **RSA Asymmetric Workspace**:
   - Key pair generator supporting 2048, 3072, and 4096-bit primes.
   - Mandatory passphrase protection for exported PKCS#8 private keys (`.pem`).
   - Integrated `PasswordLineEdit` with in-bar trailing eye action to toggle passphrase visibility between masked bullets and plain text.
   - Seamless Hybrid RSA-OAEP + AES-256-GCM envelope encryption for files of any size.
   - Secure private key decryption with mandatory passphrase prompting.

4. **DES & Triple DES Workspaces**:
   - Double DES cascade generator (2 distinct 56-bit DES keys) and Triple DES generator (3 distinct 56-bit DES keys).
   - Dedicated security notices explaining Meet-in-the-Middle and Sweet32 attack vectors.
   - File encryption and decryption with automatic IV derivation across cascade passes.

5. **AI Assistant Copilot**:
   - Interactive chat interface supporting markdown formatting and code blocks.
   - Suggestion pills for common operations and conceptual comparisons.
   - Real-time execution status indicators with pause and resume controls.
   - Structured result cards displaying key paths, file outputs, and operation parameters.
   - Non-intrusive borderless copy glyph controls (`📋`) with immediate visual checkmark feedback (`✓`).

6. **System Settings**:
   - Instant theme switching (Dark Theme, Light Theme, Cyberpunk High Contrast).
   - Environment and library audit panel.

---

## Safety, Validation & Anti-Tampering

- **Unique Path Resolution**: Every file save operation passes through `resolve_unique_path()`. If a file with the target name already exists, an incrementing numeric suffix (`_1`, `_2`) is added automatically.
- **Timestamped Default Hierarchies**: When output folders are not specified, operations automatically generate timestamped subdirectories (`storage/<category>/<algorithm>_%Y-%m-%d_%H-%M-%S/`).
- **Strict IV & Nonce Validation**: Hexadecimal IVs and nonces are trimmed and verified after hex-decoding to ensure proper byte length (12 bytes for GCM, 16 bytes for CBC, 8 bytes for DES) rather than simple character count.
- **Tamper Detection**: Decrypting an AES-GCM payload with modified ciphertext or an altered authentication tag immediately aborts with an authentication failure error.
- **Mandatory RSA Passphrase Protection**: Private key generation strictly requires a non-empty passphrase; unencrypted export (`serialization.NoEncryption()`) is completely eliminated from the codebase.
- **Thread-Safe UI Marshalling (`TaskBridge`)**: Background crypto tasks emit through `TaskBridge` using `Qt.QueuedConnection`, ensuring all widget updates and modal dialogs execute safely on the Qt main GUI thread.
- **Non-Deprecated Hazmat Imports**: Modern TripleDES imports and cipher primitives from the `cryptography` library ensure compatibility with contemporary OpenSSL releases.
- **Code Fence Normalization**: The AI parser automatically strips markdown code fences before parsing JSON responses from the Gemini API.

---

## Installation & Quickstart

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/CipherAI.git
cd CipherAI
```

### 2. Set Up a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Configuration

The AI Assistant Copilot requires an API key from Google AI Studio.

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Linux / macOS:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

*(Note: The core cryptographic workstations for AES, RSA, Double DES, and Triple DES operate completely locally and do not require an API key or internet connection.)*

---

## Running the Application

Launch the desktop suite:
```bash
python app.py
```

---

## Test Suite & Quality Assurance

The project includes a comprehensive automated test suite covering cryptographic primitives, parser validation, dispatcher routing, prompt contracts, and full GUI end-to-end flows.

Run all unit and integration tests:
```powershell
$env:PYTHONPATH=".;.venv/Lib/site-packages"; python -m unittest discover tests
```

### Test Suite Structure
The automated test suite contains **78 tests** across 10 specialized modules:
- `tests/test_crypto_enhancements.py` (16 tests): AES-GCM tampering detection, 64 KB streaming encryption, hybrid RSA-OAEP, mandatory passphrase protection, Double DES secondary IV derivation, `PasswordLineEdit` trailing toggle, and `TaskBridge` cross-thread safety.
- `tests/test_redesign_suite.py` (24 tests): Comprehensive functional UI test suite covering all workstation operations, theme changes, QThread execution, and activity tracker integration.
- `tests/test_tools.py` (9 tests): Dispatcher tool adapters, argument validation, and clarification triggers.
- `tests/test_parser.py` (7 tests): JSON schema validation, markdown code fence stripping, and payload extraction.
- `tests/test_iv_validation.py` (7 tests): Hexadecimal IV and nonce byte-length validation routines.
- `tests/test_dispatcher.py` (5 tests): Routing verification for chat, clarification, and tool execution requests.
- `tests/test_prompts.py` (4 tests): Verification of AI domain knowledge scope, dual-mode contracts, and mandatory RSA passphrase prompts.
- `tests/test_ai_service.py` (4 tests): Gemini client initialization, response formatting, and exception handling.
- `tests/test_smoke_e2e.py` (1 test): Full end-to-end GUI smoke verification executing live key generation, encryption, and decryption across AES, RSA, Double DES, and Triple DES.
- `tests/test_responsive_resizing.py` (1 test): Multi-resolution DPI and dynamic resize validation.

---

## Repository Structure

```
CipherAI/
├── ai/
│   ├── conversation.py       # Chat history and context tracking
│   ├── dispatcher.py         # Routes AI actions to tools or chat
│   ├── parser.py             # Validates and cleans JSON responses
│   ├── prompts.py            # System prompt, domain scope, and tool contracts
│   ├── service.py            # Google Gemini client integration
│   ├── session_state.py      # Working memory for recent keys and paths
│   └── tools/                # Workstation adapters (AES, RSA, DES)
│
├── core/
│   ├── paths.py              # File conflict resolution and timestamped paths
│   ├── settings.py           # Gemini model configuration and temperatures
│   └── validators.py         # IV, key, and directory validators
│
├── crypto/
│   ├── aes.py                # AES-GCM and AES-CBC symmetric service
│   ├── base_des.py           # Core DES primitives and unique path saving
│   ├── double_des.py         # Double DES cascade service
│   ├── hashing.py            # Cryptographic digests and HMAC utilities
│   ├── rsa.py                # RSA-OAEP, passphrase handling, and hybrid cipher
│   └── triple_des.py         # Triple DES 3-pass CBC cascade service
│
├── gui/
│   ├── activity.py           # In-memory activity tracking and logging
│   ├── components.py         # TaskBridge, PasswordLineEdit, CyberCard, PathPickerRow
│   ├── dialogs.py            # Styled success, error, and result dialogs
│   ├── main_window.py        # Sidebar navigation and workspace stack
│   ├── theme.py              # Dark, Light, and Cyberpunk color palettes
│   └── pages/
│       ├── aes.py            # AES workspace page
│       ├── dashboard.py      # Telemetry, activity log, and quick launcher
│       ├── des.py            # DES / Triple DES workspace page
│       ├── home.py           # AI Assistant chat workspace
│       ├── rsa.py            # RSA asymmetric workspace with passphrase toggle
│       └── settings.py       # Theme selector and system diagnostics
│
├── storage/                  # Default storage for keys, encrypted and decrypted files
├── tests/                    # 78 automated unit and integration tests
├── app.py                    # Application entry point
├── requirements.txt          # Python package dependencies
└── README.md                 # Complete project documentation
```

---

## License

This project is licensed for educational, research, and cybersecurity engineering purposes.
