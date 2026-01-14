"""
Context-Aware Help - Analyze last command errors and explain them.

Example:
    djinn wtf  # or djinn ???
"""
import os
import subprocess
from pathlib import Path


class ContextAwareHelper:
    """Provides context-aware help based on recent errors."""
    
    def __init__(self, engine):
        self.engine = engine
        self.history_file = Path.home() / ".djinn" / "last_error.txt"
    
    def save_last_error(self, command: str, error: str):
        """Save the last error for later analysis."""
        self.history_file.parent.mkdir(exist_ok=True)
        with open(self.history_file, "w") as f:
            f.write(f"COMMAND: {command}\n")
            f.write(f"ERROR:\n{error}\n")
    
    def get_last_error(self) -> tuple:
        """Retrieve the last saved error."""
        if not self.history_file.exists():
            return None, None
        
        with open(self.history_file, "r") as f:
            content = f.read()
        
        lines = content.split("\n")
        command = None
        error_lines = []
        in_error = False
        
        for line in lines:
            if line.startswith("COMMAND: "):
                command = line[9:]
            elif line.startswith("ERROR:"):
                in_error = True
            elif in_error:
                error_lines.append(line)
        
        error = "\n".join(error_lines).strip()
        return command, error
    
    def explain_last_error(self) -> str:
        """Generate explanation for the last error."""
        command, error = self.get_last_error()
        
        if not command or not error:
            return "No recent errors found. Run a command that fails to get help!"
        
        prompt = f"""A user ran this command and got an error:

Command: {command}

Error:
{error}

Explain what went wrong in simple terms and suggest how to fix it. Be concise and practical.

Explanation:"""
        
        explanation = self.engine.backend.generate(
            prompt,
            system_prompt="You are a helpful terminal expert. Explain errors clearly and suggest fixes."
        )
        
        return explanation
    
    def analyze_shell_history(self) -> str:
        """Analyze recent shell history for context."""
        # Try to read last few commands from shell history
        history_paths = [
            Path.home() / ".bash_history",
            Path.home() / ".zsh_history",
            Path.home() / "AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
        ]
        
        for history_path in history_paths:
            if history_path.exists():
                try:
                    with open(history_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        recent = lines[-10:]  # Last 10 commands
                        return "\n".join(recent)
                except:
                    continue
        
        return "No shell history found"


def get_shell_help(query: str, engine) -> str:
    """Get help for any shell-related query."""
    prompt = f"""The user needs help with: {query}

Provide clear, concise help. Include:
1. What they're trying to do
2. The correct command(s) to use
3. Common mistakes to avoid

Help:"""
    
    return engine.backend.generate(
        prompt,
        system_prompt="You are a terminal expert. Provide practical, actionable help."
    )
