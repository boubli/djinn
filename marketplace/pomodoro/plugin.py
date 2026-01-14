"""
Pomodoro Timer Plugin for DJINN
Focus timer with notifications.
"""
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
import time
from datetime import datetime, timedelta
from pathlib import Path
import json

console = Console()

PLUGIN_NAME = "pomodoro"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Pomodoro timer for productivity."

STATS_FILE = Path.home() / ".djinn" / "pomodoro_stats.json"


def load_stats():
    """Load timer statistics."""
    if STATS_FILE.exists():
        with open(STATS_FILE) as f:
            return json.load(f)
    return {"sessions": [], "total_focus_minutes": 0}


def save_stats(stats):
    """Save timer statistics."""
    STATS_FILE.parent.mkdir(exist_ok=True)
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)


def send_notification(title, message):
    """Send system notification."""
    try:
        # Windows
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5, threaded=True)
    except:
        try:
            # Cross-platform fallback
            import subprocess
            if Path("/usr/bin/notify-send").exists():
                subprocess.run(["notify-send", title, message])
            else:
                # Just bell
                print("\a")
        except:
            print("\a")


def play_sound():
    """Play completion sound."""
    try:
        import winsound
        winsound.Beep(800, 500)
    except:
        print("\a")


@click.group()
def pomodoro():
    """Pomodoro timer commands."""
    pass


@pomodoro.command(name="start")
@click.option("--work", "-w", default=25, type=int, help="Work duration in minutes")
@click.option("--break", "break_time", "-b", default=5, type=int, help="Break duration in minutes")
@click.option("--long-break", "-l", default=15, type=int, help="Long break duration")
@click.option("--sessions", "-s", default=4, type=int, help="Sessions before long break")
@click.option("--task", "-t", help="Task description")
def start_timer(work, break_time, long_break, sessions, task):
    """Start pomodoro session."""
    console.print("\n[bold cyan]🍅 Pomodoro Timer[/bold cyan]\n")
    
    if task:
        console.print(f"[muted]Task:[/muted] {task}")
    
    console.print(f"[muted]Work: {work}min | Break: {break_time}min | Long Break: {long_break}min[/muted]")
    console.print("[muted]Press Ctrl+C to stop[/muted]\n")
    
    session_count = 0
    stats = load_stats()
    
    try:
        while True:
            session_count += 1
            
            # Work session
            console.print(f"[bold green]🔥 Session {session_count} - FOCUS[/bold green]")
            _run_timer(work * 60, "Work")
            
            # Record session
            stats["sessions"].append({
                "date": datetime.now().isoformat(),
                "duration": work,
                "task": task
            })
            stats["total_focus_minutes"] += work
            save_stats(stats)
            
            play_sound()
            send_notification("Pomodoro Complete!", f"Session {session_count} done. Take a break!")
            
            # Break
            if session_count % sessions == 0:
                console.print(f"\n[bold blue]☕ LONG BREAK ({long_break} min)[/bold blue]")
                _run_timer(long_break * 60, "Long Break")
            else:
                console.print(f"\n[bold blue]☕ SHORT BREAK ({break_time} min)[/bold blue]")
                _run_timer(break_time * 60, "Break")
            
            play_sound()
            send_notification("Break Over!", "Ready for the next session?")
            
            console.print()
    except KeyboardInterrupt:
        console.print(f"\n\n[muted]Stopped after {session_count} session(s)[/muted]")
        console.print(f"[success]Total focus time: {session_count * work} minutes[/success]")


def _run_timer(seconds, label):
    """Run countdown timer."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]{label}", total=seconds)
        
        while not progress.finished:
            time.sleep(1)
            progress.update(task, advance=1)


@pomodoro.command(name="quick")
@click.argument("minutes", type=int)
@click.option("--task", "-t", help="Task description")
def quick_timer(minutes, task):
    """Quick timer for custom duration."""
    console.print(f"\n[bold cyan]⏱️  {minutes} Minute Timer[/bold cyan]\n")
    
    if task:
        console.print(f"[muted]Task:[/muted] {task}")
    
    console.print("[muted]Press Ctrl+C to cancel[/muted]\n")
    
    try:
        _run_timer(minutes * 60, f"{minutes} min")
        
        play_sound()
        send_notification("Timer Complete!", f"{minutes} minute timer finished")
        
        console.print("\n[success]✓ Timer complete![/success]")
        
        # Save to stats
        stats = load_stats()
        stats["sessions"].append({
            "date": datetime.now().isoformat(),
            "duration": minutes,
            "task": task,
            "type": "quick"
        })
        stats["total_focus_minutes"] += minutes
        save_stats(stats)
    except KeyboardInterrupt:
        console.print("\n[muted]Timer cancelled[/muted]")


@pomodoro.command(name="stats")
@click.option("--today", is_flag=True, help="Show today's stats")
@click.option("--week", is_flag=True, help="Show this week's stats")
def show_stats(today, week):
    """Show timer statistics."""
    stats = load_stats()
    
    console.print("\n[bold cyan]📊 Pomodoro Statistics[/bold cyan]\n")
    
    sessions = stats.get("sessions", [])
    
    if today:
        today_date = datetime.now().date().isoformat()
        sessions = [s for s in sessions if s["date"].startswith(today_date)]
        label = "Today"
    elif week:
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        sessions = [s for s in sessions if s["date"] > week_ago]
        label = "This Week"
    else:
        label = "All Time"
    
    total_minutes = sum(s.get("duration", 0) for s in sessions)
    total_hours = total_minutes / 60
    
    console.print(f"[bold]{label}[/bold]")
    console.print(f"  Sessions: {len(sessions)}")
    console.print(f"  Focus Time: {total_minutes} minutes ({total_hours:.1f} hours)")
    
    if sessions:
        console.print(f"\n[bold]Recent Sessions:[/bold]")
        for session in sessions[-10:]:
            date = session["date"][:10]
            duration = session.get("duration", 0)
            task = session.get("task", "-")
            console.print(f"  {date} | {duration} min | {task}")


@pomodoro.command(name="reset")
@click.option("--confirm", is_flag=True, help="Confirm reset")
def reset_stats(confirm):
    """Reset all statistics."""
    if not confirm:
        console.print("[error]Use --confirm to reset statistics[/error]")
        return
    
    if STATS_FILE.exists():
        STATS_FILE.unlink()
    
    console.print("[success]✓ Statistics reset[/success]")


@pomodoro.command(name="reminder")
@click.argument("message")
@click.argument("minutes", type=int)
def set_reminder(message, minutes):
    """Set a reminder."""
    console.print(f"[muted]Reminder set for {minutes} minutes...[/muted]")
    
    try:
        time.sleep(minutes * 60)
        
        play_sound()
        send_notification("Reminder", message)
        
        console.print(f"\n[success]🔔 {message}[/success]")
    except KeyboardInterrupt:
        console.print("\n[muted]Reminder cancelled[/muted]")


main = pomodoro

if __name__ == "__main__":
    pomodoro()
