"""
Voice Control - Control DJINN with voice commands.
"""
import subprocess
import sys
from typing import Callable, Dict, List, Optional
from rich.console import Console


class VoiceController:
    """Voice command recognition and execution."""
    
    VOICE_COMMANDS = {
        "list files": "ls -la",
        "show processes": "ps aux",
        "check disk": "df -h",
        "show memory": "free -h",
        "git status": "git status",
        "git pull": "git pull",
        "docker containers": "docker ps",
        "run tests": "npm test",
        "start server": "npm start",
        "build project": "npm run build",
        "install dependencies": "npm install",
        "clear screen": "clear",
    }
    
    def __init__(self):
        self.console = Console()
        self.listening = False
        self.engine = None
    
    def is_available(self) -> bool:
        """Check if speech recognition is available."""
        try:
            import speech_recognition
            return True
        except ImportError:
            return False
    
    def listen_once(self) -> Optional[str]:
        """Listen for a single voice command."""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                self.console.print("[cyan]🎤 Listening...[/cyan]")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            self.console.print("[muted]Processing...[/muted]")
            text = recognizer.recognize_google(audio)
            
            return text.lower()
            
        except ImportError:
            self.console.print("[red]speech_recognition not installed.[/red]")
            self.console.print("[muted]Install with: pip install SpeechRecognition pyaudio[/muted]")
            return None
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            return None
    
    def parse_command(self, text: str) -> Optional[str]:
        """Parse voice text into a shell command."""
        text = text.lower().strip()
        
        # Check exact matches
        if text in self.VOICE_COMMANDS:
            return self.VOICE_COMMANDS[text]
        
        # Check partial matches
        for voice_cmd, shell_cmd in self.VOICE_COMMANDS.items():
            if voice_cmd in text:
                return shell_cmd
        
        # Dynamic parsing for common patterns
        if text.startswith("open "):
            target = text[5:]
            return f"cd {target}"
        
        if text.startswith("create file "):
            filename = text[12:]
            return f"touch {filename}"
        
        if text.startswith("create folder ") or text.startswith("make directory "):
            dirname = text.split(" ", 2)[-1]
            return f"mkdir {dirname}"
        
        if text.startswith("delete "):
            target = text[7:]
            return f"rm {target}"
        
        if text.startswith("run "):
            command = text[4:]
            return command
        
        return None
    
    def execute_voice_command(self, text: str) -> bool:
        """Execute a parsed voice command."""
        command = self.parse_command(text)
        
        if command:
            self.console.print(f"[green]Executing: {command}[/green]")
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.stdout:
                    self.console.print(result.stdout)
                if result.stderr:
                    self.console.print(f"[yellow]{result.stderr}[/yellow]")
                return True
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
        else:
            self.console.print(f"[yellow]Unknown command: {text}[/yellow]")
        
        return False
    
    def start_listening(self):
        """Start continuous listening mode."""
        self.listening = True
        self.console.print("[cyan]🎤 Voice control active. Say 'stop listening' to exit.[/cyan]")
        
        while self.listening:
            text = self.listen_once()
            
            if text:
                self.console.print(f"[muted]Heard: {text}[/muted]")
                
                if "stop listening" in text or "exit" in text:
                    self.listening = False
                    self.console.print("[cyan]Voice control stopped.[/cyan]")
                    break
                
                self.execute_voice_command(text)
    
    def add_custom_command(self, voice_phrase: str, shell_command: str):
        """Add a custom voice command mapping."""
        self.VOICE_COMMANDS[voice_phrase.lower()] = shell_command


class SSHManager:
    """Manage SSH connections and keys."""
    
    def __init__(self):
        from pathlib import Path
        self.ssh_dir = Path.home() / ".ssh"
        self.config_file = self.ssh_dir / "config"
        self.connections = []
        self._load_config()
    
    def _load_config(self):
        """Load SSH config file."""
        if not self.config_file.exists():
            return
        
        current_host = None
        
        try:
            with open(self.config_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("Host "):
                        if current_host:
                            self.connections.append(current_host)
                        current_host = {"alias": line.split()[1]}
                    elif current_host and line:
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            current_host[parts[0].lower()] = parts[1]
                
                if current_host:
                    self.connections.append(current_host)
        except:
            pass
    
    def list_connections(self) -> List[Dict]:
        """List saved SSH connections."""
        return self.connections
    
    def add_connection(self, alias: str, hostname: str, user: str, 
                       port: int = 22, identity_file: str = None) -> bool:
        """Add a new SSH connection to config."""
        config_entry = f"""
Host {alias}
    HostName {hostname}
    User {user}
    Port {port}
"""
        if identity_file:
            config_entry += f"    IdentityFile {identity_file}\n"
        
        try:
            self.ssh_dir.mkdir(exist_ok=True)
            
            with open(self.config_file, "a") as f:
                f.write(config_entry)
            
            self.connections.append({
                "alias": alias,
                "hostname": hostname,
                "user": user,
                "port": str(port)
            })
            
            return True
        except:
            return False
    
    def connect(self, alias: str) -> str:
        """Generate SSH connect command."""
        return f"ssh {alias}"
    
    def generate_key(self, name: str = None, key_type: str = "ed25519") -> str:
        """Generate SSH key command."""
        key_name = name or "id_" + key_type
        return f"ssh-keygen -t {key_type} -f ~/.ssh/{key_name} -N ''"
    
    def copy_key(self, alias: str, key_file: str = None) -> str:
        """Generate ssh-copy-id command."""
        key_opt = f"-i {key_file}" if key_file else ""
        return f"ssh-copy-id {key_opt} {alias}"
    
    def list_keys(self) -> List[str]:
        """List available SSH keys."""
        keys = []
        for f in self.ssh_dir.glob("*"):
            if f.suffix == ".pub":
                keys.append(f.stem)
        return keys
    
    def tunnel(self, alias: str, local_port: int, remote_port: int) -> str:
        """Generate SSH tunnel command."""
        return f"ssh -L {local_port}:localhost:{remote_port} -N {alias}"


class AICodeReviewer:
    """AI-powered code review."""
    
    SYSTEM_PROMPT = """You are an expert code reviewer. Review the code changes and provide:
1. Summary of changes
2. Potential bugs or issues
3. Suggestions for improvement
4. Security concerns if any
5. Overall quality assessment

Be constructive and specific. Format your response with clear sections."""
    
    def __init__(self, engine=None):
        self.engine = engine
        self.console = Console()
    
    def get_git_diff(self, staged: bool = False) -> str:
        """Get git diff."""
        cmd = "git diff --staged" if staged else "git diff"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except:
            return ""
    
    def review_diff(self, diff: str) -> str:
        """Review a diff using AI."""
        if not diff:
            return "No changes to review."
        
        if self.engine:
            prompt = f"Review these code changes:\n\n```diff\n{diff[:8000]}\n```"
            return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
        
        # Fallback: basic analysis
        return self._basic_review(diff)
    
    def _basic_review(self, diff: str) -> str:
        """Basic static review without AI."""
        lines = diff.split("\n")
        
        additions = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
        deletions = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
        
        issues = []
        
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line:
                issues.append(f"Line {i}: Contains TODO/FIXME")
            if "console.log" in line or "print(" in line:
                issues.append(f"Line {i}: Debug statement found")
            if "password" in line.lower() or "secret" in line.lower():
                issues.append(f"Line {i}: Possible sensitive data")
        
        review = f"""## Code Review Summary

### Statistics
- Lines added: {additions}
- Lines removed: {deletions}
- Net change: {additions - deletions}

### Potential Issues
"""
        
        if issues:
            for issue in issues[:10]:
                review += f"- ⚠️ {issue}\n"
        else:
            review += "- ✅ No obvious issues detected\n"
        
        return review
    
    def review_file(self, filepath: str) -> str:
        """Review a single file."""
        from pathlib import Path
        
        path = Path(filepath)
        if not path.exists():
            return "File not found."
        
        content = path.read_text()[:10000]
        
        if self.engine:
            prompt = f"Review this code file ({path.name}):\n\n```\n{content}\n```"
            return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
        
        return self._basic_review(content)
    
    def review_current_changes(self) -> str:
        """Review current uncommitted changes."""
        diff = self.get_git_diff()
        return self.review_diff(diff)
    
    def review_staged_changes(self) -> str:
        """Review staged changes."""
        diff = self.get_git_diff(staged=True)
        return self.review_diff(diff)
