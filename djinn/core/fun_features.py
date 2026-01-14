"""
Fun & Productivity Features for DJINN v2.2.0
"""
import random
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import subprocess


class FortuneCookie:
    """AI-generated developer fortunes."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def generate_fortune(self) -> str:
        """Generate a dev-themed fortune."""
        prompt = """Generate a short, witty fortune cookie message for developers.
It should be inspirational, funny, or thought-provoking.
Keep it to 1-2 sentences.

Fortune:"""
        
        return self.engine.backend.generate(
            prompt,
            system_prompt="You are a wise fortune cookie writer for programmers."
        )


class PomodoroTimer:
    """Pomodoro technique timer with notifications."""
    
    def __init__(self, work_minutes: int = 25, break_minutes: int = 5):
        self.work_minutes = work_minutes
        self.break_minutes = break_minutes
    
    def start(self, sessions: int = 4):
        """Start pomodoro sessions."""
        from rich.console import Console
        from rich.progress import Progress
        
        console = Console()
        
        for session in range(sessions):
            console.print(f"\n[bold green]🍅 Session {session + 1}/{sessions} - WORK TIME![/bold green]")
            self._countdown(self.work_minutes * 60, "Work")
            
            if session < sessions - 1:
                console.print(f"\n[bold blue]☕ Break Time![/bold blue]")
                self._countdown(self.break_minutes * 60, "Break")
        
        console.print("\n[bold green]✨ All sessions complete! Great work![/bold green]")
    
    def _countdown(self, seconds: int, label: str):
        """Countdown timer."""
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.console import Console
        
        console = Console()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"{label}: {seconds}s remaining", total=seconds)
            
            for i in range(seconds):
                time.sleep(1)
                progress.update(task, advance=1, description=f"{label}: {seconds -i - 1}s remaining")
        
        # Notification
        self._notify(f"{label} complete!")
    
    def _notify(self, message: str):
        """Send system notification."""
        try:
            if sys.platform == "win32":
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast("DJINN Pomodoro", message, duration=5)
            elif sys.platform == "darwin":
                subprocess.run(["osascript", "-e", f'display notification "{message}" with title "DJINN"'])
            else:  # Linux
                subprocess.run(["notify-send", "DJINN", message])
        except:
            pass


class WeatherFetcher:
    """ASCII weather report."""
    
    @staticmethod
    def get_weather(city: str = None) -> str:
        """Get weather report."""
        import requests
        
        if not city:
            # Auto-detect location
            try:
                location = requests.get('https://ipapi.co/json/', timeout=3).json()
                city = location.get('city', 'London')
            except:
                city = "London"
        
        try:
            # Use wttr.in for ASCII weather
            response = requests.get(f'https://wttr.in/{city}?format=3', timeout=5)
            return response.text
        except:
            return "Could not fetch weather"


class NewsReader:
    """HackerNews top stories reader."""
    
    @staticmethod
    def get_top_stories(limit: int = 10) -> List[Dict]:
        """Fetch top HackerNews stories."""
        import requests
        
        try:
            # Get top story IDs
            top_ids = requests.get(
                'https://hacker-news.firebaseio.com/v0/topstories.json'
            ).json()
            
            stories = []
            for story_id in top_ids[:limit]:
                story = requests.get(
                    f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                ).json()
                
                stories.append({
                    'title': story.get('title'),
                    'url': story.get('url', 'https://news.ycombinator.com'),
                    'score': story.get('score', 0),
                    'by': story.get('by', 'unknown')
                })
            
            return stories
        except:
            return []


class PasswordGenerator:
    """High-entropy password generator."""
    
    @staticmethod
    def generate(length: int = 16, include_symbols: bool = True) -> str:
        """Generate secure password."""
        import string
        import secrets
        
        chars = string.ascii_letters + string.digits
        if include_symbols:
            chars += string.punctuation
        
        password = ''.join(secrets.choice(chars) for _ in range(length))
        return password


class TimeTracker:
    """Track time spent in terminal."""
    
    def __init__(self):
        self.log_file = Path.home() / ".djinn" / "time_log.json"
        self.log_file.parent.mkdir(exist_ok=True)
        self.start_time = datetime.now()
    
    def log_session(self):
        """Log current session time."""
        import json
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        logs = []
        if self.log_file.exists():
            with open(self.log_file) as f:
                logs = json.load(f)
        
        logs.append({
            "date": str(datetime.now().date()),
            "duration_seconds": duration,
            "start": str(self.start_time),
            "end": str(datetime.now())
        })
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get time tracking statistics."""
        import json
        
        if not self.log_file.exists():
            return {"total_hours": 0, "today_hours": 0}
        
        with open(self.log_file) as f:
            logs = json.load(f)
        
        total_seconds = sum(log['duration_seconds'] for log in logs)
        today = str(datetime.now().date())
        today_seconds = sum(
            log['duration_seconds'] for log in logs 
            if log['date'] == today
        )
        
        return {
            "total_hours": round(total_seconds / 3600, 2),
            "today_hours": round(today_seconds / 3600, 2),
            "sessions": len(logs)
        }


class ProductivityScore:
    """Gamified developer productivity stats."""
    
    def __init__(self):
        self.score_file = Path.home() / ".djinn" / "productivity.json"
        self.score_file.parent.mkdir(exist_ok=True)
    
    def calculate_score(self) -> Dict:
        """Calculate productivity score."""
        from djinn.core import StatsManager, HistoryManager
        
        stats = StatsManager()
        history = HistoryManager()
        
        summary = stats.get_summary()
        hist_stats = history.get_stats()
        
        # Calculate score (arbitrary formula)
        commands_score = min(summary.get('total', 0) * 2, 1000)
        success_score = summary.get('success_rate', 0) * 5
        favorites_score = hist_stats.get('favorites', 0) * 10
        
        total_score = commands_score + success_score + favorites_score
        
        # Determine rank
        if total_score < 100:
            rank = "Novice Sorcerer"
            next_rank = "Apprentice"
            next_rank_score = 100
        elif total_score < 500:
            rank = "Apprentice"
            next_rank = "Wizarduser"
            next_rank_score = 500
        elif total_score < 1000:
            rank = "Wizard"
            next_rank = "Archmage"
            next_rank_score = 1000
        else:
            rank = "Archmage"
            next_rank = "Legendary"
            next_rank_score = total_score
        
        return {
            "score": int(total_score),
            "rank": rank,
            "next_rank": next_rank,
            "progress_to_next": min(100, int((total_score / next_rank_score) * 100))
        }
