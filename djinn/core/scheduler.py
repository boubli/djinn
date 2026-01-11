"""
Scheduler - Schedule commands to run at specific times.
"""
import json
import subprocess
import sys
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta


class Scheduler:
    """Schedule commands to run at specific times."""
    
    def __init__(self):
        self.djinn_dir = Path.home() / ".djinn"
        self.schedule_file = self.djinn_dir / "schedule.json"
        self.djinn_dir.mkdir(exist_ok=True)
    
    def _load_schedule(self) -> List[Dict]:
        """Load scheduled tasks."""
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file) as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_schedule(self, schedule: List[Dict]):
        """Save scheduled tasks."""
        with open(self.schedule_file, "w") as f:
            json.dump(schedule, f, indent=2)
    
    def add(self, command: str, run_at: str, name: str = None, repeat: str = None) -> Dict:
        """Add a scheduled task.
        
        Args:
            command: The command to run
            run_at: When to run (ISO format or relative like "+1h", "+30m")
            name: Optional name for the task
            repeat: Optional repeat interval ("hourly", "daily", "weekly")
        """
        schedule = self._load_schedule()
        
        # Parse run_at
        if run_at.startswith("+"):
            # Relative time
            run_at_dt = self._parse_relative(run_at)
        else:
            run_at_dt = datetime.fromisoformat(run_at)
        
        task = {
            "id": len(schedule) + 1,
            "name": name or f"Task {len(schedule) + 1}",
            "command": command,
            "run_at": run_at_dt.isoformat(),
            "repeat": repeat,
            "created": datetime.now().isoformat(),
            "status": "pending",
        }
        
        schedule.append(task)
        self._save_schedule(schedule)
        
        return task
    
    def _parse_relative(self, relative: str) -> datetime:
        """Parse relative time like +1h, +30m, +1d."""
        now = datetime.now()
        
        if relative.endswith("m"):
            minutes = int(relative[1:-1])
            return now + timedelta(minutes=minutes)
        elif relative.endswith("h"):
            hours = int(relative[1:-1])
            return now + timedelta(hours=hours)
        elif relative.endswith("d"):
            days = int(relative[1:-1])
            return now + timedelta(days=days)
        
        return now + timedelta(hours=1)
    
    def list_all(self) -> List[Dict]:
        """List all scheduled tasks."""
        return self._load_schedule()
    
    def list_pending(self) -> List[Dict]:
        """List pending tasks."""
        schedule = self._load_schedule()
        return [t for t in schedule if t["status"] == "pending"]
    
    def cancel(self, task_id: int) -> bool:
        """Cancel a scheduled task."""
        schedule = self._load_schedule()
        for task in schedule:
            if task["id"] == task_id:
                task["status"] = "cancelled"
                self._save_schedule(schedule)
                return True
        return False
    
    def run_due(self) -> List[Dict]:
        """Run all due tasks."""
        schedule = self._load_schedule()
        now = datetime.now()
        results = []
        
        for task in schedule:
            if task["status"] != "pending":
                continue
            
            run_at = datetime.fromisoformat(task["run_at"])
            if run_at <= now:
                # Run the task
                try:
                    result = subprocess.run(
                        task["command"],
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    task["status"] = "completed"
                    task["result"] = {
                        "returncode": result.returncode,
                        "stdout": result.stdout[-500:],
                        "stderr": result.stderr[-500:],
                        "ran_at": datetime.now().isoformat(),
                    }
                except Exception as e:
                    task["status"] = "failed"
                    task["result"] = {"error": str(e)}
                
                # Handle repeat
                if task.get("repeat"):
                    new_task = task.copy()
                    new_task["id"] = len(schedule) + 1
                    new_task["status"] = "pending"
                    
                    if task["repeat"] == "hourly":
                        new_task["run_at"] = (run_at + timedelta(hours=1)).isoformat()
                    elif task["repeat"] == "daily":
                        new_task["run_at"] = (run_at + timedelta(days=1)).isoformat()
                    elif task["repeat"] == "weekly":
                        new_task["run_at"] = (run_at + timedelta(weeks=1)).isoformat()
                    
                    schedule.append(new_task)
                
                results.append(task)
        
        self._save_schedule(schedule)
        return results
    
    def generate_cron(self, command: str, schedule_str: str) -> str:
        """Generate cron entry for a command."""
        cron_map = {
            "every minute": "* * * * *",
            "hourly": "0 * * * *",
            "daily": "0 0 * * *",
            "weekly": "0 0 * * 0",
            "monthly": "0 0 1 * *",
            "weekdays": "0 9 * * 1-5",
        }
        
        cron_time = cron_map.get(schedule_str.lower(), "0 * * * *")
        return f"{cron_time} {command}"


class FileWatcher:
    """Watch files and trigger commands on changes."""
    
    def __init__(self):
        self.watches = {}
    
    def add_watch(self, path: str, command: str, event: str = "modify"):
        """Add a file watch.
        
        Args:
            path: File or directory to watch
            command: Command to run on change
            event: Event type (modify, create, delete)
        """
        self.watches[path] = {
            "command": command,
            "event": event,
            "last_modified": self._get_mtime(path),
        }
    
    def _get_mtime(self, path: str) -> float:
        """Get file modification time."""
        p = Path(path)
        if p.exists():
            return p.stat().st_mtime
        return 0
    
    def check_changes(self) -> List[Dict]:
        """Check for file changes and run commands."""
        triggered = []
        
        for path, watch in self.watches.items():
            current_mtime = self._get_mtime(path)
            if current_mtime > watch["last_modified"]:
                # File changed
                watch["last_modified"] = current_mtime
                
                try:
                    result = subprocess.run(
                        watch["command"],
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    triggered.append({
                        "path": path,
                        "command": watch["command"],
                        "success": result.returncode == 0,
                    })
                except:
                    pass
        
        return triggered
    
    def generate_watch_command(self, path: str, command: str) -> str:
        """Generate a watch command for different systems."""
        # Using entr if available
        return f"echo {path} | entr -c {command}"
