"""
Advanced Features - Danger detection, templates, snippets, suggestions.
"""
import re
from typing import List, Optional, Dict
from pathlib import Path
import json


class DangerDetector:
    """Detect dangerous commands before execution."""
    
    # Dangerous patterns to watch for
    DANGEROUS_PATTERNS = [
        # File deletion
        (r'\brm\s+-rf?\s+(/|~|\*)', "Recursive delete from root/home"),
        (r'\brm\s+-rf?\s+\*', "Delete everything in current directory"),
        (r'del\s+/[sS]', "Recursive delete (Windows)"),
        (r'Remove-Item.*-Recurse.*-Force', "Recursive force delete (PowerShell)"),
        
        # Disk operations
        (r'\bdd\s+if=.*of=', "Direct disk write - can destroy data"),
        (r'mkfs\.', "Format filesystem"),
        (r'format\s+[a-zA-Z]:', "Format drive (Windows)"),
        
        # Database
        (r'DROP\s+(TABLE|DATABASE)', "Drop database/table"),
        (r'TRUNCATE\s+TABLE', "Truncate table"),
        (r'DELETE\s+FROM\s+\w+\s*;?\s*$', "Delete all rows from table"),
        
        # System
        (r':(){ :\|:& };:', "Fork bomb"),
        (r'chmod\s+-R\s+777', "Insecure permissions"),
        (r'chmod\s+777\s+/', "Root permission change"),
        (r'>\s*/dev/sd', "Overwrite disk device"),
        
        # Git
        (r'git\s+push.*--force', "Force push - can lose commits"),
        (r'git\s+reset\s+--hard', "Hard reset - loses uncommitted changes"),
        
        # Network
        (r'curl.*\|\s*(bash|sh)', "Piping remote script to shell"),
        (r'wget.*\|\s*(bash|sh)', "Piping remote script to shell"),
    ]
    
    @classmethod
    def check(cls, command: str) -> List[Dict[str, str]]:
        """Check command for dangerous patterns. Returns list of warnings."""
        warnings = []
        for pattern, description in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                warnings.append({
                    "pattern": pattern,
                    "description": description,
                    "severity": "high"
                })
        return warnings
    
    @classmethod
    def is_dangerous(cls, command: str) -> bool:
        """Quick check if command is dangerous."""
        return len(cls.check(command)) > 0


class TemplateManager:
    """Manage command templates for common tasks."""
    
    BUILTIN_TEMPLATES = {
        "python-project": {
            "description": "Create a new Python project structure",
            "command": "mkdir {name} && cd {name} && python -m venv venv && mkdir src tests && touch src/__init__.py tests/__init__.py README.md requirements.txt",
            "params": ["name"]
        },
        "node-project": {
            "description": "Create a new Node.js project",
            "command": "mkdir {name} && cd {name} && npm init -y && mkdir src tests && touch src/index.js README.md",
            "params": ["name"]
        },
        "git-init": {
            "description": "Initialize git with .gitignore",
            "command": "git init && echo 'node_modules/\n__pycache__/\n.env\n*.log' > .gitignore && git add . && git commit -m 'Initial commit'",
            "params": []
        },
        "docker-compose": {
            "description": "Create docker-compose.yml template",
            "command": "echo 'version: \"3.8\"\nservices:\n  app:\n    build: .\n    ports:\n      - \"3000:3000\"' > docker-compose.yml",
            "params": []
        },
        "cleanup": {
            "description": "Clean temp files and caches",
            "command": "find . -name '*.pyc' -delete && find . -name '__pycache__' -type d -delete && find . -name 'node_modules' -type d -prune -exec rm -rf {} +",
            "params": []
        },
        "backup": {
            "description": "Create timestamped backup",
            "command": "tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz {path}",
            "params": ["path"]
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            config_path = str(djinn_dir / "templates.json")
        
        self.config_path = Path(config_path)
        self._templates = None
    
    @property
    def templates(self) -> Dict:
        """Load templates lazily."""
        if self._templates is None:
            self._templates = self._load()
        return self._templates
    
    def _load(self) -> Dict:
        """Load custom templates from file."""
        templates = self.BUILTIN_TEMPLATES.copy()
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    custom = json.load(f)
                    templates.update(custom)
            except:
                pass
        return templates
    
    def _save(self):
        """Save custom templates."""
        # Only save non-builtin templates
        custom = {k: v for k, v in self._templates.items() 
                  if k not in self.BUILTIN_TEMPLATES}
        with open(self.config_path, "w") as f:
            json.dump(custom, f, indent=2)
    
    def get(self, name: str) -> Optional[Dict]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def add(self, name: str, command: str, description: str = "", params: List[str] = None):
        """Add a custom template."""
        self.templates[name] = {
            "description": description,
            "command": command,
            "params": params or []
        }
        self._save()
    
    def remove(self, name: str) -> bool:
        """Remove a custom template."""
        if name in self.templates and name not in self.BUILTIN_TEMPLATES:
            del self.templates[name]
            self._save()
            return True
        return False
    
    def list_all(self) -> Dict:
        """List all templates."""
        return self.templates.copy()
    
    def render(self, name: str, **kwargs) -> Optional[str]:
        """Render a template with given parameters."""
        template = self.get(name)
        if not template:
            return None
        
        command = template["command"]
        for key, value in kwargs.items():
            command = command.replace(f"{{{key}}}", value)
        
        return command


class SnippetManager:
    """Manage multi-line command snippets."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            config_path = str(djinn_dir / "snippets.json")
        
        self.config_path = Path(config_path)
        self._snippets = None
    
    @property
    def snippets(self) -> Dict[str, str]:
        if self._snippets is None:
            self._snippets = self._load()
        return self._snippets
    
    def _load(self) -> Dict[str, str]:
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save(self):
        with open(self.config_path, "w") as f:
            json.dump(self._snippets, f, indent=2)
    
    def add(self, name: str, content: str):
        """Add a snippet."""
        self.snippets[name] = content
        self._save()
    
    def get(self, name: str) -> Optional[str]:
        """Get a snippet."""
        return self.snippets.get(name)
    
    def remove(self, name: str) -> bool:
        """Remove a snippet."""
        if name in self.snippets:
            del self.snippets[name]
            self._save()
            return True
        return False
    
    def list_all(self) -> Dict[str, str]:
        """List all snippets."""
        return self.snippets.copy()


class MultiSuggestion:
    """Generate multiple command suggestions."""
    
    SYSTEM_PROMPT = """You are a command generator. Generate exactly 3 different command options for the user's request.

Rules:
- Output ONLY the commands, one per line
- Number them 1., 2., 3.
- Make each option use a different approach or tool
- Be concise

Example output:
1. find . -name "*.log" -delete
2. rm -f *.log
3. ls *.log | xargs rm"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str, context: str = None) -> List[str]:
        """Generate multiple suggestions."""
        system = self.SYSTEM_PROMPT
        if context:
            system += f"\n\nContext: {context}"
        
        response = self.engine.backend.generate(prompt, system)
        if not response:
            return []
        
        # Parse numbered list
        suggestions = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                # Remove numbering
                cmd = re.sub(r'^\d+[\.\)]\s*', '', line)
                if cmd:
                    suggestions.append(cmd)
        
        return suggestions[:3]  # Max 3
