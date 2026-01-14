"""
Interactive Help Navigator using Prompt Toolkit.
Allows users to explore commands by category with robust keyboard navigation.
"""
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

class HelpNavigator:
    """Interactive help menu with categories and navigation."""
    
    CATEGORIES = {
        "🤖 AI & Intelligence": [
            ("summon", "Generate shell commands from natural language"),
            ("chat", "Interactive codebase-aware chat"),
            ("explain", "Explain what a command does"),
            ("wtf", "Explain the last error (Context-Aware Help)"),
            ("predict", "Predict next likely command"),
            ("voice", "Start voice interaction mode"),
            ("persona", "Change AI persona/tone"),
        ],
        "🛠 DevOps & Cloud": [
            ("docker", "Docker command generator"),
            ("k8s", "Kubernetes pod management"),
            ("aws", "AWS CLI command generator"),
            ("azure", "Azure CLI command generator"),
            ("terraform", "Terraform command generator"),
            ("compose", "Generate docker-compose.yml"),
            ("helm", "Helm chart command generator"),
        ],
        "💻 Development": [
            ("git", "Git command generator"),
            ("python", "Python development commands"),
            ("node", "Node.js/NPM commands"),
            ("rust", "Rust/Cargo commands"),
            ("go", "Go development commands"),
            ("lint", "Linting command generator"),
            ("review", "Generate Pull Request review"),
            ("codegen", "Generate code snippets"),
            ("regex", "Explain regular expressions"),
        ],
        "🌐 Network & Web": [
            ("http", "Interactive HTTP client"),
            ("api", "Generate API/curl commands"),
            ("network", "Network diagnostics"),
            ("tunnel", "Create public tunnel to local port"),
            ("ip", "Show public IP and geolocation"),
            ("scrape", "Web scraping command generator"),
            ("serve", "Start HTTP server for current dir"),
        ],
        "📂 Files & System": [
            ("find", "Semantic file search"),
            ("tree", "File tree navigator"),
            ("disk", "Disk management"),
            ("process", "Process management"),
            ("ps", "Interactive process killer"),
            ("archive", "Archive/compression commands"),
            ("clipboard", "Manage clipboard history"),
        ],
        "🔐 Security": [
            ("audit", "Audit dependencies"),
            ("encrypt", "Encrypt a file with AES"),
            ("secrets", "Scan for secrets in code"),
            ("passgen", "Generate secure password"),
            ("ssh", "SSH connection manager"),
            ("firewall", "Firewall (ufw/iptables) commands"),
        ],
        "⚡ Productivity": [
            ("pomodoro", "Start Pomodoro timer"),
            ("todo", "Generate TODO comments"),
            ("stats", "Show productivity statistics"),
            ("history", "View command history"),
            ("weather", "Get ASCII weather report"),
            ("news", "Get top HackerNews stories"),
        ],
        "🎮 Fun": [
            ("game", "Play terminal games"),
            ("pet", "Virtual terminal pet"),
            ("matrix", "Matrix-style screensaver"),
            ("ascii", "Generate ASCII art"),
            ("fortune", "Get developer fortune"),
        ],
        "⚙ DJINN": [
            ("config", "Configure Djinn settings"),
            ("market", "Plugin Marketplace"),
            ("update", "Check for updates"),
            ("theme", "Change color theme"),
            ("docs", "Auto-generate documentation"),
        ]
    }

    def __init__(self):
        self.categories = list(self.CATEGORIES.keys())
        self.selected_category_idx = 0
        self.selected_command_idx = 0
        self.active_pane = "categories"  # 'categories' or 'commands'
        
        self.kb = KeyBindings()
        self.setup_keybindings()

    def setup_keybindings(self):
        @self.kb.add('q')
        @self.kb.add('c-c')
        def _(event):
            event.app.exit()

        @self.kb.add('up')
        def _(event):
            if self.active_pane == "categories":
                self.selected_category_idx = (self.selected_category_idx - 1) % len(self.categories)
            else:
                cat_name = self.categories[self.selected_category_idx]
                cmds = self.CATEGORIES[cat_name]
                self.selected_command_idx = (self.selected_command_idx - 1) % len(cmds)

        @self.kb.add('down')
        def _(event):
            if self.active_pane == "categories":
                self.selected_category_idx = (self.selected_category_idx + 1) % len(self.categories)
            else:
                cat_name = self.categories[self.selected_category_idx]
                cmds = self.CATEGORIES[cat_name]
                self.selected_command_idx = (self.selected_command_idx + 1) % len(cmds)

        @self.kb.add('right')
        @self.kb.add('enter')
        @self.kb.add('tab')
        def _(event):
            if self.active_pane == "categories":
                self.active_pane = "commands"
                self.selected_command_idx = 0

        @self.kb.add('left')
        @self.kb.add('escape')
        def _(event):
            if self.active_pane == "commands":
                self.active_pane = "categories"

    def get_categories_text(self):
        result = []
        for idx, cat in enumerate(self.categories):
            if idx == self.selected_category_idx:
                style = "class:selected" if self.active_pane == "categories" else "class:active-parent"
                prefix = "➤ "
            else:
                style = ""
                prefix = "  "
            
            result.append((style, f"{prefix}{cat}\n"))
        return result

    def get_commands_text(self):
        current_cat = self.categories[self.selected_category_idx]
        commands = self.CATEGORIES[current_cat]
        
        result = []
        for idx, (cmd, desc) in enumerate(commands):
            if idx == self.selected_command_idx and self.active_pane == "commands":
                style = "class:selected"
                prefix = "➤ "
            else:
                style = ""
                prefix = "  "
                
            # Pad command for alignment
            result.append((style, f"{prefix}{cmd:<15} "))
            result.append((style + " class:description", f"{desc}\n"))
        return result

    def run(self):
        root_container = HSplit([
            # Header
            Frame(
                Window(FormattedTextControl(HTML("<b>🧞 DJINN Interactive Help</b>")), align=WindowAlign.CENTER, height=1),
                style="class:header"
            ),
            # Body
            VSplit([
                # Categories Column
                Frame(
                    Window(FormattedTextControl(self.get_categories_text)),
                    title="Categories",
                    style="class:pane"
                ),
                # Commands Column
                Frame(
                    Window(FormattedTextControl(self.get_commands_text)),
                    title=lambda: f"Commands: {self.categories[self.selected_category_idx]}",
                    style="class:pane"
                )
            ]),
            # Footer
            Frame(
                Window(FormattedTextControl(HTML("Navigate: <b>↑ ↓ ← →</b> | Select: <b>Enter</b> | Quit: <b>q</b>")), align=WindowAlign.CENTER, height=1),
                style="class:footer"
            )
        ])

        style = Style.from_dict({
            "header": "bg:#8800ff #ffffff bold",
            "footer": "#888888",
            "selected": "reverse",
            "active-parent": "bold underline",
            "description": "#aaaaaa italic",
            "pane": "border:#00aa00"
        })

        app = Application(
            layout=Layout(root_container),
            key_bindings=self.kb,
            style=style,
            full_screen=True,
            mouse_support=True
        )
        app.run()

def launch_help():
    """Launch the interactive help navigator."""
    navigator = HelpNavigator()
    try:
        navigator.run()
    except Exception as e:
        print(f"Error starting interactive help: {e}")
