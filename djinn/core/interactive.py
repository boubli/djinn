"""
Interactive Enhancements - Autocomplete, fuzzy search, streaming.
"""
import difflib
from typing import List, Optional, Callable
from rich.console import Console
from rich.live import Live
from rich.text import Text


class FuzzySearch:
    """Fuzzy search through command history."""
    
    def __init__(self, history_manager):
        self.history = history_manager
    
    def search(self, query: str, limit: int = 10) -> List[dict]:
        """Fuzzy search history by prompt or command."""
        all_entries = self.history.get_recent(100)  # Get recent 100
        
        results = []
        for entry in all_entries:
            # Check similarity with prompt and command
            prompt_ratio = difflib.SequenceMatcher(
                None, query.lower(), entry['prompt'].lower()
            ).ratio()
            
            cmd_ratio = difflib.SequenceMatcher(
                None, query.lower(), entry['command'].lower()
            ).ratio()
            
            score = max(prompt_ratio, cmd_ratio)
            if score > 0.3:  # Threshold
                results.append({**entry, 'score': score})
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]


class StreamingOutput:
    """Display streaming LLM output."""
    
    def __init__(self, console: Console):
        self.console = console
    
    def stream(self, generator: Callable, prefix: str = ""):
        """Stream output character by character."""
        text = Text()
        text.append(prefix, style="success")
        
        with Live(text, console=self.console, refresh_per_second=20) as live:
            buffer = ""
            for chunk in generator():
                buffer += chunk
                text = Text()
                text.append(prefix, style="success")
                text.append(buffer, style="command")
                live.update(text)
        
        return buffer


class AutoCompleter:
    """Autocomplete suggestions for prompts."""
    
    COMMON_PROMPTS = [
        "list all files",
        "find files larger than",
        "delete all",
        "create folder",
        "compress files",
        "copy files to",
        "move files to",
        "rename files",
        "search for text",
        "show disk usage",
        "show memory usage",
        "kill process",
        "start service",
        "stop service",
        "restart service",
        "view logs",
        "download file from",
        "upload file to",
        "backup folder",
        "restore backup",
    ]
    
    GIT_PROMPTS = [
        "undo last commit",
        "create branch",
        "merge branch",
        "show changes",
        "stash changes",
        "view commit history",
        "push to remote",
        "pull from remote",
        "reset to commit",
        "cherry pick",
    ]
    
    DOCKER_PROMPTS = [
        "list containers",
        "stop all containers",
        "remove unused images",
        "view logs",
        "exec into container",
        "build image",
        "push image",
        "pull image",
    ]
    
    def __init__(self, history_manager=None):
        self.history = history_manager
        self.prompts = self.COMMON_PROMPTS + self.GIT_PROMPTS + self.DOCKER_PROMPTS
    
    def complete(self, partial: str, limit: int = 5) -> List[str]:
        """Get autocomplete suggestions."""
        partial = partial.lower()
        suggestions = []
        
        # Check built-in prompts
        for prompt in self.prompts:
            if prompt.lower().startswith(partial):
                suggestions.append(prompt)
        
        # Check history if available
        if self.history:
            for entry in self.history.get_recent(50):
                if entry['prompt'].lower().startswith(partial):
                    if entry['prompt'] not in suggestions:
                        suggestions.append(entry['prompt'])
        
        return suggestions[:limit]


class DryRun:
    """Dry-run mode - explain what command would do without running."""
    
    SYSTEM_PROMPT = """You are a command analyzer. Explain what this command would do step by step without running it.

Rules:
- Be concise but thorough
- List each operation the command would perform
- Highlight any dangerous operations
- Mention files/directories that would be affected

Format your response as:
1. [action 1]
2. [action 2]
..."""

    def __init__(self, engine):
        self.engine = engine
    
    def analyze(self, command: str) -> Optional[str]:
        """Analyze what a command would do."""
        prompt = f"Analyze this command: {command}"
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class LearningSystem:
    """Learn from user corrections to improve future suggestions."""
    
    def __init__(self, storage_path: str = None):
        from pathlib import Path
        import json
        
        if storage_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            storage_path = str(djinn_dir / "learning.json")
        
        self.storage_path = Path(storage_path)
        self._patterns = None
    
    @property
    def patterns(self) -> dict:
        if self._patterns is None:
            self._patterns = self._load()
        return self._patterns
    
    def _load(self) -> dict:
        import json
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    return json.load(f)
            except:
                pass
        return {"corrections": [], "preferences": {}}
    
    def _save(self):
        import json
        with open(self.storage_path, "w") as f:
            json.dump(self._patterns, f, indent=2)
    
    def record_correction(self, original_prompt: str, original_cmd: str, corrected_cmd: str):
        """Record when user corrects a command."""
        self.patterns["corrections"].append({
            "prompt": original_prompt,
            "original": original_cmd,
            "corrected": corrected_cmd,
        })
        self._save()
    
    def get_similar_corrections(self, prompt: str) -> List[dict]:
        """Get corrections for similar prompts."""
        results = []
        for correction in self.patterns["corrections"]:
            if difflib.SequenceMatcher(
                None, prompt.lower(), correction["prompt"].lower()
            ).ratio() > 0.7:
                results.append(correction)
        return results
