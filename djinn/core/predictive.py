"""
Predictive Commands - Suggest next likely commands based on context and history.
"""
from typing import List, Dict, Optional
from collections import Counter


class PredictiveEngine:
    """Predicts next likely commands based on history and context."""
    
    # Common command sequences
    SEQUENCES = {
        "git add": ["git commit", "git status"],
        "git commit": ["git push", "git log"],
        "git pull": ["git status", "npm install", "pip install"],
        "git checkout": ["git pull", "git status"],
        "npm install": ["npm run dev", "npm start", "npm test"],
        "npm run build": ["npm run deploy", "npm run test"],
        "pip install": ["python", "pytest"],
        "docker build": ["docker run", "docker push"],
        "docker-compose up": ["docker-compose logs", "docker-compose down"],
        "cd": ["ls", "dir", "code ."],
        "mkdir": ["cd"],
        "pytest": ["git add", "git commit"],
    }
    
    # Context-based suggestions
    CONTEXT_SUGGESTIONS = {
        "package.json": ["npm install", "npm run dev", "npm test"],
        "requirements.txt": ["pip install -r requirements.txt", "python", "pytest"],
        "Dockerfile": ["docker build -t app .", "docker run", "docker-compose up"],
        "docker-compose.yml": ["docker-compose up", "docker-compose down", "docker-compose logs"],
        ".git": ["git status", "git pull", "git log --oneline"],
        "Makefile": ["make", "make build", "make test"],
        "pyproject.toml": ["pip install -e .", "pytest", "python -m build"],
        "Cargo.toml": ["cargo build", "cargo run", "cargo test"],
        "go.mod": ["go build", "go run .", "go test"],
    }
    
    def __init__(self, history_manager=None):
        self.history = history_manager
    
    def predict_next(self, last_command: str, context_files: List[str] = None) -> List[str]:
        """Predict next likely commands."""
        suggestions = []
        
        # Check sequence patterns
        for pattern, next_cmds in self.SEQUENCES.items():
            if pattern in last_command.lower():
                suggestions.extend(next_cmds)
                break
        
        # Check context
        if context_files:
            for file, cmds in self.CONTEXT_SUGGESTIONS.items():
                if file in context_files:
                    suggestions.extend(cmds)
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        
        return unique[:5]
    
    def get_frequent_commands(self, limit: int = 5) -> List[str]:
        """Get most frequently used commands from history."""
        if not self.history:
            return []
        
        try:
            recent = self.history.get_recent(100)
            commands = [entry.get("command", "") for entry in recent]
            counter = Counter(commands)
            return [cmd for cmd, _ in counter.most_common(limit)]
        except:
            return []
    
    def suggest_for_directory(self, files: List[str]) -> List[str]:
        """Suggest commands based on directory contents."""
        suggestions = []
        
        for file in files:
            for pattern, cmds in self.CONTEXT_SUGGESTIONS.items():
                if pattern in file:
                    suggestions.extend(cmds)
        
        return list(set(suggestions))[:5]
    
    def smart_suggest(self, prompt: str, context: Dict = None) -> List[str]:
        """Smart suggestions combining multiple signals."""
        suggestions = []
        
        # Time-based suggestions
        from datetime import datetime
        hour = datetime.now().hour
        
        if 9 <= hour <= 11:  # Morning - typically starting work
            suggestions.extend(["git pull", "git status"])
        elif 16 <= hour <= 18:  # End of day - wrapping up
            suggestions.extend(["git push", "git status"])
        
        # Keyword-based
        prompt_lower = prompt.lower()
        if "deploy" in prompt_lower:
            suggestions.extend(["git push", "npm run deploy", "docker push"])
        if "test" in prompt_lower:
            suggestions.extend(["npm test", "pytest", "go test"])
        if "clean" in prompt_lower:
            suggestions.extend(["docker system prune", "npm cache clean", "rm -rf node_modules"])
        
        return list(set(suggestions))[:5]
