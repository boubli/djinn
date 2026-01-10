"""
Alias Manager - Save and manage command shortcuts.
"""
import json
from pathlib import Path
from typing import Dict, Optional


class AliasManager:
    """Manages command aliases/shortcuts."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            config_path = str(djinn_dir / "aliases.json")
        
        self.config_path = Path(config_path)
        self._aliases = None
    
    @property
    def aliases(self) -> Dict[str, str]:
        """Load aliases lazily."""
        if self._aliases is None:
            self._aliases = self._load()
        return self._aliases
    
    def _load(self) -> Dict[str, str]:
        """Load aliases from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save(self):
        """Save aliases to file."""
        with open(self.config_path, "w") as f:
            json.dump(self._aliases, f, indent=2)
    
    def add(self, name: str, prompt: str) -> bool:
        """Add a new alias."""
        name = name.lstrip("@").lower()
        self.aliases[name] = prompt
        self._save()
        return True
    
    def remove(self, name: str) -> bool:
        """Remove an alias."""
        name = name.lstrip("@").lower()
        if name in self.aliases:
            del self.aliases[name]
            self._save()
            return True
        return False
    
    def get(self, name: str) -> Optional[str]:
        """Get an alias prompt."""
        name = name.lstrip("@").lower()
        return self.aliases.get(name)
    
    def list_all(self) -> Dict[str, str]:
        """List all aliases."""
        return self.aliases.copy()
    
    def resolve(self, text: str) -> str:
        """Resolve @alias in text to actual prompt."""
        if text.startswith("@"):
            parts = text.split(" ", 1)
            alias_name = parts[0]
            extra = parts[1] if len(parts) > 1 else ""
            
            prompt = self.get(alias_name)
            if prompt:
                return f"{prompt} {extra}".strip()
        
        return text
