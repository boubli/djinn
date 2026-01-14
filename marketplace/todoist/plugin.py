"""
Todoist Plugin for DJINN
Task management from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
from pathlib import Path
from datetime import datetime

console = Console()

PLUGIN_NAME = "todoist"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Manage Todoist tasks from terminal."


def get_todoist_client():
    """Get Todoist client."""
    try:
        from todoist_api_python import TodoistAPI
        
        token = os.environ.get("TODOIST_TOKEN")
        if not token:
            config_file = Path.home() / ".djinn" / "todoist.json"
            if config_file.exists():
                with open(config_file) as f:
                    token = json.load(f).get("token")
        
        if not token:
            console.print("[error]TODOIST_TOKEN not set[/error]")
            console.print("[muted]Set with: djinn todoist auth YOUR_TOKEN[/muted]")
            return None
        
        return TodoistAPI(token)
    except ImportError:
        console.print("[error]todoist-api-python not installed. Run: pip install todoist-api-python[/error]")
        return None


@click.group()
def todoist():
    """Todoist commands."""
    pass


@todoist.command(name="auth")
@click.argument("token")
def set_auth(token):
    """Save Todoist API token."""
    config_file = Path.home() / ".djinn" / "todoist.json"
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump({"token": token}, f)
    
    console.print("[success]✓ Todoist token saved![/success]")


@todoist.command(name="tasks")
@click.option("--project", help="Filter by project name")
@click.option("--today", is_flag=True, help="Show today's tasks")
def list_tasks(project, today):
    """List tasks."""
    api = get_todoist_client()
    if not api:
        return
    
    console.print("\n[bold cyan]📋 Tasks[/bold cyan]\n")
    
    try:
        if today:
            tasks = api.get_tasks(filter="today")
        elif project:
            projects = api.get_projects()
            proj_id = next((p.id for p in projects if p.name.lower() == project.lower()), None)
            if proj_id:
                tasks = api.get_tasks(project_id=proj_id)
            else:
                console.print(f"[error]Project '{project}' not found[/error]")
                return
        else:
            tasks = api.get_tasks()
        
        table = Table()
        table.add_column("", width=3)
        table.add_column("Task")
        table.add_column("Due")
        table.add_column("Priority")
        
        priority_colors = {1: "white", 2: "blue", 3: "yellow", 4: "red"}
        
        for task in tasks[:25]:
            priority = task.priority
            color = priority_colors.get(priority, "white")
            
            due = ""
            if task.due:
                due = task.due.string
            
            table.add_row(
                "○",
                task.content,
                due,
                f"[{color}]P{5-priority}[/{color}]"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@todoist.command(name="add")
@click.argument("content")
@click.option("--project", help="Project name")
@click.option("--due", help="Due date (e.g., 'today', 'tomorrow', '2024-12-25')")
@click.option("--priority", type=click.Choice(["1", "2", "3", "4"]), default="1")
def add_task(content, project, due, priority):
    """Add a new task."""
    api = get_todoist_client()
    if not api:
        return
    
    try:
        params = {"content": content, "priority": int(priority)}
        
        if project:
            projects = api.get_projects()
            proj_id = next((p.id for p in projects if p.name.lower() == project.lower()), None)
            if proj_id:
                params["project_id"] = proj_id
        
        if due:
            params["due_string"] = due
        
        task = api.add_task(**params)
        
        console.print(f"[success]✓ Task added: {content}[/success]")
        console.print(f"[muted]ID: {task.id}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@todoist.command(name="complete")
@click.argument("task_id")
def complete_task(task_id):
    """Mark task as complete."""
    api = get_todoist_client()
    if not api:
        return
    
    try:
        api.close_task(task_id)
        console.print(f"[success]✓ Task completed![/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@todoist.command(name="projects")
def list_projects():
    """List projects."""
    api = get_todoist_client()
    if not api:
        return
    
    console.print("\n[bold cyan]📁 Projects[/bold cyan]\n")
    
    try:
        projects = api.get_projects()
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("ID")
        
        for project in projects:
            table.add_row(project.name, project.id)
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@todoist.command(name="quick")
@click.argument("text")
def quick_add(text):
    """Quick add task with natural language."""
    api = get_todoist_client()
    if not api:
        return
    
    try:
        # Todoist's quick add parses natural language
        task = api.add_task(content=text)
        console.print(f"[success]✓ Task added: {task.content}[/success]")
        
        if task.due:
            console.print(f"[muted]Due: {task.due.string}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = todoist

if __name__ == "__main__":
    todoist()
