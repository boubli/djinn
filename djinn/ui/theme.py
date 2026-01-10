"""
Djinn Theme - Moroccan-inspired color scheme.
"""
from rich.theme import Theme as RichTheme
from rich.style import Style


class Theme:
    """Moroccan-inspired color theme for Djinn."""
    
    # Moroccan color palette
    COLORS = {
        "purple": "#8B5CF6",
        "purple_light": "#A855F7",
        "gold": "#D4AF37",
        "amber": "#F59E0B",
        "teal": "#14B8A6",
        "cyan": "#06B6D4",
        "red": "#EF4444",
        "green": "#22C55E",
        "gray": "#6B7280",
        "dark": "#1F2937",
    }
    
    # Rich theme definition
    RICH_THEME = RichTheme({
        "info": Style(color="#06B6D4"),
        "warning": Style(color="#F59E0B"),
        "error": Style(color="#EF4444", bold=True),
        "success": Style(color="#22C55E", bold=True),
        "command": Style(color="#A855F7", bold=True),
        "prompt": Style(color="#D4AF37"),
        "muted": Style(color="#6B7280"),
        "highlight": Style(color="#8B5CF6", bold=True),
        "arabic": Style(color="#D4AF37"),
    })
    
    @staticmethod
    def get_theme() -> RichTheme:
        """Get the Rich theme."""
        return Theme.RICH_THEME
    
    @staticmethod
    def style(name: str) -> str:
        """Get a color by name."""
        return Theme.COLORS.get(name, "#FFFFFF")
    
    @staticmethod
    def gradient(text: str, start_color: str = "purple", end_color: str = "cyan") -> str:
        """Apply a gradient effect (for Rich markup)."""
        # Simple implementation - alternates colors
        start = Theme.COLORS.get(start_color, "#8B5CF6")
        end = Theme.COLORS.get(end_color, "#06B6D4")
        return f"[{start}]{text}[/{start}]"
