"""
Clipboard Manager - Manage command clipboard history.
"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class ClipboardManager:
    """Manages clipboard history for copied commands."""
    
    MAX_HISTORY = 50
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            storage_path = str(djinn_dir / "clipboard.json")
        
        self.storage_path = Path(storage_path)
        self.history = self._load()
    
    def _load(self) -> List[dict]:
        """Load clipboard history from file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save(self):
        """Save clipboard history to file."""
        with open(self.storage_path, "w") as f:
            json.dump(self.history[-self.MAX_HISTORY:], f, indent=2)
    
    def add(self, command: str, prompt: str = None):
        """Add a command to clipboard history."""
        entry = {
            "command": command,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        }
        self.history.append(entry)
        self._save()
    
    def get_recent(self, limit: int = 10) -> List[dict]:
        """Get recent clipboard entries."""
        return list(reversed(self.history[-limit:]))
    
    def get(self, index: int) -> Optional[dict]:
        """Get a specific clipboard entry by index (1-based, most recent first)."""
        if 1 <= index <= len(self.history):
            return self.history[-index]
        return None
    
    def clear(self):
        """Clear clipboard history."""
        self.history = []
        self._save()
    
    def search(self, query: str) -> List[dict]:
        """Search clipboard history."""
        results = []
        query_lower = query.lower()
        for entry in reversed(self.history):
            if query_lower in entry["command"].lower():
                results.append(entry)
            elif entry.get("prompt") and query_lower in entry["prompt"].lower():
                results.append(entry)
        return results[:20]
