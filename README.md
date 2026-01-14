# DJINN - Terminal Sorcery at Your Command 🧞‍♂️

<p align="center">
  <img src="assets/djinn_logo.png" width="300" alt="DJINN Logo">
</p>

[![PyPI Version](https://img.shields.io/pypi/v/djinn-cli.svg?color=blue)](https://pypi.org/project/djinn-cli/)
[![Python Versions](https://img.shields.io/pypi/pyversions/djinn-cli.svg)](https://pypi.org/project/djinn-cli/)
[![License](https://img.shields.io/github/license/boubli/djinn.svg)](LICENSE)

**DJINN** is an AI-powered CLI that converts natural language into precise shell commands. Stop memorizing flags; just ask.

```bash
djinn "find all files larger than 100MB and sort by size"
```

---

## ⚡ Key Features

- **Natural Language Parsing**: Uses LLMs (Ollama, OpenAI, LM Studio) to understand you.
- **Smart Execution**: `djinn -x` to run commands instantly.
- **Interactive Mode**: `djinn -i` for a chat-like experience.
- **180+ Built-in Commands**: Git, Docker, Network, Files, Security, and more.
- **Plugin Marketplace**: Download 30+ additional plugins.
- **Cross-Platform**: Windows, macOS, Linux.

---

## 🔌 Plugins System

### Built-in Plugins (Included)

DJINN comes with **100+ commands built-in**, covering:

| Category     | Commands                                        |
| ------------ | ----------------------------------------------- |
| **Git**      | `djinn git status`, `djinn git undo`            |
| **Docker**   | `djinn docker cleanup`, `djinn docker logs`     |
| **Network**  | `djinn ip`, `djinn ports`, `djinn ping`         |
| **Files**    | `djinn tree`, `djinn search`, `djinn qr`        |
| **Security** | `djinn pass`, `djinn audit`, `djinn hash`       |
| **System**   | `djinn sysinfo`, `djinn monitor`, `djinn clean` |

### 🛒 Plugin Marketplace (Download More)

Want more features? Install additional plugins from the marketplace:

```bash
# Browse available plugins
djinn market list

# Install a plugin
djinn market install spotify
djinn market install notion-cli
djinn market install kubernetes

# View installed plugins
djinn plugins installed

# Remove a plugin
djinn plugins remove spotify
```

### 📦 30+ Marketplace Plugins Available

| Category         | Plugins                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------- |
| **AI & ML**      | `ollama-manager`, `openai-chat`, `huggingface`                                            |
| **Cloud**        | `vercel-deploy`, `firebase`, `netlify`, `aws-toolkit`, `cloudflare`, `supabase`, `stripe` |
| **DevOps**       | `kubernetes`, `terraform`, `system-monitor`                                               |
| **Databases**    | `database-cli`, `redis-cli`, `elasticsearch`                                              |
| **Development**  | `api-tester`, `github-toolkit`, `webhook-tester`, `data-converter`, `data-faker`          |
| **Productivity** | `notion-cli`, `slack-cli`, `todoist`, `linear`, `jira`, `pomodoro`, `screenshot`          |
| **Security**     | `password-manager` (1Password/Bitwarden)                                                  |
| **Media**        | `spotify`, `youtube-dl`                                                                   |

See all plugins: [marketplace/README.md](marketplace/README.md)

---

## 📚 Documentation

Everything you need to know about using DJINN:

- **[Installation Guide](docs/installation.md)**: Install via Pip, Script, Homebrew, or Docker.
- **[Command Reference](docs/commands.md)**: Master the CLI, from aliases to configuration.
- **[Plugins & Subcommands](docs/plugins.md)**: Learn about the plugin system.
- **[Marketplace](marketplace/README.md)**: Browse and create plugins.

---

## 🚀 Quick Start

```bash
# Install DJINN
pip install djinn-cli

# Run setup wizard (first time)
djinn setup

# Use natural language
djinn "list all docker containers"

# Or use direct commands
djinn git status
djinn docker cleanup
djinn sysinfo

# Install more plugins
djinn market install spotify
djinn spotify now
```

---

## 🤝 Contributing

We love contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Creating Plugins

Want to create your own plugin?

```bash
# Generate plugin template
djinn plugins create my-awesome-plugin
```

See [marketplace/README.md](marketplace/README.md) for plugin development guide.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
