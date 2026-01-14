# DJINN Marketplace Plugins

**30+ Plugins** to extend DJINN CLI with additional features.

## 📦 Available Plugins

### 🤖 AI & Machine Learning

| Plugin           | Description                      | Dependencies    |
| ---------------- | -------------------------------- | --------------- |
| `ollama-manager` | Manage local Ollama LLM models   | requests        |
| `openai-chat`    | Direct GPT-4/ChatGPT access      | openai          |
| `huggingface`    | HuggingFace Hub model management | huggingface_hub |

### 🛠️ DevOps

| Plugin           | Description                        | Dependencies |
| ---------------- | ---------------------------------- | ------------ |
| `kubernetes`     | Enhanced kubectl wrapper           | -            |
| `terraform`      | Infrastructure as code management  | -            |
| `system-monitor` | CPU, RAM, Disk, Network monitoring | psutil       |

### ☁️ Cloud Platforms

| Plugin          | Description                  | Dependencies |
| --------------- | ---------------------------- | ------------ |
| `vercel-deploy` | Deploy to Vercel             | -            |
| `firebase`      | Firebase hosting & Firestore | -            |
| `netlify`       | Netlify deployment           | -            |
| `cloudflare`    | DNS, Workers, Pages          | requests     |
| `aws-toolkit`   | S3, EC2, Lambda shortcuts    | boto3        |
| `supabase`      | Database, auth, storage      | supabase     |
| `stripe`        | Payments & billing           | stripe       |

### 💻 Development Tools

| Plugin           | Description                | Dependencies |
| ---------------- | -------------------------- | ------------ |
| `api-tester`     | Postman-like HTTP client   | requests     |
| `github-toolkit` | PRs, releases, actions     | PyGithub     |
| `webhook-tester` | Webhook testing & mocking  | requests     |
| `data-converter` | JSON/YAML/TOML/CSV convert | pyyaml, toml |
| `data-faker`     | Generate fake test data    | -            |

### 📊 Databases

| Plugin          | Description                        | Dependencies              |
| --------------- | ---------------------------------- | ------------------------- |
| `database-cli`  | PostgreSQL, MySQL, SQLite, MongoDB | psycopg2, mysql-connector |
| `redis-cli`     | Redis client                       | redis                     |
| `elasticsearch` | ES cluster management              | elasticsearch             |

### ⚡ Productivity

| Plugin       | Description                 | Dependencies       |
| ------------ | --------------------------- | ------------------ |
| `notion-cli` | Notion workspace management | notion-client      |
| `slack-cli`  | Slack messaging             | slack_sdk          |
| `todoist`    | Task management             | todoist-api-python |
| `linear`     | Linear issue tracking       | requests           |
| `jira`       | Jira issue tracking         | requests           |
| `pomodoro`   | Focus timer                 | -                  |
| `screenshot` | Screen capture & OCR        | pillow, pyautogui  |

### 🔒 Security

| Plugin             | Description           | Dependencies |
| ------------------ | --------------------- | ------------ |
| `password-manager` | 1Password & Bitwarden | pyperclip    |

### 🎬 Media

| Plugin       | Description              | Dependencies |
| ------------ | ------------------------ | ------------ |
| `spotify`    | Control Spotify playback | spotipy      |
| `youtube-dl` | Video downloader         | yt-dlp       |

---

## 🔌 Installing Plugins

```bash
# List all available plugins
djinn market list

# Install a plugin
djinn market install ollama-manager

# View installed plugins
djinn plugins installed
```

## 🛠️ Creating Your Own Plugin

### Plugin Structure

```
marketplace/
└── my-plugin/
    ├── plugin.py       # Main plugin file
    └── README.md       # Documentation
```

### Minimal Template

```python
"""My Plugin for DJINN"""
import click
from rich.console import Console

console = Console()

PLUGIN_NAME = "my-plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "Your Name"
PLUGIN_DESCRIPTION = "What this plugin does"

@click.group()
def myplugin():
    """My plugin commands."""
    pass

@myplugin.command(name="hello")
@click.argument("name")
def hello(name):
    """Say hello."""
    console.print(f"[success]Hello, {name}![/success]")

main = myplugin

if __name__ == "__main__":
    myplugin()
```

## 📝 Contributing

1. Fork this repository
2. Create `marketplace/your-plugin/plugin.py`
3. Add entry to `registry.json`
4. Submit a Pull Request

### Requirements

- [ ] Plugin has `plugin.py`
- [ ] Works with DJINN >= 2.2.0
- [ ] No malicious code
- [ ] Documented with examples

## 📜 License

All plugins are MIT licensed unless otherwise specified.
