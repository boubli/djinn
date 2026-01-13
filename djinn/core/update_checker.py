import requests
import click
from packaging import version
from djinn import __version__
from rich.console import Console

console = Console()

def check_for_updates():
    """Check PyPI for a newer version of djinn-cli."""
    try:
        response = requests.get("https://pypi.org/pypi/djinn-cli/json", timeout=1)
        if response.status_code == 200:
            data = response.json()
            latest_version = data["info"]["version"]
            
            if version.parse(latest_version) > version.parse(__version__):
                console.print(f"\n[bold yellow]✨ Update Available: {latest_version}[/bold yellow] (Current: {__version__})")
                console.print(f"Run [bold cyan]pip install --upgrade djinn-cli[/bold cyan] to update.\n")
    except:
        # Fail silently if offline or PyPI is down
        pass
