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
