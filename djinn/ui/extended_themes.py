"""
Additional Themes for DJINN.
"""
from rich.theme import Theme as RichTheme


# Extended theme collection
EXTENDED_THEMES = {
    "cyberpunk": RichTheme({
        "highlight": "bold #ff00ff",
        "success": "#00ff00",
        "warning": "#ffff00",
        "error": "bold #ff0000",
        "command": "#00ffff",
        "prompt": "#ff00ff",
        "muted": "#666699",
        "info": "#9999ff",
    }),
    
    "retro": RichTheme({
        "highlight": "bold #ffa500",
        "success": "#00ff00",
        "warning": "#ffff00",
        "error": "bold #ff0000",
        "command": "#00ff00",
        "prompt": "#ffa500",
        "muted": "#808080",
        "info": "#ffff00",
    }),
    
    "nord": RichTheme({
        "highlight": "bold #88c0d0",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "bold #bf616a",
        "command": "#81a1c1",
        "prompt": "#88c0d0",
        "muted": "#4c566a",
        "info": "#b48ead",
    }),
    
    "dracula": RichTheme({
        "highlight": "bold #bd93f9",
        "success": "#50fa7b",
        "warning": "#f1fa8c",
        "error": "bold #ff5555",
        "command": "#8be9fd",
        "prompt": "#ff79c6",
        "muted": "#6272a4",
        "info": "#bd93f9",
    }),
    
    "solarized": RichTheme({
        "highlight": "bold #268bd2",
        "success": "#859900",
        "warning": "#b58900",
        "error": "bold #dc322f",
        "command": "#2aa198",
        "prompt": "#268bd2",
        "muted": "#586e75",
        "info": "#6c71c4",
    }),
    
    "light": RichTheme({
        "highlight": "bold #0066cc",
        "success": "#008800",
        "warning": "#cc6600",
        "error": "bold #cc0000",
        "command": "#006666",
        "prompt": "#0066cc",
        "muted": "#666666",
        "info": "#6600cc",
    }),
    
    "monokai": RichTheme({
        "highlight": "bold #f92672",
        "success": "#a6e22e",
        "warning": "#fd971f",
        "error": "bold #f92672",
        "command": "#66d9ef",
        "prompt": "#ae81ff",
        "muted": "#75715e",
        "info": "#e6db74",
    }),
}


def get_extended_theme(name: str):
    """Get an extended theme by name."""
    return EXTENDED_THEMES.get(name)


def list_extended_themes():
    """List all extended theme names."""
    return list(EXTENDED_THEMES.keys())
