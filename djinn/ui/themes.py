"""
Themes - Color schemes for Djinn CLI.
"""
from rich.theme import Theme as RichTheme
from rich.style import Style
from typing import Dict


class ThemeManager:
    """Manages color themes for Djinn."""
    
    THEMES = {
        "default": {
            "primary": "#22C55E",      # Green
            "secondary": "#10B981",
            "accent": "#4ADE80",
            "muted": "#6B7280",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "success": "#22C55E",
            "info": "#06B6D4",
        },
        "hacker": {
            "primary": "#00FF00",      # Matrix green
            "secondary": "#00CC00",
            "accent": "#00FF00",
            "muted": "#005500",
            "error": "#FF0000",
            "warning": "#FFFF00",
            "success": "#00FF00",
            "info": "#00FFFF",
        },
        "ocean": {
            "primary": "#0EA5E9",      # Blue
            "secondary": "#06B6D4",
            "accent": "#38BDF8",
            "muted": "#64748B",
            "error": "#F43F5E",
            "warning": "#FB923C",
            "success": "#10B981",
            "info": "#0EA5E9",
        },
        "purple": {
            "primary": "#8B5CF6",      # Purple
            "secondary": "#A855F7",
            "accent": "#C084FC",
            "muted": "#6B7280",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "success": "#22C55E",
            "info": "#06B6D4",
        },
        "minimal": {
            "primary": "#FFFFFF",      # White
            "secondary": "#E5E5E5",
            "accent": "#FFFFFF",
            "muted": "#737373",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "success": "#22C55E",
            "info": "#FFFFFF",
        },
        # New extended themes
        "cyberpunk": {
            "primary": "#ff00ff",
            "secondary": "#00ffff",
            "accent": "#ff00ff",
            "muted": "#666699",
            "error": "#ff0000",
            "warning": "#ffff00",
            "success": "#00ff00",
            "info": "#9999ff",
        },
        "retro": {
            "primary": "#ffa500",
            "secondary": "#00ff00",
            "accent": "#ffa500",
            "muted": "#808080",
            "error": "#ff0000",
            "warning": "#ffff00",
            "success": "#00ff00",
            "info": "#ffff00",
        },
        "nord": {
            "primary": "#88c0d0",
            "secondary": "#81a1c1",
            "accent": "#88c0d0",
            "muted": "#4c566a",
            "error": "#bf616a",
            "warning": "#ebcb8b",
            "success": "#a3be8c",
            "info": "#b48ead",
        },
        "dracula": {
            "primary": "#bd93f9",
            "secondary": "#ff79c6",
            "accent": "#bd93f9",
            "muted": "#6272a4",
            "error": "#ff5555",
            "warning": "#f1fa8c",
            "success": "#50fa7b",
            "info": "#8be9fd",
        },
        "solarized": {
            "primary": "#268bd2",
            "secondary": "#2aa198",
            "accent": "#268bd2",
            "muted": "#586e75",
            "error": "#dc322f",
            "warning": "#b58900",
            "success": "#859900",
            "info": "#6c71c4",
        },
        "light": {
            "primary": "#0066cc",
            "secondary": "#006666",
            "accent": "#0066cc",
            "muted": "#666666",
            "error": "#cc0000",
            "warning": "#cc6600",
            "success": "#008800",
            "info": "#6600cc",
        },
        "monokai": {
            "primary": "#f92672",
            "secondary": "#66d9ef",
            "accent": "#ae81ff",
            "muted": "#75715e",
            "error": "#f92672",
            "warning": "#fd971f",
            "success": "#a6e22e",
            "info": "#e6db74",
        },
    }
    
    def __init__(self, theme_name: str = "default"):
        self.theme_name = theme_name if theme_name in self.THEMES else "default"
        self.colors = self.THEMES[self.theme_name]
    
    def get_rich_theme(self) -> RichTheme:
        """Get Rich theme for console."""
        return RichTheme({
            "info": Style(color=self.colors["info"]),
            "warning": Style(color=self.colors["warning"]),
            "error": Style(color=self.colors["error"], bold=True),
            "success": Style(color=self.colors["success"], bold=True),
            "command": Style(color=self.colors["primary"], bold=True),
            "prompt": Style(color=self.colors["accent"]),
            "muted": Style(color=self.colors["muted"]),
            "highlight": Style(color=self.colors["primary"], bold=True),
        })
    
    def color(self, name: str) -> str:
        """Get a color by name."""
        return self.colors.get(name, "#FFFFFF")
    
    @classmethod
    def list_themes(cls) -> list:
        """List available theme names."""
        return list(cls.THEMES.keys())

