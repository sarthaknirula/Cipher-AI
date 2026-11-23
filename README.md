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
- **Cascade DES Implementations**: Double DES and Triple DES (3DES EDE mode) for legacy compatibility, cryptanalysis demonstration, and educational analysis.
- **Cryptographic Hashing & HMAC**: SHA-256, SHA-512, SHA-3, BLAKE2, and HMAC verification routines.
- **Non-Blocking Multithreaded GUI**: Asynchronous background operations managed via `CryptoTaskWorker` and `QThread`, preventing UI freezing during heavy 4096-bit key generation or large file encryption.
- **Smart Path Conflict Resolution**: Built-in path resolution that prevents accidental file overwrites by appending incrementing numeric suffixes.
- **Cybersecurity Telemetry & Activity Auditing**: In-memory telemetry engine that logs every operation, cryptographic algorithm, outcome, and timestamp across workspaces.
- **Dynamic Theming**: Multi-palette styling engine supporting Dark Mode, Light Mode, and Cyberpunk high-contrast themes.

---

## Cryptographic Specifications

| Algorithm | Primitive | Supported Key Sizes | Modes / Padding | Nonce / IV | Purpose & Security Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AES** | Symmetric Block Cipher | 128, 192, 256 bits | **GCM** (AEAD, Default)<br>CBC (PKCS#7) | 12 bytes (GCM)<br>16 bytes (CBC) | **High Assurance**: Recommended NIST FIPS 197 standard for all general-purpose file encryption. |
| **RSA** | Asymmetric Key Pair | 2048, 3072, 4096 bits | OAEP (SHA-256 / MGF1)<br>Hybrid AES-256-GCM | N/A (OAEP)<br>12 bytes (Hybrid) | **High Assurance**: Public-key encryption with mandatory passphrase protection on all private keys. |
| **Double DES** | Symmetric Cascade | 112 bits (2x 56-bit keys) | Cascade CBC | 8 bytes | **Legacy / Educational**: Vulnerable to Meet-in-the-Middle attacks (effective strength ~57 bits). |
| **Triple DES** | Symmetric Cascade | 168 bits (3x 56-bit keys) | 3-Pass CBC Cascade | 8 bytes | **Legacy Cascade (Non-Interoperable)**: Implemented as a 3-pass file-level CBC cascade ($E \rightarrow D \rightarrow E$). Does not interoperate with standard per-block ANSI X9.52 3DES-CBC. Vulnerable to Sweet32 collisions. |
| **Hashing** | Cryptographic Digests | 256, 512 bits | SHA-2, SHA-3, BLAKE2 | N/A | **Integrity & Verification**: File integrity checking and constant-time HMAC message authentication. |

---

## AI Copilot & Domain Specialist

The AI module is powered by the Google Gemini API with a dual-mode operational contract:

### 1. Workstation Operator (`action: "tool"`)
When natural language requests describe actions on the local filesystem (such as generating keys or encrypting files), the AI constructs validated JSON tool payloads. Tool execution is strictly guarded by the application dispatcher:
- Execution is restricted to the 4 implemented engines: `AES`, `RSA`, `DOUBLE_DES`, `TRIPLE_DES`.
- If required parameters (e.g. input file path, key file path) are missing, the AI pauses and asks a clarification question (`action: "clarify"`).
- Target filepaths and directory structures are validated before any cryptographic Hazmat service is invoked.

### 2. Universal Cryptography Domain Expert (`action: "chat"`)
When users ask theoretical, architectural, or learning questions, the AI responds in conversational chat mode (`action: "chat"`). In this mode, the assistant has no algorithm restrictions and covers the full breadth of modern and historical cryptology:
- **Symmetric & Stream Ciphers**: ChaCha20-Poly1305, Serpent, Twofish, Camellia, modes of operation (GCM, CTR, SIV).
- **Elliptic Curve Cryptography**: Curve25519, Ed25519, NIST P-256, secp256k1, pairing-friendly curves.
- **Post-Quantum Cryptography (PQC)**: NIST standards including ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), and lattice foundations.
- **Protocols & Architectures**: TLS 1.3, Signal Protocol (Double Ratchet), WireGuard, SSHv2, PGP/GPG, WebAuthn/FIDO2.
- **Advanced Primitives**: Zero-Knowledge Proofs (zk-SNARKs, zk-STARKs), Fully Homomorphic Encryption (FHE), Shamir's Secret Sharing.
- **Cryptanalysis & Attacks**: Side-channel analysis, timing attacks, padding oracle exploits, and historical cryptanalysis.

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
   - Quick action launcher for instant navigation to encryption tasks.
   - Live activity log detailing operation types, algorithm variants, targets, and execution status.
   - Cryptographic environment viewer showing runtime provider information and OpenSSL versions.

2. **AES Symmetric Workspace**:
   - Cryptographically secure key generator for 128, 192, and 256-bit keys.
   - Authenticated GCM mode (default) with 12-byte nonce input and tampering detection.
   - Standard CBC mode with PKCS#7 padding and 16-byte IV input.
   - Independent 2-column side-by-side file encryption and decryption panels.

3. **RSA Asymmetric Workspace**:
   - Key pair generator supporting 2048, 3072, and 4096-bit primes.
   - Mandatory passphrase protection for exported PKCS#8 private keys (`.pem`).
   - Seamless Hybrid RSA-OAEP + AES-256-GCM encryption for files of any size.
   - Secure private key decryption with passphrase prompting.

4. **DES & Triple DES Workspaces**:
   - Double DES cascade generator (2 distinct 56-bit DES keys) and Triple DES generator (3 distinct 56-bit DES keys).
   - Dedicated security notices explaining Meet-in-the-Middle and Sweet32 attack vectors.
   - File encryption and decryption with automatic IV derivation across cascade passes.

5. **AI Assistant Copilot**:
   - Interactive chat interface supporting markdown formatting and code blocks.
   - Real-time execution status indicators with pause and resume controls.
   - Structured result cards displaying key paths, file outputs, and operation parameters.
   - Non-intrusive borderless copy controls with visual feedback.

6. **System Settings**:
   - Instant theme switching (Dark Theme, Light Theme, Cyberpunk High Contrast).
   - Environment and library audit panel.

---

## Safety, Validation & Anti-Tampering

- **Unique Path Resolution**: Every file save operation passes through `resolve_unique_path()`. If a file with the target name already exists, an incrementing numeric suffix (`_1`, `_2`) is added automatically.
- **Strict IV & Nonce Validation**: Hexadecimal IVs and nonces are trimmed and verified after hex-decoding to ensure proper byte length rather than simple character count.
- **Tamper Detection**: Decrypting an AES-GCM payload with modified ciphertext or an altered authentication tag immediately aborts with an authentication failure error.
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
- `tests/test_crypto_enhancements.py`: AES-GCM tampering detection, streaming encryption, hybrid RSA, passphrase protection, and filename cleanup.
- `tests/test_prompts.py`: Verification of AI domain knowledge scope, dual-mode contracts, and tool execution boundaries.
- `tests/test_dispatcher.py`: Routing verification for chat, clarification, and tool execution requests.
- `tests/test_parser.py`: JSON parsing, markdown code fence stripping, and schema validation.
- `tests/test_iv_validation.py`: Hexadecimal IV and nonce byte-length validation routines.
- `tests/test_redesign_suite.py`: Functional UI test suite covering all workstation operations, theme changes, and logging.
- `tests/test_smoke_e2e.py`: End-to-end GUI smoke tests verifying asynchronous worker threads and path propagation.
- `tests/test_responsive_resizing.py`: Multi-resolution DPI and dynamic resize validation.

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
│   ├── paths.py              # File conflict resolution and unique paths
│   ├── settings.py           # Gemini model configuration and temperatures
│   └── validators.py         # IV, key, and directory validators
│
├── crypto/
│   ├── aes.py                # AES-GCM and AES-CBC symmetric service
│   ├── base_des.py           # Core DES primitives and unique path saving
│   ├── double_des.py         # Double DES cascade service
│   ├── hashing.py            # Cryptographic digests and HMAC utilities
│   ├── rsa.py                # RSA-OAEP, passphrase handling, and hybrid cipher
│   └── triple_des.py         # Triple DES EDE service
│
├── gui/
│   ├── activity.py           # In-memory activity tracking and logging
│   ├── components.py         # Cards, headers, pickers, and CryptoTaskWorker
│   ├── dialogs.py            # Styled success, error, and result dialogs
│   ├── main_window.py        # Sidebar navigation and workspace stack
│   ├── theme.py              # Dark, Light, and Cyberpunk color palettes
│   └── pages/
│       ├── aes.py            # AES workspace page
│       ├── dashboard.py      # Telemetry, activity log, and quick launcher
│       ├── des.py            # DES / Triple DES workspace page
│       ├── home.py           # AI Assistant chat workspace
│       ├── rsa.py            # RSA asymmetric workspace page
│       └── settings.py       # Theme selector and system diagnostics
│
├── storage/                  # Default storage for keys, encrypted and decrypted files
├── tests/                    # 74 automated unit and integration tests
├── app.py                    # Application entry point
├── requirements.txt          # Python package dependencies
└── README.md                 # Complete project documentation
```

---

## License

This project is licensed for educational, research, and cybersecurity engineering purposes.
