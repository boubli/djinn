"""
Auto-Fix Plugin - Analyzes failed commands and suggests fixes.
"""
from typing import Optional, Tuple

class AutoFixPlugin:
    """Plugin to handle command execution failures."""
    
    SYSTEM_PROMPT = """You are a terminal error expert. command failed.
    
    Task:
    1. Analyze the failed command and the error message.
    2. Provide a CORRECTED command that fixes the error.
    3. Output ONLY the corrected command. No explanation.
    
    Common fixes:
    - Typo correction (gti -> git)
    - Permission checks (add sudo)
    - Missing flags (--force)
    - Missing dependencies (suggest install command if appropriate, or the command to run)
    
    If the error is about a missing tool, provide the installation command (e.g., 'pip install X' or 'npm install X').
    """

    def __init__(self, engine):
        self.engine = engine
    
    def generate_fix(self, command: str, error_output: str) -> Optional[str]:
        """Generate a fix for a failed command."""
        prompt = f"Command failed:\n{command}\n\nError output:\n{error_output}\n\nProvide the corrected command."
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
