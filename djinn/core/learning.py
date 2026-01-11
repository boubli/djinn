"""
Learning Engine - Learn from user patterns and provide personalized suggestions.
"""
import json
from typing import Dict, List, Optional
from pathlib import Path
from collections import Counter
from datetime import datetime


class LearningEngine:
    """Learns from user command patterns."""
    
    def __init__(self):
        self.djinn_dir = Path.home() / ".djinn"
        self.patterns_file = self.djinn_dir / "patterns.json"
        self.djinn_dir.mkdir(exist_ok=True)
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load learned patterns."""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file) as f:
                    return json.load(f)
            except:
                pass
        return {
            "sequences": {},  # Command sequences (A -> B happens often)
            "time_patterns": {},  # Commands by time of day
            "directory_patterns": {},  # Commands by directory type
            "shortcuts": {},  # User-defined shortcuts
            "favorites": [],  # Frequently used prompts
        }
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, "w") as f:
            json.dump(self.patterns, f, indent=2)
    
    def learn_sequence(self, prev_command: str, current_command: str):
        """Learn that these commands often follow each other."""
        if not prev_command or not current_command:
            return
        
        key = prev_command[:50]  # Truncate for key
        if key not in self.patterns["sequences"]:
            self.patterns["sequences"][key] = {}
        
        next_key = current_command[:50]
        self.patterns["sequences"][key][next_key] = \
            self.patterns["sequences"][key].get(next_key, 0) + 1
        
        self._save_patterns()
    
    def learn_time_pattern(self, command: str):
        """Learn what commands are used at what times."""
        hour = datetime.now().hour
        time_slot = f"{hour:02d}:00"
        
        if time_slot not in self.patterns["time_patterns"]:
            self.patterns["time_patterns"][time_slot] = {}
        
        cmd_key = command[:30]
        self.patterns["time_patterns"][time_slot][cmd_key] = \
            self.patterns["time_patterns"][time_slot].get(cmd_key, 0) + 1
        
        self._save_patterns()
    
    def learn_directory_pattern(self, directory_type: str, command: str):
        """Learn what commands are used in what directory types."""
        if directory_type not in self.patterns["directory_patterns"]:
            self.patterns["directory_patterns"][directory_type] = {}
        
        cmd_key = command[:30]
        self.patterns["directory_patterns"][directory_type][cmd_key] = \
            self.patterns["directory_patterns"][directory_type].get(cmd_key, 0) + 1
        
        self._save_patterns()
    
    def add_shortcut(self, name: str, prompt: str):
        """Add a personalized shortcut."""
        self.patterns["shortcuts"][name] = prompt
        self._save_patterns()
    
    def get_shortcut(self, name: str) -> Optional[str]:
        """Get a shortcut prompt."""
        return self.patterns["shortcuts"].get(name)
    
    def list_shortcuts(self) -> Dict:
        """List all shortcuts."""
        return self.patterns["shortcuts"]
    
    def suggest_next(self, current_command: str) -> List[str]:
        """Suggest next likely commands based on learned patterns."""
        key = current_command[:50]
        if key in self.patterns["sequences"]:
            sorted_next = sorted(
                self.patterns["sequences"][key].items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [cmd for cmd, _ in sorted_next[:5]]
        return []
    
    def suggest_for_time(self) -> List[str]:
        """Suggest commands based on current time."""
        hour = datetime.now().hour
        time_slot = f"{hour:02d}:00"
        
        if time_slot in self.patterns["time_patterns"]:
            sorted_cmds = sorted(
                self.patterns["time_patterns"][time_slot].items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [cmd for cmd, _ in sorted_cmds[:5]]
        return []
    
    def suggest_for_directory(self, directory_type: str) -> List[str]:
        """Suggest commands for a directory type."""
        if directory_type in self.patterns["directory_patterns"]:
            sorted_cmds = sorted(
                self.patterns["directory_patterns"][directory_type].items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [cmd for cmd, _ in sorted_cmds[:5]]
        return []
    
    def get_insights(self) -> Dict:
        """Get insights about usage patterns."""
        return {
            "total_sequences": len(self.patterns["sequences"]),
            "total_shortcuts": len(self.patterns["shortcuts"]),
            "active_times": list(self.patterns["time_patterns"].keys())[:5],
            "directory_types": list(self.patterns["directory_patterns"].keys()),
        }
