"""
SSH Mode - Generate commands for remote servers.
"""
from typing import Optional


class SSHPlugin:
    """Generate SSH commands for remote execution."""
    
    SYSTEM_PROMPT = """You are an SSH and remote server expert. Generate a command to run on a remote server via SSH.

Rules:
- Output the full ssh command: ssh user@host "command"
- Use appropriate quoting for the remote command
- For file transfers, use scp or rsync
- Be security-conscious

Examples:
- "check disk space" -> ssh user@host "df -h"
- "view logs" -> ssh user@host "tail -f /var/log/syslog"
- "copy file" -> scp file.txt user@host:/path/"""

    def __init__(self, engine, user: str = None, host: str = None):
        self.engine = engine
        self.user = user
        self.host = host
    
    def generate(self, prompt: str, user: str = None, host: str = None) -> Optional[str]:
        """Generate SSH command."""
        user = user or self.user or "user"
        host = host or self.host or "server"
        
        full_prompt = f"For {user}@{host}: {prompt}"
        return self.engine.backend.generate(full_prompt, self.SYSTEM_PROMPT)


class APIPlugin:
    """Generate API/curl commands."""
    
    SYSTEM_PROMPT = """You are an API and HTTP expert. Generate curl commands for API requests.

Rules:
- Output a curl command
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)
- Include headers when needed (-H)
- For POST/PUT, include data (-d)
- Use -s for silent mode, -o for output

Examples:
- "get weather" -> curl -s "https://wttr.in/London?format=3"
- "post json" -> curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' URL"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        """Generate API/curl command."""
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
