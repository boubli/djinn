"""
Terminal Recorder - Record terminal sessions.
"""
import os
import time
import json
from typing import Optional
from pathlib import Path
from datetime import datetime


class TerminalRecorder:
    """Record and playback terminal sessions."""
    
    def __init__(self):
        self.djinn_dir = Path.home() / ".djinn"
        self.recordings_dir = self.djinn_dir / "recordings"
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.current_recording = None
    
    def start(self, name: str = None) -> str:
        """Start a new recording session."""
        if name is None:
            name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        
        self.current_recording = {
            "name": name,
            "started": datetime.now().isoformat(),
            "commands": [],
        }
        
        return name
    
    def record_command(self, command: str, output: str = "", returncode: int = 0):
        """Record a command and its output."""
        if self.current_recording is None:
            return
        
        self.current_recording["commands"].append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "output": output[:5000],  # Limit output size
            "returncode": returncode,
        })
    
    def stop(self) -> Optional[str]:
        """Stop recording and save."""
        if self.current_recording is None:
            return None
        
        self.current_recording["ended"] = datetime.now().isoformat()
        
        filepath = self.recordings_dir / f"{self.current_recording['name']}.json"
        with open(filepath, "w") as f:
            json.dump(self.current_recording, f, indent=2)
        
        name = self.current_recording["name"]
        self.current_recording = None
        
        return str(filepath)
    
    def list_recordings(self) -> list:
        """List all recordings."""
        recordings = []
        for f in self.recordings_dir.glob("*.json"):
            try:
                with open(f) as file:
                    data = json.load(file)
                    recordings.append({
                        "name": f.stem,
                        "started": data.get("started", ""),
                        "commands": len(data.get("commands", [])),
                    })
            except:
                pass
        return recordings
    
    def get_recording(self, name: str) -> Optional[dict]:
        """Get a recording by name."""
        filepath = self.recordings_dir / f"{name}.json"
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return None
    
    def delete_recording(self, name: str) -> bool:
        """Delete a recording."""
        filepath = self.recordings_dir / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def export_to_script(self, name: str) -> Optional[str]:
        """Export recording to a shell script."""
        recording = self.get_recording(name)
        if not recording:
            return None
        
        script_lines = ["#!/bin/bash", f"# DJINN Recording: {name}", ""]
        
        for cmd in recording.get("commands", []):
            script_lines.append(f"# {cmd['timestamp']}")
            script_lines.append(cmd["command"])
            script_lines.append("")
        
        script_path = self.recordings_dir / f"{name}.sh"
        with open(script_path, "w") as f:
            f.write("\n".join(script_lines))
        
        return str(script_path)
    
    def export_to_markdown(self, name: str) -> Optional[str]:
        """Export recording to markdown."""
        recording = self.get_recording(name)
        if not recording:
            return None
        
        lines = [
            f"# Terminal Session: {name}",
            f"**Started:** {recording.get('started', '')}",
            f"**Ended:** {recording.get('ended', '')}",
            "",
            "## Commands",
            "",
        ]
        
        for i, cmd in enumerate(recording.get("commands", []), 1):
            lines.append(f"### {i}. {cmd['command']}")
            if cmd.get("output"):
                lines.append("```")
                lines.append(cmd["output"][:500])
                lines.append("```")
            lines.append("")
        
        md_path = self.recordings_dir / f"{name}.md"
        with open(md_path, "w") as f:
            f.write("\n".join(lines))
        
        return str(md_path)


class GistManager:
    """Share commands as GitHub Gists."""
    
    def __init__(self, token: str = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
    
    def create_gist(self, content: str, filename: str = "commands.sh", 
                    description: str = "Shared via DJINN", public: bool = False) -> Optional[str]:
        """Create a GitHub Gist."""
        if not self.token:
            return None
        
        import requests
        
        data = {
            "description": description,
            "public": public,
            "files": {
                filename: {"content": content}
            }
        }
        
        try:
            response = requests.post(
                "https://api.github.com/gists",
                json=data,
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if response.status_code == 201:
                return response.json().get("html_url")
        except:
            pass
        
        return None
    
    def share_command(self, command: str, description: str = None) -> Optional[str]:
        """Share a single command as a Gist."""
        desc = description or f"DJINN: {command[:50]}"
        return self.create_gist(command, "command.sh", desc)
    
    def share_script(self, script: str, name: str = "script.sh") -> Optional[str]:
        """Share a script as a Gist."""
        return self.create_gist(script, name, f"DJINN Script: {name}")
