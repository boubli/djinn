"""
Visualizer - Visualize command output with charts and graphs.
"""
from typing import Dict, List, Optional
import re


class OutputVisualizer:
    """Visualize command output as ASCII charts."""
    
    BLOCK_CHARS = "▁▂▃▄▅▆▇█"
    
    def bar_chart(self, data: Dict[str, float], width: int = 40) -> str:
        """Create a horizontal bar chart."""
        if not data:
            return "No data"
        
        max_val = max(data.values())
        max_label = max(len(str(k)) for k in data.keys())
        
        lines = []
        for label, value in data.items():
            bar_len = int((value / max_val) * width) if max_val > 0 else 0
            bar = "█" * bar_len
            lines.append(f"{str(label).ljust(max_label)} │{bar} {value:.1f}")
        
        return "\n".join(lines)
    
    def sparkline(self, values: List[float]) -> str:
        """Create a sparkline from values."""
        if not values:
            return ""
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val or 1
        
        spark = ""
        for v in values:
            idx = int(((v - min_val) / range_val) * (len(self.BLOCK_CHARS) - 1))
            spark += self.BLOCK_CHARS[idx]
        
        return spark
    
    def progress_bar(self, current: float, total: float, width: int = 30) -> str:
        """Create a progress bar."""
        percentage = (current / total * 100) if total > 0 else 0
        filled = int((current / total) * width) if total > 0 else 0
        
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def pie_chart(self, data: Dict[str, float], size: int = 10) -> str:
        """Create an ASCII pie chart representation."""
        total = sum(data.values())
        if total == 0:
            return "No data"
        
        lines = []
        for label, value in data.items():
            percentage = (value / total) * 100
            blocks = int(percentage / 5)  # Each block = 5%
            bar = "▓" * blocks + "░" * (20 - blocks)
            lines.append(f"{label}: {bar} {percentage:.1f}%")
        
        return "\n".join(lines)
    
    def histogram(self, values: List[float], bins: int = 10) -> str:
        """Create a histogram."""
        if not values:
            return "No data"
        
        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins if bins > 0 else 1
        
        bin_counts = [0] * bins
        for v in values:
            idx = min(int((v - min_val) / bin_width), bins - 1)
            bin_counts[idx] += 1
        
        max_count = max(bin_counts) or 1
        lines = []
        
        for i, count in enumerate(bin_counts):
            bar_len = int((count / max_count) * 30)
            bar = "█" * bar_len
            low = min_val + i * bin_width
            lines.append(f"{low:6.1f} │{bar} ({count})")
        
        return "\n".join(lines)
    
    def parse_df_output(self, df_output: str) -> Dict[str, Dict]:
        """Parse df -h output for visualization."""
        lines = df_output.strip().split("\n")
        if len(lines) < 2:
            return {}
        
        result = {}
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 6:
                filesystem = parts[0]
                size = parts[1]
                used = parts[2]
                use_percent = parts[4].replace("%", "")
                try:
                    result[parts[5]] = {
                        "filesystem": filesystem,
                        "size": size,
                        "used": used,
                        "percent": float(use_percent),
                    }
                except:
                    pass
        
        return result
    
    def visualize_disk_usage(self, df_output: str) -> str:
        """Visualize disk usage from df output."""
        data = self.parse_df_output(df_output)
        
        if not data:
            return "Could not parse disk usage"
        
        lines = ["📊 Disk Usage", ""]
        for mount, info in data.items():
            bar = self.progress_bar(info["percent"], 100)
            lines.append(f"{mount}")
            lines.append(f"  {bar} ({info['used']}/{info['size']})")
            lines.append("")
        
        return "\n".join(lines)
    
    def table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Create an ASCII table."""
        if not headers or not rows:
            return "No data"
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Build table
        separator = "─" * (sum(widths) + len(widths) * 3 + 1)
        
        lines = [separator]
        
        # Headers
        header_line = "│"
        for i, h in enumerate(headers):
            header_line += f" {h.ljust(widths[i])} │"
        lines.append(header_line)
        lines.append(separator)
        
        # Rows
        for row in rows:
            row_line = "│"
            for i, cell in enumerate(row):
                if i < len(widths):
                    row_line += f" {str(cell).ljust(widths[i])} │"
            lines.append(row_line)
        
        lines.append(separator)
        
        return "\n".join(lines)


class SpeechSynthesis:
    """Text-to-speech for notifications."""
    
    @staticmethod
    def speak(text: str, voice: str = None) -> bool:
        """Speak text using system TTS."""
        import subprocess
        import sys
        
        try:
            if sys.platform == "darwin":
                # macOS
                voice_opt = f"-v {voice}" if voice else ""
                subprocess.run(["say", voice_opt, text], capture_output=True)
                return True
            
            elif sys.platform == "win32":
                # Windows
                ps_cmd = f"""
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.Speak("{text}")
                """
                subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
                return True
            
            else:
                # Linux - try espeak
                subprocess.run(["espeak", text], capture_output=True)
                return True
                
        except:
            return False
    
    @staticmethod
    def notify_done(command: str):
        """Speak that a command is done."""
        short_cmd = command[:30] if len(command) > 30 else command
        SpeechSynthesis.speak(f"Command complete: {short_cmd}")
    
    @staticmethod
    def notify_error(message: str):
        """Speak an error."""
        SpeechSynthesis.speak(f"Error: {message}")


class ProjectSetup:
    """Quick project setup templates."""
    
    TEMPLATES = {
        "node": {
            "name": "Node.js Project",
            "commands": [
                "npm init -y",
                "mkdir src",
                "touch src/index.js",
                "npm install -D typescript @types/node",
            ],
            "files": {
                ".gitignore": "node_modules/\ndist/\n.env\n",
            }
        },
        "python": {
            "name": "Python Project", 
            "commands": [
                "python -m venv venv",
                "touch main.py",
                "touch requirements.txt",
            ],
            "files": {
                ".gitignore": "venv/\n__pycache__/\n.env\n*.pyc\n",
            }
        },
        "react": {
            "name": "React App",
            "commands": [
                "npx create-react-app . --template typescript",
            ],
        },
        "fastapi": {
            "name": "FastAPI Project",
            "commands": [
                "python -m venv venv",
                "pip install fastapi uvicorn",
            ],
            "files": {
                "main.py": '''from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
''',
                ".gitignore": "venv/\n__pycache__/\n.env\n",
            }
        },
        "express": {
            "name": "Express.js API",
            "commands": [
                "npm init -y",
                "npm install express cors dotenv",
            ],
            "files": {
                "index.js": '''const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'Hello World!' });
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
''',
            }
        },
    }
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List available templates."""
        return list(cls.TEMPLATES.keys())
    
    @classmethod
    def get_template(cls, name: str) -> Optional[Dict]:
        """Get a project template."""
        return cls.TEMPLATES.get(name.lower())
