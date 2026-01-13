<p align="center">
  <img src="assets/djinn_logo.png" alt="DJINN CLI Logo - AI Terminal Assistant" width="200">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.1-green" alt="DJINN Version 2.1.1">
  <img src="https://img.shields.io/badge/python-3.8+-blue" alt="Supports Python 3.8 and newer">
  <img src="https://img.shields.io/badge/license-MIT-purple" alt="MIT License">
  <img src="https://img.shields.io/badge/commands-60+-orange" alt="Over 60 built-in commands">
  <img src="https://img.shields.io/badge/plugins-900+-red" alt="900+ plugin templates available">
</p>

<h1 align="center">⚡ DJINN</h1>
<h3 align="center">The Ultimate AI-Powered CLI Tool</h3>

<p align="center">
  <b>Transform natural language into precise shell commands with 60+ built-in commands and 900+ plugin templates.</b><br>
  TUI Dashboard • Universal Package Manager • Voice Control • AI Code Reviewer
</p>

---

## 🚀 Quick Start

```bash
# Install from PyPI
pip install djinn-cli

# Or download the Windows executable
# https://github.com/boubli/djinn/releases
```

```bash
# Your first command
djinn "list all docker containers sorted by size"

# Interactive mode
djinn -i
```

---

## ✨ Features Overview

### 🤖 Core AI Commands
| Command | Description |
|---------|-------------|
| `djinn "prompt"` | Convert natural language to shell command |
| `djinn -i` | Interactive chat mode |
| `djinn explain "cmd"` | Explain any command in detail |
| `djinn redo` | Regenerate last command |
| `djinn alias` | Manage command aliases |

### 📊 TUI (Full-Screen Interactive)
| Command | Description |
|---------|-------------|
| `djinn dashboard` | System monitor (CPU, RAM, Disk, Network) |
| `djinn explore` | Interactive file manager |
| `djinn db connect file.db` | Database viewer (SQLite/PostgreSQL/MySQL) |
| `djinn http get URL` | API testing client |

### 📦 Universal Tools
| Command | Description |
|---------|-------------|
| `djinn pkg install X` | Smart package manager (npm/pip/cargo/go/gem) |
| `djinn setup new node` | Project templates |
| `djinn flow run my-build` | Workflow automation |
| `djinn env list` | .env file management |

### 🧠 AI & Automation
| Command | Description |
|---------|-------------|
| `djinn voice` | Voice control (speech recognition) |
| `djinn review` | AI-powered code reviewer |
| `djinn docs readme` | Auto-generate documentation |
| `djinn why "error"` | Explain why commands fail |

### 🔧 DevOps & Plugins
| Command | Description |
|---------|-------------|
| `djinn cheat docker` | Built-in cheatsheets |
| `djinn compose generate` | Docker Compose generator |
| `djinn scan` | Dependency vulnerability scanner |
| `djinn release bump minor` | Git release automation |

### 🎯 Productivity
| Command | Description |
|---------|-------------|
| `djinn learn shortcut` | Save personalized shortcuts |
| `djinn schedule add cmd +1h` | Schedule commands |
| `djinn record start` | Record terminal sessions |
| `djinn ssh list` | SSH connection manager |

### 🎮 Fun & Learning
| Command | Description |
|---------|-------------|
| `djinn game typing` | CLI typing practice |
| `djinn game quiz` | Test your CLI knowledge |
| `djinn speak "message"` | Text-to-speech |

---

## � Complete Command Reference

### AI Commands
```bash
djinn "natural language prompt"     # Generate command
djinn -i                            # Interactive mode
djinn explain "git rebase -i"       # Explain command
djinn suggest                       # Context suggestions
djinn redo                          # Regenerate last
djinn translate "cmd" --to bash     # Translate between shells
```

### Plugin Commands (900+ Templates)
```bash
djinn plugin docker ps              # Docker commands
djinn plugin aws s3 ls              # AWS commands
djinn plugin k8s get pods           # Kubernetes
djinn plugin git log                # Git commands
djinn plugin security scan          # Security tools
```

### Configuration
```bash
djinn config set provider ollama    # Set LLM provider
djinn config set model llama3       # Set model
djinn theme list                    # List themes
djinn theme set cyberpunk           # Set theme
```

### System Dashboard
```bash
djinn dashboard                     # Launch system monitor
# Shows: CPU usage, RAM, Disk space, Network I/O, Top processes
# Press Ctrl+C to exit
```

### Package Manager
```bash
djinn pkg info                      # Show detected manager
djinn pkg install react             # Auto-detects npm/pip/cargo
djinn pkg install flask -D          # Dev dependency
djinn pkg list                      # List packages
djinn pkg outdated                  # Check outdated
```

### Database Viewer
```bash
djinn db connect mydb.sqlite        # Connect to SQLite
djinn db tables mydb.sqlite         # List tables
djinn db query mydb.sqlite "SELECT * FROM users LIMIT 10"
```

### HTTP Client
```bash
djinn http get https://api.github.com
djinn http post https://api.example.com -d '{"name":"test"}'
djinn http get URL -H "Authorization:Bearer token"
```

### File Explorer
```bash
djinn explore                       # Launch file explorer
djinn explore /var/log              # Start in specific path
# Commands: ls, cd, tree, mkdir, rm, pwd, q
```

### Voice Control
```bash
djinn voice                         # Single voice command
djinn voice --listen                # Continuous listening
# Say: "list files", "git status", "docker containers"
```

### Code Review
```bash
djinn review                        # Review uncommitted changes
djinn review --staged               # Review staged only
djinn review file.py                # Review specific file
```

### Project Architect
```bash
djinn architect list                # List templates
djinn architect create fullstack-react-node myapp
djinn architect stacks              # Quick stack templates
djinn setup new fastapi             # Quick setup
```

### Workflows
```bash
djinn flow templates                # List templates
djinn flow create my-deploy         # Create workflow
djinn flow run my-deploy            # Run workflow
djinn flow run my-deploy --dry-run  # Preview
```

### Environment Management
```bash
djinn env list                      # List .env variables
djinn env get API_KEY               # Get variable
djinn env set API_KEY value         # Set variable
djinn env backup                    # Backup .env
djinn dotfiles backup               # Backup dotfiles
```

### Scheduling
```bash
djinn schedule add "npm test" +1h   # Run in 1 hour
djinn schedule add "backup" +30m    # Run in 30 min
djinn schedule list                 # List pending
djinn schedule run                  # Run due tasks
```

### SSH Manager
```bash
djinn ssh list                      # List connections
djinn ssh add server host user      # Add connection
djinn ssh keys                      # List SSH keys
```

---

## � LLM Providers

DJINN supports multiple AI backends:

| Provider | Local | Setup |
|----------|-------|-------|
| **Ollama** | ✅ | `ollama serve` |
| **LM Studio** | ✅ | Start local server |
| **OpenAI** | ❌ | Set `OPENAI_API_KEY` |

```bash
djinn config set provider ollama
djinn config set model llama3.2
djinn model list                    # List installed models
djinn model download codellama      # Download model
```

---

## 📦 Installation

### Option 1: Automated Script (Recommended)
**Windows (PowerShell):**
```powershell
powershell -c "irm https://raw.githubusercontent.com/boubli/djinn/master/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -fsSL https://raw.githubusercontent.com/boubli/djinn/master/install.sh | bash
```

### Option 2: Standalone Executable (No Python Required)
Download the latest binaries for Windows (`.exe`), macOS, and Linux from [GitHub Releases](https://github.com/boubli/djinn/releases).
Just download and run!

### Option 3: Python Package (Pip)
```bash
pip install djinn-cli
```

### Option 4: Homebrew (macOS/Linux)
```bash
brew install --HEAD https://raw.githubusercontent.com/boubli/djinn/master/homebrew/djinn.rb
```

### Option 5: Docker
```bash
docker build -t djinn .
docker run --rm -it djinn "list files"
```

### Option 6: From Source
```bash
git clone https://github.com/boubli/djinn
cd djinn
pip install -e .
```

---

## 🎨 Themes

```bash
djinn theme list                    # Available themes
djinn theme set <theme>             # Set theme
```

Available: `default`, `cyberpunk`, `retro`, `nord`, `dracula`, `solarized`, `monokai`, `light`

---

## 📄 License

MIT License - © 2026 [Youssef Boubli](https://boubli.tech)

---

<p align="center">
  <b>Built with ⚡ by <a href="https://boubli.tech">Youssef Boubli</a></b>
</p>
