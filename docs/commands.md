# Command Reference

## 🪄 Core Commands

| Command | Description | Example |
| :--- | :--- | :--- |
| `djinn <prompt>` | **Summom (Default)**: Converts English to Shell. | `djinn "list all pdfs"` |
| `djinn -i` | **Interactive Mode**: Chat-like interface. | `djinn -i` |
| `djinn -x <prompt>` | **Execute**: Run immediately without asking. | `djinn -x "git pull"` |
| `djinn --help` | Show help menu. | `djinn --help` |
| `djinn --version` | Show current version. | `djinn --version` |

## ⚙️ Configuration

| Command | Description |
| :--- | :--- |
| `djinn config --show` | Display current settings (Backend, Model, Theme). |
| `djinn config --backend <name>` | Set LLM (ollama, lmstudio, openai). |
| `djinn config --model <name>` | Set Model (llama3.2, gpt-4o, etc.). |

## 🔖 Aliases

Save your favorite prompts for later.

| Command | Description |
| :--- | :--- |
| `djinn alias add <name> <prompt>` | Create an alias. |
| `djinn alias list` | Show all aliases. |
| `djinn alias remove <name>` | Delete an alias. |
| `djinn @<name>` | Run an alias. |

**Example:**
```bash
djinn alias add deploy "git push origin master && git push heroku master"
djinn @deploy
```

## 🔌 Subcommands (Plugins)

DJINN comes with specialized built-in plugins:

### version-control
`djinn git "<prompt>"` overrides the model to focus purely on git commands.

### docker-ops
`djinn docker "<prompt>"` specialized prompts for container management.

### theme-manager
`djinn theme list` / `djinn theme set <name>` to change CLI colors.
