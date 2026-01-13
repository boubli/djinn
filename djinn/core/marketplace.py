import os
import json
import requests
import click
from rich.console import Console
from rich.table import Table
from pathlib import Path

console = Console()
REGISTRY_URL = "https://raw.githubusercontent.com/boubli/djinn/master/registry.json"
PLUGIN_DIR = Path.home() / ".djinn" / "plugins"

class Marketplace:
    def __init__(self):
        self.plugin_dir = PLUGIN_DIR
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

    def fetch_registry(self):
        """Fetch the latest plugin registry from GitHub."""
        try:
            response = requests.get(REGISTRY_URL, timeout=5)
            response.raise_for_status()
            return response.json().get("plugins", {})
        except Exception as e:
            console.print(f"[bold red]Error fetching registry:[/bold red] {e}")
            return {}

    def list_plugins(self):
        """List all available plugins."""
        plugins = self.fetch_registry()
        if not plugins:
            return

        table = Table(title="🧞 DJINN Marketplace")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Author", style="green")
        table.add_column("Description")

        for name, data in plugins.items():
            table.add_row(name, data.get("version"), data.get("author"), data.get("description"))

        console.print(table)
        console.print("\nInstall a plugin with: [bold]djinn market install <name>[/bold]")

    def install_plugin(self, name):
        """Download and install a plugin."""
        plugins = self.fetch_registry()
        if name not in plugins:
            console.print(f"[bold red]Plugin '{name}' not found.[/bold red]")
            return

        plugin_data = plugins[name]
        url = plugin_data["url"]
        
        try:
            console.print(f"Downloading [cyan]{name}[/cyan]...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Save to plugin directory
            # We assume single file plugins for MVP
            filename = f"{name}.py"
            file_path = self.plugin_dir / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            console.print(f"[bold green]Successfully installed {name}![/bold green]")
            console.print(f"Plugin saved to: {file_path}")
            console.print("[dim](Restart current shell if not immediately visible)[/dim]")
            
        except Exception as e:
            console.print(f"[bold red]Installation failed:[/bold red] {e}")

