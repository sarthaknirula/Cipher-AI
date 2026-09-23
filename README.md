# Cipher AI

Cipher AI is a desktop application built with **Python** and **PySide6** that
provides cryptographic utilities through a clean graphical interface. The project
focuses on modular architecture, separation of concerns, and extensibility. It
also includes an AI-powered assistant that helps users understand and perform
cryptographic workflows through the existing application services.

> **Project Status:** 🚧 Under Active Development

---

# Current Features

## Encryption Algorithms

### AES
- File Encryption
- File Decryption
- Secure Key Generation
- Optional hexadecimal IV support for encryption

### RSA
- RSA Key Pair Generation
- Encryption
- Decryption

### Double DES
- File Encryption
- File Decryption
- Key Generation
- Optional hexadecimal IV support for encryption

### Triple DES
- File Encryption
- File Decryption
- Key Generation
- Optional hexadecimal IV support for encryption

---

# Validation Behaviour

The application validates required paths before cryptographic services run.

- Input files and key files must exist.
- Explicit output directories must already exist.
- If an AI-requested output directory does not exist, the assistant pauses and
  asks whether the user wants to provide another directory or use the default
  application output directory.
- The application does not silently change a user-provided output location.
- When the default output directory is selected, the application reports the actual generated file path.

IV handling is centralized through a shared validator.

- String IVs are trimmed before validation.
- IVs are parsed using Python's `bytes.fromhex()`.
- Validation checks the decoded byte array, not the raw string length.
- AES requires a 16-byte IV, represented as 32 hexadecimal characters.
- Double DES and Triple DES use the DES-family CBC block size, so their IVs are
  validated against the byte length required by the underlying cipher.

---

# AI Assistant

The project includes an AI assistant powered by the Gemini API.

Current progress includes:

- Gemini API integration
- Persistent chat session
- Prompt engineering
- Modular AI architecture
- Dedicated AI service layer
- JSON response parsing and dispatch
- Tool adapters for supported crypto services
- Path validation before tool execution

The AI assistant is designed to:

- Explain cryptographic concepts
- Recommend suitable encryption algorithms
- Understand user intent
- Return structured JSON responses for application actions
- Ask clarification questions when required information is missing or invalid

The AI **does not perform cryptographic operations directly**. Instead, it
delegates operations to the existing cryptographic service layer.

---

# Architecture

The application follows a layered architecture.

```text
GUI

↓

Service Layer

↓

Cryptographic Operations

↓

Filesystem
```

Each feature follows the same design philosophy.

Example:

```text
AES Page

↓

AES Service

↓

Storage
```

---

# AI Architecture

The AI module follows the architecture below.

```text
User

↓

AI Page

↓

AI Service

↓

Gemini API

↓

Structured JSON

↓

Parser

↓

Dispatcher

↓

Tools

↓

Cryptographic Services
```

This design keeps responsibilities clearly separated and allows the AI system to
grow independently of the cryptographic implementation.

---

# Project Structure

```text
CipherAI/

├── ai/
│   ├── dispatcher.py
│   ├── parser.py
│   ├── prompts.py
│   ├── service.py
│   ├── session_state.py
│   └── tools/
│
├── assets/
├── core/
├── crypto/
├── gui/
├── storage/
├── tests/
│
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

---

# Technologies Used

- Python
- PySide6
- Google Gemini API
- Cryptography Library
- unittest

---

# Installation

Clone the repository.

```bash
git clone <repository-url>
cd CipherAI
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the virtual environment.

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

---

# Gemini API Configuration

Generate a Gemini API key from Google AI Studio.

Export the API key as an environment variable.

### Linux / macOS

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

### Windows

```cmd
set GEMINI_API_KEY=YOUR_API_KEY
```

The application automatically loads the API key from the environment.

---

# Running the Application

```bash
python app.py
```

---

# Running Tests

Run the focused local tests that do not require the Gemini client dependency.

```bash
python -m unittest tests.test_tools tests.test_iv_validation
```

Run all tests.

```bash
python -m unittest discover -s tests
```

The full test suite imports the Gemini AI service. If the Google Gemini package
is not installed, full discovery will fail with a missing `google.genai`
dependency.

An interactive smoke test is available for manually testing the AI service.

```bash
python tests/test_ai_service.py
```

---

# Design Principles

The project is built around the following principles:

- Separation of Concerns
- Single Responsibility Principle
- Modular Design
- Maintainability
- Extensibility
- Clean Architecture

---

# Future Improvements

## AI Assistant

- AI-powered workflow automation
- Context-aware conversations
- Better prompt engineering

## Cryptography

- Digital Signatures
- Hashing Algorithms
- HMAC Support
- Secure File Hash Verification
- Certificate Management
- Hybrid Encryption (AES + RSA)

## Application

- File drag-and-drop support
- Recent operations history
- User preferences
- Theme customization
- Logging system
- Better error reporting
- Plugin architecture
- Improved key management
- Secure key vault

---

# License

This project is intended for educational and learning purposes.
