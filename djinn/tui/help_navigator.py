"""
Interactive Help Navigator using Rich.
Allows users to explore commands by category with keyboard navigation.
"""
import sys
import click
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.align import Align
from djinn.ui.theme import Theme

console = Console()

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
        self.running = True

    def run(self):
        """Start the interactive loop."""
        with Live(self.make_layout(), refresh_per_second=10, screen=True) as live:
            while self.running:
                live.update(self.make_layout())
                char = click.getchar()
                self.handle_input(char)

    def handle_input(self, char):
        """Handle keyboard input."""
        if char in ('q', 'Q', '\x03'):  # q or Ctrl+C
            self.running = False
            return
        
        # Navigation
        if char == '\r':  # Enter
            if self.active_pane == "categories":
                self.active_pane = "commands"
                self.selected_command_idx = 0
            else:
                # Execute/Show help for command?
                # For now just toggle back
                pass
        
        elif char == '\x1b':  # Escape sequence
            # Handle arrow keys (simplified for standard ANSI)
            # This is a bit tricky with click.getchar() as it returns chars one by one
            # Usually users use libraries like `readchar` or `cureses` for this.
            # But for simplicity, we assume generic arrow handling or use prompt_toolkit if available.
            pass
        
        # Simple mapping for Windows/VSCode terminal often sends special codes
        # We'll use a simpler approach: 
        # w/s for up/down in categories
        # a/d for switch panes?
        # Actually, let's use prompt_toolkit given it's a dependency.
        pass

# Redefine run using prompt_toolkit for better key handling
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout as PTLayout
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import HTML

class PromptToolkitNavigator:
    def __init__(self):
        self.categories = list(HelpNavigator.CATEGORIES.keys())
        self.cat_idx = 0
        self.cmd_idx = 0
        self.focus = "categories" # categories, commands

    def get_layout(self):
        # We will render the Rich layout to a string (or use PT widgets)
        # Using Rich inside PT is complex.
        # Let's stick to pure Rich with a loop, but handle keys better.
        pass

# Back to Rich + Click.getchar() specific handling
def get_key():
    first_char = click.getchar()
    if first_char == '\xe0': # Windows arrow prefix
        second_char = click.getchar()
        if second_char == 'H': return 'up'
        if second_char == 'P': return 'down'
        if second_char == 'K': return 'left'
        if second_char == 'M': return 'right'
    if first_char == '\x1b': # Unix arrow prefix
        second_char = click.getchar()
        if second_char == '[':
            third_char = click.getchar()
            if third_char == 'A': return 'up'
            if third_char == 'B': return 'down'
            if third_char == 'C': return 'right'
            if third_char == 'D': return 'left'
    return first_char

class RichHelpNavigator(HelpNavigator):
    def run(self):
        with Live(self.make_layout(), refresh_per_second=20, screen=True) as live:
            while self.running:
                live.update(self.make_layout())
                key = get_key()
                
                if key in ('q', 'Q', '\x03'):
                    self.running = False
                elif key == 'up':
                    if self.active_pane == "categories":
                        self.selected_category_idx = (self.selected_category_idx - 1) % len(self.categories)
                    else:
                        cat_name = self.categories[self.selected_category_idx]
                        cmds = self.CATEGORIES[cat_name]
                        self.selected_command_idx = (self.selected_command_idx - 1) % len(cmds)
                elif key == 'down':
                    if self.active_pane == "categories":
                        self.selected_category_idx = (self.selected_category_idx + 1) % len(self.categories)
                    else:
                        cat_name = self.categories[self.selected_category_idx]
                        cmds = self.CATEGORIES[cat_name]
                        self.selected_command_idx = (self.selected_command_idx + 1) % len(cmds)
                elif key in ('right', '\r', ' '):
                    if self.active_pane == "categories":
                        self.active_pane = "commands"
                        self.selected_command_idx = 0
                elif key in ('left', '\x1b'): # Esc or Left
                    if self.active_pane == "commands":
                        self.active_pane = "categories"
    
    def make_layout(self):
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="categories", ratio=1),
            Layout(name="commands", ratio=2)
        )
        
        # Header
        layout["header"].update(
            Panel(Align.center("[bold magenta]🧞 DJINN Interactive Help[/bold magenta]"), style="magenta")
        )
        
        # Categories List
        cat_text = Text()
        for idx, cat in enumerate(self.categories):
            style = "bold green reverse" if idx == self.selected_category_idx and self.active_pane == "categories" else "white"
            if idx == self.selected_category_idx and self.active_pane == "commands":
                style = "bold green" # Highlight selected parent even if focus is child
            
            prefix = "➤ " if idx == self.selected_category_idx else "  "
            cat_text.append(f"{prefix}{cat}\n", style=style)
            
        layout["categories"].update(
            Panel(cat_text, title="Categories", border_style="green" if self.active_pane == "categories" else "dim")
        )
        
        # Commands List
        current_cat = self.categories[self.selected_category_idx]
        commands = self.CATEGORIES[current_cat]
        
        cmd_text = Text()
        for idx, (cmd, desc) in enumerate(commands):
            style = "bold cyan reverse" if idx == self.selected_command_idx and self.active_pane == "commands" else "white"
            prefix = "➤ " if idx == self.selected_command_idx and self.active_pane == "commands" else "  "
            
            cmd_text.append(f"{prefix}{cmd:<15} ", style=style)
            cmd_text.append(f"{desc}\n", style="dim" if style == "white" else "black on cyan")
            
        layout["commands"].update(
            Panel(cmd_text, title=f"Commands: {current_cat}", border_style="cyan" if self.active_pane == "commands" else "dim")
        )
        
        # Footer
        layout["footer"].update(
            Panel(Align.center("Navigate: [bold]↑ ↓ ← →[/bold] | Select: [bold]Enter[/bold] | Quit: [bold]q[/bold]"), style="dim")
        )
        
        return layout

def launch_help():
    """Launch the interactive help navigator."""
    navigator = RichHelpNavigator()
    try:
        navigator.run()
    except Exception as e:
        console.print(f"[red]Error starting interactive help: {e}[/red]")
