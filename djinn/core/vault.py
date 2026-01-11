"""
Vault Manager - Secure storage for sensitive command snippets.
"""
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, Optional
from getpass import getpass


class VaultManager:
    """Manages secure storage for sensitive command snippets."""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            storage_path = str(djinn_dir / "vault.json")
        
        self.storage_path = Path(storage_path)
        self.vault = self._load()
    
    def _load(self) -> Dict:
        """Load vault from file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    return json.load(f)
            except:
                pass
        return {"entries": {}, "locked": False}
    
    def _save(self):
        """Save vault to file."""
        with open(self.storage_path, "w") as f:
            json.dump(self.vault, f, indent=2)
    
    def _obfuscate(self, text: str) -> str:
        """Simple obfuscation (not true encryption, but hides from casual view)."""
        return base64.b64encode(text.encode()).decode()
    
    def _deobfuscate(self, text: str) -> str:
        """Reverse obfuscation."""
        try:
            return base64.b64decode(text.encode()).decode()
        except:
            return text
    
    def add(self, name: str, command: str, description: str = ""):
        """Add a command to the vault."""
        self.vault["entries"][name] = {
            "command": self._obfuscate(command),
            "description": description
        }
        self._save()
    
    def get(self, name: str) -> Optional[str]:
        """Get a command from the vault."""
        entry = self.vault["entries"].get(name)
        if entry:
            return self._deobfuscate(entry["command"])
        return None
    
    def list_all(self) -> Dict[str, str]:
        """List all vault entries (names and descriptions only)."""
        return {
            name: entry.get("description", "")
            for name, entry in self.vault["entries"].items()
        }
    
    def remove(self, name: str) -> bool:
        """Remove an entry from the vault."""
        if name in self.vault["entries"]:
            del self.vault["entries"][name]
            self._save()
            return True
        return False
