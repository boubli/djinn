"""
Plugins - Specialized command helpers for Git, Docker, etc.
"""
from typing import Optional
from djinn.core.engine import DjinnEngine


class GitPlugin:
    """Git-specific command generator."""
    
    SYSTEM_PROMPT = """You are a Git expert. Convert the user's natural language description into a git command.

Rules:
- Output ONLY the git command, no explanations
- Use common git commands and flags
- For complex operations, chain commands with &&
- Be safe with destructive operations (prefer --dry-run when appropriate)

Common patterns:
- "undo last commit" -> git reset --soft HEAD~1
- "see what changed" -> git diff
- "save work temporarily" -> git stash
- "start fresh branch" -> git checkout -b <branch>"""

    def __init__(self, engine: DjinnEngine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        """Generate a git command."""
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class DockerPlugin:
    """Docker-specific command generator."""
    
    SYSTEM_PROMPT = """You are a Docker expert. Convert the user's natural language description into a docker command.

Rules:
- Output ONLY the docker command, no explanations
- Use docker and docker-compose commands appropriately
- For cleanup operations, use appropriate flags
- Include common flags like --rm, -it when appropriate

Common patterns:
- "cleanup unused" -> docker system prune -a
- "list running" -> docker ps
- "stop all containers" -> docker stop $(docker ps -q)
- "view logs" -> docker logs -f <container>"""

    def __init__(self, engine: DjinnEngine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        """Generate a docker command."""
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class UndoPlugin:
    """Generate undo/reverse commands."""
    
    SYSTEM_PROMPT = """You are a command reversal expert. Given a command, generate the command that would undo or reverse its effects.

Rules:
- Output ONLY the undo command, no explanations
- If the action cannot be undone, output "IRREVERSIBLE"
- Be safe and conservative

Examples:
- "mkdir foo" -> rmdir foo
- "git commit" -> git reset --soft HEAD~1
- "rm file" -> IRREVERSIBLE (file is deleted)
- "mv a b" -> mv b a"""

    def __init__(self, engine: DjinnEngine):
        self.engine = engine
    
    def generate_undo(self, command: str) -> Optional[str]:
        """Generate an undo command."""
        prompt = f"Generate the command to undo: {command}"
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ChainPlugin:
    """Generate multi-step command chains."""
    
    SYSTEM_PROMPT = """You are a shell scripting expert. Convert the user's multi-step task into a chained command.

Rules:
- Output commands chained with && (or ; if order doesn't matter)
- Use proper shell syntax for the detected shell
- Be efficient - combine operations when possible
- Output ONLY the commands, no explanations

Examples:
- "find large files then delete them" -> find . -size +100M -exec rm {} \;
- "build and deploy" -> npm run build && npm run deploy
- "backup then compress" -> cp -r folder backup && tar -czf backup.tar.gz backup"""

    def __init__(self, engine: DjinnEngine):
        self.engine = engine
    
    def generate(self, prompt: str, context: str = None) -> Optional[str]:
        """Generate a chained command."""
        system = self.SYSTEM_PROMPT
        if context:
            system += f"\n\nContext: {context}"
        return self.engine.backend.generate(prompt, system)


class AutoFixPlugin:
    """Suggest fixes for failed commands."""
    
    SYSTEM_PROMPT = """You are a debugging expert. Given a failed command and its error, suggest a fix.

Rules:
- Output ONLY the corrected command, no explanations
- If you need to show multiple steps, chain with &&
- Common fixes: permissions (sudo), missing packages, typos, wrong flags

Examples:
- "Permission denied" -> sudo <original command>
- "command not found" -> install the package first
- "No such file" -> check path or create directory first"""

    def __init__(self, engine: DjinnEngine):
        self.engine = engine
    
    def suggest_fix(self, command: str, error: str) -> Optional[str]:
        """Suggest a fix for a failed command."""
        prompt = f"Command: {command}\nError: {error}\nSuggest a fix."
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
