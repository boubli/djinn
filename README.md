<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-green" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-purple" alt="License">
  <img src="https://img.shields.io/badge/commands-87-orange" alt="Commands">
</p>

<h1 align="center">⚡ DJINN</h1>
<h3 align="center">Terminal Sorcery at Your Command</h3>

<p align="center">
  <b>Convert natural language to shell commands using AI</b><br>
  87 specialized commands • Multi-LLM support • Works everywhere
</p>

---

## 👨‍💻 Developer

<p align="center">
  <a href="https://boubli.tech">
    <img src="https://img.shields.io/badge/Website-boubli.tech-10B981?style=for-the-badge" alt="Website">
  </a>
  <a href="https://github.com/boubli">
    <img src="https://img.shields.io/badge/GitHub-boubli-181717?style=for-the-badge&logo=github" alt="GitHub">
  </a>
  <a href="https://huggingface.co/TRADMSS">
    <img src="https://img.shields.io/badge/HuggingFace-TRADMSS-yellow?style=for-the-badge" alt="HuggingFace">
  </a>
</p>

**Youssef Boubli** - Creative Technologist: AI, Web & Product Design

> Multidisciplinary engineer with 7+ years of full-stack development experience. Creator of HIBA-7B (therapeutic AI) and other AI projects. Building the future with empathetic AI.

📍 Global Remote (Portugal/Morocco) | 📧 bbb.vloger@gmail.com

---

## ✨ Features

- 🤖 **AI-Powered**: Understands natural language prompts
- ⚡ **87 Commands**: Specialized plugins for every tool
- 🔄 **Multi-LLM**: Ollama, LM Studio, OpenAI
- 📋 **Auto-Copy**: Commands copied to clipboard
- 🎨 **5 Themes**: Customize your terminal
- 🔒 **Danger Detection**: Warns before destructive commands
- 💬 **Chat Mode**: Interactive AI conversation

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/boubli/djinn.git
cd djinn

# Install
pip install -e .

# Run
djinn "list all files larger than 100MB"
```

### Requirements

- Python 3.8+
- Ollama, LM Studio, or OpenAI API key

## 📖 Usage

### Basic Command

```bash
djinn "your natural language prompt"
```

### Execute Directly

```bash
djinn -x "delete all temp files"          # Execute after confirmation
djinn -x -y "create backup folder"        # Execute without confirmation
```

### Interactive Mode

```bash
djinn -i                                   # Start interactive chat
djinn chat                                 # AI conversation mode
```

## 🎯 87 Commands by Category

### 🔧 DevOps
| Command | Description |
|---------|-------------|
| `djinn git "..."` | Git commands |
| `djinn docker "..."` | Docker commands |
| `djinn k8s "..."` | Kubernetes/kubectl |
| `djinn terraform "..."` | Terraform |
| `djinn helm "..."` | Helm charts |
| `djinn ansible "..."` | Ansible playbooks |
| `djinn vagrant "..."` | Vagrant VMs |

### ☁️ Cloud
| Command | Description |
|---------|-------------|
| `djinn aws "..."` | AWS CLI |
| `djinn gcp "..."` | Google Cloud |
| `djinn azure "..."` | Azure CLI |
| `djinn ssh user@host "..."` | SSH commands |
| `djinn api "..."` | Curl/API requests |

### 🗄️ Databases
| Command | Description |
|---------|-------------|
| `djinn mysql "..."` | MySQL |
| `djinn postgres "..."` | PostgreSQL |
| `djinn redis "..."` | Redis |
| `djinn mongo "..."` | MongoDB |
| `djinn sql "..."` | SQL queries |
| `djinn graphql "..."` | GraphQL queries |

### 🛠️ System Admin
| Command | Description |
|---------|-------------|
| `djinn npm "..."` | NPM/Node.js |
| `djinn pip "..."` | Python pip |
| `djinn systemctl "..."` | Service management |
| `djinn cron "..."` | Cron jobs |
| `djinn nginx "..."` | Nginx config |

### 🔒 Security
| Command | Description |
|---------|-------------|
| `djinn firewall "..."` | Firewall/ufw |
| `djinn ssl "..."` | SSL/TLS certs |
| `djinn network "..."` | Network diagnostics |
| `djinn nmap "..."` | Port scanning |
| `djinn gpg "..."` | Encryption |

### 🎬 Multimedia
| Command | Description |
|---------|-------------|
| `djinn ffmpeg "..."` | Video/audio processing |
| `djinn magick "..."` | Image processing |

### 💻 Languages
| Command | Description |
|---------|-------------|
| `djinn python "..."` | Python commands |
| `djinn node "..."` | Node.js |
| `djinn rust "..."` | Rust/Cargo |
| `djinn go "..."` | Go |
| `djinn java "..."` | Java/Maven/Gradle |
| `djinn cpp "..."` | C++ compilation |

### 🛠️ Dev Tools
| Command | Description |
|---------|-------------|
| `djinn pytest "..."` | Pytest |
| `djinn lint "..."` | Linting tools |
| `djinn debug "..."` | Debugging |
| `djinn regex "..."` | Regex patterns |
| `djinn awk "..."` | AWK/sed |
| `djinn jq "..."` | JSON processing |
| `djinn make "..."` | Makefiles |

### 📱 Mobile
| Command | Description |
|---------|-------------|
| `djinn react "..."` | React/Next.js |
| `djinn flutter "..."` | Flutter/Dart |
| `djinn android "..."` | Android/ADB |
| `djinn ios "..."` | iOS/Xcode |

### 📊 Data & ML
| Command | Description |
|---------|-------------|
| `djinn pandas "..."` | Pandas code |
| `djinn spark "..."` | Apache Spark |
| `djinn jupyter "..."` | Jupyter notebooks |

### 🧠 AI Utilities
| Command | Description |
|---------|-------------|
| `djinn chat` | AI conversation |
| `djinn translate "cmd" --to powershell` | Shell translation |
| `djinn codegen "..." --lang python` | Code generation |
| `djinn script "..."` | Shell scripts |
| `djinn oneliner "..."` | One-liners |

### 📝 Productivity
| Command | Description |
|---------|-------------|
| `djinn commit "..."` | Commit messages |
| `djinn changelog "..."` | Changelog entries |
| `djinn readme "..."` | README sections |
| `djinn docs "..."` | Documentation |
| `djinn todo "..."` | TODO comments |

### 🔍 Smart Features
| Command | Description |
|---------|-------------|
| `djinn explain "cmd"` | Explain a command |
| `djinn undo "cmd"` | Reverse a command |
| `djinn suggest "..."` | Multiple options |
| `djinn check "cmd"` | Danger detection |
| `djinn dryrun "cmd"` | Preview effects |

### 📁 Templates & Snippets
| Command | Description |
|---------|-------------|
| `djinn template list` | View templates |
| `djinn template run python-project myapp` | Use template |
| `djinn snippet add deploy "..."` | Save snippet |
| `djinn alias add cleanup "..."` | Create alias |

## ⚙️ Configuration

```bash
djinn config --backend ollama           # Set LLM backend
djinn config --model llama3             # Set model
djinn theme hacker                      # Change theme
djinn config --show                     # View config
```

## 🎨 Themes

- `default` - Green terminal
- `hacker` - Matrix green
- `ocean` - Blue tones
- `purple` - Purple gradient
- `minimal` - Clean white

## 📦 Project Structure

```
djinn/
├── cli.py              # Main CLI (2200+ lines)
├── core/               # 14 plugin files
│   ├── engine.py       # LLM engine
│   ├── backends.py     # Ollama, LMStudio, OpenAI
│   ├── plugins.py      # Git, Docker, Undo
│   ├── cloud.py        # AWS, GCP, Azure, K8s
│   ├── ai.py           # Chat, Translate, CodeGen
│   └── ...
└── ui/
    ├── logo.py
    ├── spinner.py
    └── themes.py
```

## 🔄 Version History

### v1.0.0 (2026-01-10)
- 🎉 Initial release
- 87 specialized commands
- Multi-LLM backend support
- 5 color themes
- Template and snippet system

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new command plugins
- Improve LLM prompts
- Add new themes
- Fix bugs

## 📄 License

MIT License - © 2026 [Youssef Boubli](https://boubli.tech)

---

<p align="center">
  <b>Built with ⚡ power by <a href="https://boubli.tech">Youssef Boubli</a></b><br>
  <sub>Terminal Sorcery at Your Command</sub>
</p>
