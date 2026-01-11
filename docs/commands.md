---
layout: default
title: Commands Reference
---

# Complete Command Reference

DJINN provides 60+ built-in commands and 900+ plugin templates. This page documents every command.

---

## Core AI Commands

### Natural Language to Command
```bash
djinn "your natural language prompt"
```
Converts natural language into a shell command.

**Examples:**
```bash
djinn "list all files larger than 100MB"
djinn "find all Python files modified today"
djinn "show disk usage sorted by size"
```

### Interactive Mode
```bash
djinn -i
djinn --interactive
```
Start an interactive chat session with DJINN.

### Explain Command
```bash
djinn explain "command"
```
Get a detailed explanation of any command.

### Redo
```bash
djinn redo
```
Regenerate the last command with a different approach.

### Suggest
```bash
djinn suggest
```
Get AI-powered suggestions based on your current directory.

---

## TUI Commands (Full-Screen Interactive)

### System Dashboard
```bash
djinn dashboard
```
Launch a full-screen system monitor showing:
- CPU usage (per core)
- Memory usage (RAM + Swap)
- Disk usage
- Network I/O
- Top processes

**Controls:** Press `Ctrl+C` to exit.

### File Explorer
```bash
djinn explore [path]
```
Interactive terminal file manager.

**Commands within explorer:**
- `ls` - List files
- `ls -a` - Show hidden files
- `cd <dir>` - Change directory
- `tree` - Show directory tree
- `mkdir <name>` - Create directory
- `rm <name>` - Remove file/directory
- `pwd` - Print working directory
- `q` - Quit

### Database Viewer
```bash
djinn db connect <file.sqlite>    # Connect to SQLite
djinn db tables <file.sqlite>     # List tables
djinn db query <file> "SQL"       # Execute query
djinn db info <file.sqlite>       # Get DB info
```

**Example:**
```bash
djinn db query myapp.db "SELECT * FROM users LIMIT 10"
```

### HTTP Client
```bash
djinn http get <url>
djinn http post <url> -d '<json>'
djinn http put <url> -d '<json>'
djinn http delete <url>
```

**Options:**
- `-d, --data` - JSON data for POST/PUT
- `-H, --header` - Custom header (key:value)

**Examples:**
```bash
djinn http get https://api.github.com/users/octocat
djinn http post https://api.example.com/users -d '{"name":"John"}'
djinn http get https://api.secure.com -H "Authorization:Bearer token123"
```

---

## Package Management

### Universal Package Manager
```bash
djinn pkg info                    # Show detected manager
djinn pkg install <package>       # Install package
djinn pkg install <package> -D    # Install as dev dependency
djinn pkg uninstall <package>     # Remove package
djinn pkg list                    # List installed
djinn pkg update [package]        # Update packages
djinn pkg outdated                # Check for outdated
```

**Supported Managers:** npm, yarn, pnpm, pip, poetry, cargo, go, gem, composer, apt, brew

**Example:**
```bash
cd my-python-project
djinn pkg install requests        # Auto-detects pip
cd ../my-node-project
djinn pkg install react           # Auto-detects npm
```

---

## AI & Automation

### Voice Control
```bash
djinn voice                       # Single command
djinn voice --listen              # Continuous mode
```
**Requires:** `pip install SpeechRecognition pyaudio`

**Supported phrases:**
- "list files" → `ls -la`
- "git status" → `git status`
- "docker containers" → `docker ps`
- "run tests" → `npm test`

### AI Code Review
```bash
djinn review                      # Review uncommitted changes
djinn review --staged             # Review staged only
djinn review <file>               # Review specific file
```

### Why Explainer
```bash
djinn why "<error message>"
```
Explains WHY a command failed, not just what went wrong.

**Example:**
```bash
djinn why "permission denied"
```

---

## Project Management

### Project Architect
```bash
djinn architect list              # List templates
djinn architect stacks            # List quick stacks
djinn architect create <template> <name>
```

**Templates:**
- `fullstack-react-node` - React + Express
- `django-react` - Django + React
- `fastapi-vue` - FastAPI + Vue
- `microservices` - Multi-service architecture
- `monorepo-npm` - NPM workspaces
- `cli-python` - Python CLI tool

**Quick Stacks:**
```bash
djinn setup list                  # List stacks
djinn setup new node              # Node.js project
djinn setup new python            # Python project
djinn setup new fastapi           # FastAPI API
djinn setup new express           # Express.js API
```

### Workflow Automation
```bash
djinn flow templates              # Built-in templates
djinn flow create <name>          # Create workflow
djinn flow list                   # List workflows
djinn flow run <name>             # Execute workflow
djinn flow run <name> --dry-run   # Preview only
djinn flow delete <name>          # Delete workflow
```

**Built-in Templates:**
- `node-ci` - npm install → lint → test → build
- `python-ci` - pip install → ruff → pytest
- `docker-deploy` - build → tag → push
- `git-release` - pull → tag → push

---

## Environment & Configuration

### Env File Management
```bash
djinn env list                    # List variables (masks secrets)
djinn env get <KEY>               # Get variable value
djinn env set <KEY> <value>       # Set variable
djinn env delete <KEY>            # Remove variable
djinn env backup                  # Create backup
djinn env validate                # Check for issues
```

### Dotfiles Backup
```bash
djinn dotfiles backup             # Backup to ~/.djinn/dotfiles
djinn dotfiles restore            # Restore dotfiles
djinn dotfiles list               # List backed up files
djinn dotfiles export             # Export as tar.gz
```

### SSH Manager
```bash
djinn ssh list                    # List connections
djinn ssh add <alias> <host> <user>
djinn ssh connect <alias>         # Print connect command
djinn ssh keys                    # List SSH keys
```

---

## Productivity

### Learning & Shortcuts
```bash
djinn learn status                # View learning status
djinn learn shortcut              # List shortcuts
djinn learn shortcut add <name> "<prompt>"
djinn learn insights              # Usage insights
```

### Scheduling
```bash
djinn schedule add "<cmd>" <when>
djinn schedule list               # List pending
djinn schedule run                # Run due tasks
djinn schedule cancel <id>        # Cancel task
```

**Time formats:**
- `+30m` - 30 minutes from now
- `+1h` - 1 hour from now
- `+1d` - Tomorrow
- `2024-12-31T10:00:00` - Specific datetime

### Recording
```bash
djinn record start [name]         # Start recording
djinn record stop                 # Stop and save
djinn record list                 # List recordings
djinn record export <name>        # Export as shell script
djinn record delete <name>        # Delete recording
```

### Gist Sharing
```bash
djinn gist "<content>"            # Share as GitHub Gist
```
**Requires:** `GITHUB_TOKEN` environment variable.

---

## Fun & Learning

### Games
```bash
djinn game typing                 # Typing speed practice
djinn game quiz                   # CLI knowledge quiz
djinn game memory                 # Command memory game
```

### Text-to-Speech
```bash
djinn speak "<message>"
```
Speaks the message aloud using system TTS.

---

## Plugin System

Access 900+ command templates:

```bash
djinn plugin <category> <command>
```

**Categories:**
- `security` - Secrets, encryption, firewall, SSL
- `database` - MySQL, PostgreSQL, MongoDB, Redis
- `networking` - ping, dig, nmap, curl, wget
- `cloud` - AWS, GCP, Azure, DigitalOcean
- `sysadmin` - processes, services, disk, users
- `containers` - Docker, K8s, Helm, Podman
- `development` - Node, Python, Go, Rust, Java
- `git` - 100+ advanced Git commands
- `files` - find, grep, sed, awk, tar
- `api` - HTTP testing, gRPC, WebSocket
- `monitoring` - top, htop, sar, benchmarks
- `misc` - tmux, FFmpeg, yt-dlp, QR codes

---

## Configuration

```bash
djinn config show                 # Show current config
djinn config set <key> <value>    # Set config value
djinn config reset                # Reset to defaults
```

**Key settings:**
- `provider` - LLM provider (ollama, lmstudio, openai)
- `model` - Model name
- `temperature` - Generation temperature (0.0-1.0)
- `theme` - UI theme

---

## Model Management

```bash
djinn model list                  # List installed models
djinn model browse                # Browse available models
djinn model download <name>       # Download model
djinn model delete <name>         # Delete model
djinn model info <name>           # Get model info
djinn model recommend             # Get recommendations
```

---

## Themes

```bash
djinn theme list                  # List themes
djinn theme set <name>            # Set theme
```

**Available themes:** default, cyberpunk, retro, nord, dracula, solarized, monokai, light

---

## Cheatsheets

```bash
djinn cheat <tool>                # Show cheatsheet
djinn cheat <tool> search <term>  # Search cheatsheet
```

**Available:** git, docker, kubernetes, linux, npm, python, aws, postgres
