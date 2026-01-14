"""
Additional TUI and Fun Features for DJINN v2.2.0
"""
from textual.app import App
from textual.widgets import Static, Label
from textual.containers import Container
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
import time
import random
from pathlib import Path


class MarkdownPreview(App):
    """Live markdown preview in terminal."""
    
    CSS = """
    #preview {
        height: 100%;
        overflow-y: scroll;
    }
    """
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def compose(self):
        yield Static(id="preview")
    
    def on_mount(self):
        self.load_markdown()
    
    def load_markdown(self):
        """Load and render markdown file."""
        try:
            with open(self.file_path) as f:
                content = f.read()
            
            md = Markdown(content)
            self.query_one("#preview", Static).update(md)
        except Exception as e:
            self.query_one("#preview", Static).update(f"Error: {e}")


class HexEditor(App):
    """Simple hex file viewer."""
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def compose(self):
        yield Static(id="hex-view")
    
    def on_mount(self):
        self.load_hex()
    
    def load_hex(self):
        """Load file as hex."""
        try:
            with open(self.file_path, 'rb') as f:
                data = f.read(1024)  # First 1KB
            
            # Format as hex
            hex_lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_part = ' '.join(f'{b:02x}' for b in chunk)
                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                hex_lines.append(f"{i:04x}  {hex_part:<48}  {ascii_part}")
            
            self.query_one("#hex-view", Static).update('\n'.join(hex_lines))
        except Exception as e:
            self.query_one("#hex-view", Static).update(f"Error: {e}")


class GitGraphTUI(App):
    """Visual git commit graph."""
    
    def compose(self):
        yield Static(id="git-graph")
    
    def on_mount(self):
        self.load_git_graph()
    
    def load_git_graph(self):
        """Load git commit graph."""
        import subprocess
        
        try:
            result = subprocess.run(
                ["git", "log", "--graph", "--oneline", "--all", "-20"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.query_one("#git-graph", Static).update(result.stdout)
            else:
                self.query_one("#git-graph", Static).update("Not a git repository")
        except:
            self.query_one("#git-graph", Static).update("Git not found")


class ASCIIArtGenerator:
    """Generate ASCII art from images."""
    
    ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
    
    @staticmethod
    def image_to_ascii(image_path: str, width: int = 100) -> str:
        """Convert image to ASCII art."""
        try:
            from PIL import Image
            
            img = Image.open(image_path)
            
            # Calculate height to maintain aspect ratio
            aspect_ratio = img.height / img.width
            height = int(width * aspect_ratio * 0.55)  # 0.55 to account for character aspect ratio
            
            # Resize image
            img = img.resize((width, height))
            
            # Convert to grayscale
            img = img.convert('L')
            
            # Convert pixels to ASCII
            pixels = img.getdata()
            ascii_str = ''
            
            for i, pixel in enumerate(pixels):
                ascii_str += ASCIIArtGenerator.ASCII_CHARS[pixel // 25]
                if (i + 1) % width == 0:
                    ascii_str += '\n'
            
            return ascii_str
        except ImportError:
            return "Error: Pillow not installed. Run: pip install pillow"
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def text_to_ascii_art(text: str, font: str = "standard") -> str:
        """Convert text to ASCII art banner."""
        try:
            import pyfiglet
            
            return pyfiglet.figlet_format(text, font=font)
        except ImportError:
            return "Error: pyfiglet not installed. Run: pip install pyfiglet"


class MatrixScreensaver(App):
    """Matrix-style screensaver."""
    
    def __init__(self, duration: int = 60):
        super().__init__()
        self.duration = duration
        self.start_time = time.time()
    
    def compose(self):
        yield Static(id="matrix")
    
    def on_mount(self):
        self.set_interval(0.1, self.update_matrix)
    
    def update_matrix(self):
        """Update matrix animation."""
        if time.time() - self.start_time > self.duration:
            self.exit()
            return
        
        # Generate random matrix-like text
        chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノ"
        lines = []
        for _ in range(20):
            line = ''.join(random.choice(chars) for _ in range(80))
            lines.append(line)
        
        self.query_one("#matrix", Static).update('\n'.join(lines))


class TerminalPet:
    """Virtual pet that lives in the terminal status bar."""
    
    PETS = {
        "cat": ["😺", "😸", "😹", "😻", "😼", "😽"],
        "dog": ["🐕", "🐶", "🦮", "🐕‍🦺"],
        "bird": ["🐦", "🐤", "🐥", "🦜"],
        "fish": ["🐟", "🐠", "🐡"],
    }
    
    MOODS = ["happy", "sad", "sleepy", "hungry", "playful"]
    
    def __init__(self, pet_type: str = "cat"):
        self.pet_type = pet_type
        self.mood = "happy"
        self.hunger = 50
        self.happiness = 80
        self.load_state()
    
    def load_state(self):
        """Load pet state from file."""
        state_file = Path.home() / ".djinn" / "pet_state.json"
        if state_file.exists():
            import json
            with open(state_file) as f:
                state = json.load(f)
                self.mood = state.get("mood", "happy")
                self.hunger = state.get("hunger", 50)
                self.happiness = state.get("happiness", 80)
    
    def save_state(self):
        """Save pet state."""
        import json
        state_file = Path.home() / ".djinn" / "pet_state.json"
        state_file.parent.mkdir(exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump({
                "mood": self.mood,
                "hunger": self.hunger,
                "happiness": self.happiness
            }, f)
    
    def get_emoji(self) -> str:
        """Get current pet emoji."""
        emojis = self.PETS.get(self.pet_type, self.PETS["cat"])
        return random.choice(emojis)
    
    def feed(self):
        """Feed the pet."""
        self.hunger = max(0, self.hunger - 30)
        self.happiness = min(100, self.happiness + 10)
        self.update_mood()
        self.save_state()
    
    def play(self):
        """Play with the pet."""
        self.happiness = min(100, self.happiness + 20)
        self.hunger = min(100, self.hunger + 10)
        self.update_mood()
        self.save_state()
    
    def update_mood(self):
        """Update pet mood based on stats."""
        if self.happiness > 70:
            self.mood = "happy"
        elif self.happiness < 30:
            self.mood = "sad"
        elif self.hunger > 70:
            self.mood = "hungry"
        else:
            self.mood = random.choice(["playful", "sleepy"])
    
    def status(self) -> str:
        """Get pet status string."""
        return f"{self.get_emoji()} {self.mood.title()} | Hunger: {self.hunger}% | Happy: {self.happiness}%"


class TypingGame:
    """Z-Type style typing game."""
    
    WORDS = [
        "function", "variable", "class", "import", "return", "async", "await",
        "const", "let", "var", "interface", "type", "enum", "module",
        "docker", "kubernetes", "python", "javascript", "typescript", "rust"
    ]
    
    def __init__(self):
        self.score = 0
        self.lives = 3
    
    def play(self):
        """Start the typing game."""
        from rich.console import Console
        from rich.prompt import Prompt
        
        console = Console()
        
        console.print("\n[bold green]⌨️  Typing Game - Destroy the falling words![/bold green]")
        console.print(f"[muted]Lives: {self.lives} | Score: {self.score}[/muted]\n")
        
        while self.lives > 0:
            # Pick random word
            word = random.choice(self.WORDS)
            
            console.print(f"\n[bold yellow]>>> {word} <<<[/bold yellow]")
            
            # Get user input with timeout (simplified - no real timeout in CLI)
            user_input = Prompt.ask("[prompt]Type the word[/prompt]")
            
            if user_input == word:
                self.score += len(word) * 10
                console.print(f"[success]✓ Correct! +{len(word) * 10} points[/success]")
            else:
                self.lives -= 1
                console.print(f"[error]✗ Wrong! Lives remaining: {self.lives}[/error]")
            
            console.print(f"[muted]Score: {self.score}[/muted]")
        
        console.print(f"\n[bold red]Game Over![/bold red]")
        console.print(f"[highlight]Final Score: {self.score}[/highlight]\n")


class StockTicker:
    """Real-time stock/crypto price display."""
    
    @staticmethod
    def get_crypto_price(symbol: str) -> Dict:
        """Get crypto price from CoinGecko."""
        import requests
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true"
            r = requests.get(url, timeout=5)
            data = r.json()
            
            if symbol in data:
                return {
                    "symbol": symbol.upper(),
                    "price": data[symbol]["usd"],
                    "change_24h": data[symbol].get("usd_24h_change", 0)
                }
        except:
            pass
        
        return{"error": "Could not fetch price"}
    
    @staticmethod
    def format_ticker(data: Dict) -> str:
        """Format ticker display."""
        if "error" in data:
            return data["error"]
        
        price = data["price"]
        change = data.get("change_24h", 0)
        
        color = "success" if change > 0 else "error"
        arrow = "↑" if change > 0 else "↓"
        
        return f"[bold]{data['symbol']}[/bold]: ${price:,.2f} [{color}]{arrow} {abs(change):.2f}%[/{color}]"


def run_markdown_preview(file_path: str):
    """Launch markdown preview."""
    app = MarkdownPreview(file_path)
    app.run()


def run_hex_editor(file_path: str):
    """Launch hex editor."""
    app = HexEditor(file_path)
    app.run()


def run_git_graph():
    """Launch git graph."""
    app = GitGraphTUI()
    app.run()


def run_screensaver(duration: int = 60):
    """Launch Matrix screensaver."""
    app = MatrixScreensaver(duration)
    app.run()


from typing import Dict
