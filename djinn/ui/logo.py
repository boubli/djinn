"""
Djinn Logo - 3D style with green/white colors.
"""
from rich.console import Console
from rich.text import Text
from rich.panel import Panel


class Logo:
    """Djinn logo - 3D style with green/white."""
    
    # 3D style logo
    STYLED_LOGO = r"""
    ╭──────────────────────────────────────────────────╮
    │                                                  │
    │     ___    _____  _____  _   _  _   _            │
    │    /   \  |_   _||_   _|| \ | || \ | |           │
    │   / /\ /    | |    | |  |  \| ||  \| |           │
    │  / /_//     | |    | |  | |\  || |\  |           │
    │ /___,'   |__| |  |___|  |_| \_||_| \_|           │
    │                                                  │
    │  ──────────────────────────────────────────────  │
    │        Terminal Sorcery at Your Command          │
    │  ──────────────────────────────────────────────  │
    │                                                  │
    ╰──────────────────────────────────────────────────╯
"""

    # Ultra minimal
    MICRO_LOGO = "[bold #22C55E]DJINN[/bold #22C55E] [#FFFFFF]• Terminal Sorcery[/#FFFFFF]"

    CREDITS = "\n  [#6B7280]by Youssef Boubli • boubli.tech[/#6B7280]\n"

    @staticmethod
    def get_colored_logo(console: Console = None) -> Text:
        """Get the logo with green/white colors."""
        if console is None:
            console = Console()
        
        text = Text()
        lines = Logo.STYLED_LOGO.split("\n")
        
        # Green/white gradient
        colors = [
            "#059669",  # Dark green
            "#10B981",  # Green
            "#22C55E",  # Bright green
            "#4ADE80",  # Light green
            "#86EFAC",  # Lighter green
            "#FFFFFF",  # White
            "#86EFAC",  # Lighter green
            "#4ADE80",  # Light green
            "#22C55E",  # Bright green
            "#10B981",  # Green
            "#059669",  # Dark green
            "#10B981",  # Green
            "#22C55E",  # Bright green
        ]
        
        for i, line in enumerate(lines):
            if not line:
                text.append("\n")
                continue
            color = colors[i % len(colors)]
            text.append(line + "\n", style=color)
        
        return text
    
    @staticmethod
    def print_logo(console: Console = None, mini: bool = False):
        """Print the logo to console."""
        if console is None:
            console = Console()
        
        if mini:
            console.print(Logo.MICRO_LOGO)
        else:
            console.print(Logo.get_colored_logo(console))
    
    @staticmethod
    def print_credits(console: Console = None):
        """Print developer credits."""
        if console is None:
            console = Console()
        console.print(Logo.CREDITS)
    
    @staticmethod
    def get_welcome_panel() -> Panel:
        """Get a welcome panel with the logo."""
        return Panel(
            Logo.get_colored_logo(),
            border_style="#22C55E",
            padding=(0, 2),
        )
