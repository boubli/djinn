---
layout: default
title: Installation
---

# Installation Guide

DJINN can be installed multiple ways. Choose the method that works best for you.

---

## 📦 Method 1: pip (Recommended)

Install the latest stable version from PyPI:

```bash
pip install djinn-cli
```

### Upgrade to Latest Version
```bash
pip install --upgrade djinn-cli
```

### Install Specific Version
```bash
pip install djinn-cli==2.0.0
pip install djinn-cli==1.0.2
pip install djinn-cli==1.0.0
```

### Install from GitHub (Latest Dev)
```bash
pip install git+https://github.com/boubli/djinn.git
```

### Verify Installation
```bash
djinn --version
djinn --help
```

---

## 💻 Method 2: Windows Executable

Download the standalone `.exe` file (no Python required):

1. Go to [GitHub Releases](https://github.com/boubli/djinn/releases)
2. Download `djinn.exe`
3. Move to a folder in your PATH (e.g., `C:\Program Files\DJINN\`)
4. Run from any terminal: `djinn "your prompt"`

> **Note:** Windows SmartScreen may show a warning since the binary is unsigned. Click "More info" → "Run anyway".

---

## 🔧 Method 3: From Source

Clone and install in development mode:

```bash
git clone https://github.com/boubli/djinn.git
cd djinn
pip install -e .
```

This allows you to modify the code and see changes immediately.

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, Linux

### Dependencies (auto-installed)
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `requests` - HTTP client
- `pyperclip` - Clipboard support

### Optional Dependencies
```bash
# For voice control
pip install SpeechRecognition pyaudio

# For system dashboard
pip install psutil

# For database viewer
pip install psycopg2  # PostgreSQL
pip install mysql-connector-python  # MySQL
```

---

## 🤖 LLM Backend Setup

DJINN needs an LLM backend. Choose one:

### Option A: Ollama (Recommended - Free & Local)
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull llama3.2

# Configure DJINN
djinn config set provider ollama
djinn config set model llama3.2
```

### Option B: LM Studio (Local)
```bash
# Download from https://lmstudio.ai
# Start the local server

djinn config set provider lmstudio
djinn config set model <your-model>
```

### Option C: OpenAI (Cloud)
```bash
export OPENAI_API_KEY="your-key"

djinn config set provider openai
djinn config set model gpt-4
```

---

## ✅ Quick Test

After installation, test DJINN:

```bash
# Check version
djinn --version

# Get a command
djinn "list all files in current directory"

# Interactive mode
djinn -i

# System dashboard
djinn dashboard
```

---

## 🔄 Version History

| Version | Date | Highlights |
|---------|------|------------|
| **2.0.0** | 2026-01-11 | TUI Dashboard, Universal Pkg Manager, Voice Control, AI Code Reviewer |
| **1.0.2** | 2026-01-10 | 900+ plugin templates, cheatsheets, workflows, notifications |
| **1.0.0** | 2026-01-10 | Initial release with 87 commands |

---

## 🆘 Troubleshooting

### "djinn not found"
Add Python scripts to PATH:
```bash
# Windows
set PATH=%PATH%;%APPDATA%\Python\Python311\Scripts

# Linux/macOS
export PATH=$PATH:~/.local/bin
```

### "No LLM configured"
Run the setup wizard:
```bash
djinn config set provider ollama
djinn config set model llama3.2
```

### "Permission denied"
Use sudo on Linux/macOS:
```bash
sudo pip install djinn-cli
```

Or install for user only:
```bash
pip install --user djinn-cli
```
