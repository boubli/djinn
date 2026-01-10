"""
Animated Logo - Matrix-style effects.
"""
import time
import random
from rich.console import Console
from rich.text import Text
from rich.live import Live


class AnimatedLogo:
    """Animated logo with typing effect."""
    
    LOGO_LINES = [
        "    ╭──────────────────────────────────────────────────╮",
        "    │                                                  │",
        "    │     ___    _____  _____  _   _  _   _            │",
        "    │    /   \\  |_   _||_   _|| \\ | || \\ | |           │",
        "    │   / /\\ /    | |    | |  |  \\| ||  \\| |           │",
        "    │  / /_//     | |    | |  | |\\  || |\\  |           │",
        "    │ /___,'   |__| |  |___|  |_| \\_||_| \\_|           │",
        "    │                                                  │",
        "    │  ──────────────────────────────────────────────  │",
        "    │        Terminal Sorcery at Your Command          │",
        "    │  ──────────────────────────────────────────────  │",
        "    │                                                  │",
        "    ╰──────────────────────────────────────────────────╯",
    ]
    
    COLORS = ["#059669", "#10B981", "#22C55E", "#4ADE80", "#86EFAC"]
    
    @classmethod
    def typing_effect(cls, console: Console, speed: float = 0.02):
        """Display logo with typing effect."""
        for i, line in enumerate(cls.LOGO_LINES):
            color = cls.COLORS[i % len(cls.COLORS)]
            text = Text()
            console.print(line, style=color, end="")
            console.print()
            time.sleep(speed)
    
    @classmethod
    def matrix_effect(cls, console: Console, duration: float = 1.0):
        """Display logo with matrix-style reveal."""
        # Start with random characters
        chars = "░▒▓█▀▄■□▪▫"
        
        result = []
        for line in cls.LOGO_LINES:
            scrambled = ''.join(
                random.choice(chars) if c not in ' │╭╮╰╯─' else c 
                for c in line
            )
            result.append(scrambled)
        
        start_time = time.time()
        
        with Live(console=console, refresh_per_second=20) as live:
            while time.time() - start_time < duration:
                progress = (time.time() - start_time) / duration
                
                text = Text()
                for i, (original, current) in enumerate(zip(cls.LOGO_LINES, result)):
                    color = cls.COLORS[i % len(cls.COLORS)]
                    
                    # Gradually reveal original characters
                    new_line = ""
                    for j, (o, c) in enumerate(zip(original, current)):
                        if random.random() < progress or o in ' │╭╮╰╯─':
                            new_line += o
                        else:
                            new_line += random.choice(chars)
                    
                    result[i] = new_line
                    text.append(new_line + "\n", style=color)
                
                live.update(text)
        
        # Final reveal
        text = Text()
        for i, line in enumerate(cls.LOGO_LINES):
            color = cls.COLORS[i % len(cls.COLORS)]
            text.append(line + "\n", style=color)
        console.print(text)
    
    @classmethod
    def fade_in(cls, console: Console, steps: int = 5):
        """Display logo with fade-in effect."""
        shades = ["#1a1a1a", "#333333", "#4d4d4d", "#666666", "#808080"] + cls.COLORS
        
        for shade_idx in range(len(shades)):
            text = Text()
            for i, line in enumerate(cls.LOGO_LINES):
                # Use progressively brighter colors
                color_idx = min(shade_idx, len(cls.COLORS) - 1)
                color = shades[shade_idx] if shade_idx < 5 else cls.COLORS[i % len(cls.COLORS)]
                text.append(line + "\n", style=color)
            
            console.clear()
            console.print(text)
            time.sleep(0.1)
