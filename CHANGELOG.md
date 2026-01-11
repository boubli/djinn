# Changelog

All notable changes to DJINN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.2] - 2026-01-11

### Added
- 🧠 **Deep Directory Context** - DJINN reads project files for smarter suggestions
- 🛠️ **Auto-Fix Mode** - Failed commands trigger automatic fix suggestions
- 📊 `djinn stats` - View personal usage statistics
- 🔄 `djinn redo` - Re-run last command with modifications
- 📋 `djinn clipboard` - Manage clipboard history
- 🔐 `djinn vault` - Secure storage for sensitive commands
- 🧩 `djinn plugin` - Community plugin marketplace
- ⛓️ `djinn chain` - Chain multiple commands with AI
- 🌐 `djinn web` - Web-knowledge powered command search
- 🎓 `djinn tour` - Interactive feature tour
- ⌨️ `djinn completion` - Shell completion for Bash/Zsh/Fish/PowerShell
- 🤖 `djinn model` - Download & manage local LLMs (Ollama)

### Pro Features
- 📚 `djinn cheat` - Built-in cheatsheets (git, docker, k8s, linux, npm, python, aws, postgres)
- 🐳 `djinn compose` - Docker Compose generator (7 templates + AI)
- 🔍 `djinn scan` - Dependency vulnerability scanner (npm, pip)
- 🚀 `djinn release` - Git release automation (bump, tag, changelog)
- 💾 `djinn sync` - Export/import settings across machines
- 🔮 `djinn predict` - Smart command suggestions
- 🔔 `djinn notify` - Desktop notifications
- ✨ Animated ASCII logo

### Themes
- 7 new themes: cyberpunk, retro, nord, dracula, solarized, light, monokai

### 🚀 Plugin Library (200+ Features)
- **Security**: Secrets scanning, encryption, SSL certs, SSH, firewall, audit
- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, SQLite, Elasticsearch, Cassandra, InfluxDB
- **Networking**: DNS, ports, curl, wget, tcpdump, netcat, ARP, bandwidth testing
- **Cloud**: AWS, GCP, Azure, DigitalOcean, Heroku, Vercel, Netlify
- **System Admin**: Process, service, disk, memory, user, permissions, cron, packages, logs, backup
- **Containers**: Docker (50+ commands), Docker Compose, Kubernetes (60+ commands), Helm, Podman
- **Development**: Node/npm, Python/pip/poetry, Go, Rust, Java/Maven/Gradle, .NET, Ruby, PHP, Flutter, Terraform, Ansible
- **Git**: 100+ git commands, GitHub CLI, GitLab CLI
- **Files**: find, grep, sed, awk, text tools, archive, diff, encoding, jq, yq
- **API**: HTTPie, curl, gRPC, WebSocket, OpenAPI, web servers, Lighthouse
- **Monitoring**: top/htop, sar, dstat, benchmarks, profiling, network monitor
- **Misc**: tmux, screen, FFmpeg, ImageMagick, yt-dlp, PDF tools, QR codes, weather, ASCII art

### 🔮 Innovative Features
- 🧠 `djinn learn` - Learn from your patterns, create shortcuts
- 🔄 `djinn flow` - Multi-step workflow automation
- 🌿 `djinn env` - .env file management
- 🎬 `djinn record` - Terminal session recording
- 📝 `djinn docs` - Auto-generate documentation
- ❓ `djinn why` - Explain WHY commands failed
- ⏰ `djinn schedule` - Schedule commands for later
- 🎮 `djinn game` - Typing practice & CLI quiz
- 🔊 `djinn speak` - Text-to-speech notifications  
- 📦 `djinn setup` - Quick project templates (node, python, fastapi, express)
- 💾 `djinn dotfiles` - Backup/restore dotfiles
- 🔗 `djinn gist` - Share as GitHub Gist

### 🖥️ TUI & Advanced Features (v2.0)
- 📊 `djinn dashboard` - Full-screen system monitor (CPU, RAM, Disk, Network, Processes)
- 📦 `djinn pkg` - Universal package manager (npm/pip/cargo/go/gem/composer/brew)
- 🗄️ `djinn db` - Interactive database viewer (SQLite, PostgreSQL, MySQL)
- 🌐 `djinn http` - API testing client (GET, POST, PUT, DELETE with headers)
- 📁 `djinn explore` - Interactive file explorer with cd, ls, tree, mkdir, rm
- 🎤 `djinn voice` - Voice control (speech recognition)
- 🔍 `djinn review` - AI-powered code reviewer
- 📐 `djinn architect` - Project architecture templates (fullstack, microservices, monorepo)
- 🔑 `djinn ssh` - SSH connection manager

## [1.0.0] - 2026-01-10

### Added
- 🎉 Initial release of DJINN
- 87 specialized commands across 14 categories
- Multi-LLM backend support (Ollama, LM Studio, OpenAI)
- 5 color themes (default, hacker, ocean, purple, minimal)
- Template system with 6 built-in templates
- Snippet system for saving multi-line commands
- Alias system for shortcuts
- Danger detection for destructive commands
- Dry-run mode to preview command effects
- AI chat mode for interactive conversations
- Shell translation between bash/powershell/zsh
- Code generation in any language
- Commit message generation
- README and changelog generation
- Fuzzy search through history

### Commands by Category
- **Core**: djinn, explain, undo, suggest, check, dryrun
- **DevOps**: git, docker, k8s, terraform, helm, ansible, vagrant
- **Cloud**: aws, gcp, azure, ssh, api
- **Databases**: mysql, postgres, redis, mongo, sql, graphql
- **Languages**: python, node, rust, go, java, cpp
- **AI**: chat, translate, codegen, script, oneliner
- **Productivity**: commit, changelog, readme, docs, todo
- **Security**: firewall, ssl, network, nmap, gpg
- **Mobile**: react, flutter, android, ios
- **Data/ML**: pandas, spark, jupyter
- And many more...

### Technical
- Click-based CLI architecture
- Modular plugin system
- Rich terminal UI with spinners
- Clipboard integration
- SQLite history storage
- JSON configuration
