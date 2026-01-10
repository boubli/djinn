"""
Djinn Spinner - Progress indicators with style.
"""
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.spinner import Spinner
from contextlib import contextmanager
from typing import Optional


class DjinnSpinner:
    """Stylish progress spinners for Djinn."""
    
    # Custom spinner frames with Moroccan feel
    FRAMES = ["◐", "◓", "◑", "◒"]
    MAGIC_FRAMES = ["✦", "✧", "★", "☆", "✦", "✧"]
    WAVE_FRAMES = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▂"]
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    @contextmanager
    def status(self, message: str = "Summoning the Djinn...", style: str = "#8B5CF6"):
        """Show a status spinner."""
        with self.console.status(
            f"[{style}]{message}[/{style}]",
            spinner="dots",
            spinner_style=style
        ) as status:
            yield status
    
    @contextmanager  
    def progress(self, description: str = "Processing"):
        """Show a progress bar."""
        with Progress(
            SpinnerColumn(style="#8B5CF6"),
            TextColumn("[#D4AF37]{task.description}[/#D4AF37]"),
            BarColumn(complete_style="#8B5CF6", finished_style="#22C55E"),
            console=self.console,
        ) as progress:
            yield progress
    
    def magic_text(self, text: str) -> str:
        """Add magic sparkle to text."""
        return f"✨ {text} ✨"
    
    def print_generating(self):
        """Print a generating message."""
        self.console.print("\n[#F59E0B]⚡ Summoning command...[/#F59E0B]\n")
    
    def print_success(self, command: str):
        """Print success message with the command."""
        self.console.print("[#22C55E]✓ Command generated:[/#22C55E]")
        self.console.print(f"  [bold #A855F7]{command}[/bold #A855F7]\n")
    
    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"[#EF4444]✗ {message}[/#EF4444]")
    
    def print_copied(self):
        """Print clipboard confirmation."""
        self.console.print("[#14B8A6]📋 Copied to clipboard![/#14B8A6]")
        self.console.print("[#6B7280]   Paste with Ctrl+V[/#6B7280]")
