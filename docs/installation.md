# Installation Guide

## 🚀 Quick Install

### Windows (PowerShell)
```powershell
powershell -c "irm https://raw.githubusercontent.com/boubli/djinn/master/install.ps1 | iex"
```

### macOS / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/boubli/djinn/master/install.sh | bash
```

---

## 📦 Other Methods

### Pip (Python Package)
If you have Python installed:
```bash
pip install djinn-cli
```

### Standalone Binary (No Python Required)
Download the latest executable for your OS from [GitHub Releases](https://github.com/boubli/djinn/releases).

### Homebrew (macOS)
```bash
brew install --HEAD https://raw.githubusercontent.com/boubli/djinn/master/homebrew/djinn.rb
```

### Docker
```bash
docker build -t djinn .
docker run --rm -it djinn "list files"
```

---

## 🔄 Updating DJINN

To get the latest features and bug fixes:

**If installed via Pip:**
```bash
pip install --upgrade djinn-cli
```

**If installed via Script:**
Simply run the install script again. It detects existing installations and updates them.

---

## 🗑️ Uninstalling

We're sad to see you go! Here is how to remove DJINN:

**If installed via Pip:**
```bash
pip uninstall djinn-cli
```

**If installed via Script (Windows):**
Delete the `djinn.exe` from your Scripts folder (usually `%LOCALAPPDATA%\Programs\Python\Python3x\Scripts`).

**If installed via Script (Mac/Linux):**
```bash
rm /usr/local/bin/djinn
```
