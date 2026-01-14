"""
Firebase Plugin for DJINN
Firebase project management, deploy, hosting, Firestore.
"""
import click
from rich.console import Console
from rich.table import Table
import subprocess
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "firebase"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Firebase hosting, Firestore, and project management."


def run_firebase_cmd(args, capture=True):
    """Run Firebase CLI command."""
    cmd = ["firebase"] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        else:
            subprocess.run(cmd)
            return True, ""
    except FileNotFoundError:
        return False, "Firebase CLI not installed. Run: npm i -g firebase-tools"


@click.group()
def firebase():
    """Firebase commands."""
    pass


@firebase.command(name="init")
@click.option("--hosting", is_flag=True, help="Initialize hosting")
@click.option("--firestore", is_flag=True, help="Initialize Firestore")
@click.option("--functions", is_flag=True, help="Initialize Functions")
def init_project(hosting, firestore, functions):
    """Initialize Firebase in current directory."""
    args = ["init"]
    
    features = []
    if hosting:
        features.append("hosting")
    if firestore:
        features.append("firestore")
    if functions:
        features.append("functions")
    
    if features:
        args.extend(["--only", ",".join(features)])
    
    console.print("\n[bold cyan]🔥 Initializing Firebase...[/bold cyan]\n")
    run_firebase_cmd(args, capture=False)


@firebase.command(name="deploy")
@click.option("--only", "only_services", help="Deploy specific services (hosting,functions)")
@click.option("--message", "-m", help="Deploy message")
def deploy(only_services, message):
    """Deploy to Firebase."""
    args = ["deploy"]
    
    if only_services:
        args.extend(["--only", only_services])
    if message:
        args.extend(["--message", message])
    
    console.print("\n[bold cyan]🚀 Deploying to Firebase...[/bold cyan]\n")
    run_firebase_cmd(args, capture=False)


@firebase.command(name="serve")
@click.option("--only", "only_services", help="Serve specific services")
@click.option("--port", default=5000, type=int)
def serve_local(only_services, port):
    """Start local Firebase emulator."""
    args = ["serve", "--port", str(port)]
    
    if only_services:
        args.extend(["--only", only_services])
    
    console.print(f"\n[bold cyan]🔥 Starting Firebase on http://localhost:{port}[/bold cyan]\n")
    run_firebase_cmd(args, capture=False)


@firebase.command(name="projects")
def list_projects():
    """List Firebase projects."""
    console.print("\n[bold cyan]📋 Firebase Projects[/bold cyan]\n")
    
    success, output = run_firebase_cmd(["projects:list"])
    
    if success:
        console.print(output)
    else:
        console.print(f"[error]{output}[/error]")


@firebase.command(name="use")
@click.argument("project_id")
def use_project(project_id):
    """Switch to a Firebase project."""
    success, output = run_firebase_cmd(["use", project_id])
    
    if success:
        console.print(f"[success]✓ Now using project: {project_id}[/success]")
    else:
        console.print(f"[error]{output}[/error]")


@firebase.command(name="hosting")
@click.argument("action", type=click.Choice(["channel", "disable", "sites"]))
@click.argument("args", nargs=-1)
def hosting_commands(action, args):
    """Firebase Hosting commands."""
    if action == "channel":
        # Create preview channel
        channel_id = args[0] if args else "preview"
        console.print(f"\n[bold cyan]🔗 Creating preview channel: {channel_id}[/bold cyan]\n")
        
        success, output = run_firebase_cmd(["hosting:channel:deploy", channel_id])
        
        if success:
            # Extract URL from output
            console.print(output)
        else:
            console.print(f"[error]{output}[/error]")
    
    elif action == "disable":
        console.print("\n[bold yellow]⚠️  Disabling Firebase Hosting[/bold yellow]\n")
        run_firebase_cmd(["hosting:disable"], capture=False)
    
    elif action == "sites":
        console.print("\n[bold cyan]🌐 Hosting Sites[/bold cyan]\n")
        run_firebase_cmd(["hosting:sites:list"], capture=False)


@firebase.command(name="functions")
@click.argument("action", type=click.Choice(["log", "delete", "shell"]))
@click.argument("function_name", required=False)
def functions_commands(action, function_name):
    """Firebase Functions commands."""
    if action == "log":
        console.print("\n[bold cyan]📜 Function Logs[/bold cyan]\n")
        args = ["functions:log"]
        if function_name:
            args.extend(["--only", function_name])
        run_firebase_cmd(args, capture=False)
    
    elif action == "delete":
        if not function_name:
            console.print("[error]Function name required[/error]")
            return
        
        console.print(f"\n[bold red]🗑️  Deleting function: {function_name}[/bold red]\n")
        run_firebase_cmd(["functions:delete", function_name, "--force"], capture=False)
    
    elif action == "shell":
        console.print("\n[bold cyan]🐚 Starting Functions Shell[/bold cyan]\n")
        run_firebase_cmd(["functions:shell"], capture=False)


@firebase.command(name="firestore")
@click.argument("action", type=click.Choice(["indexes", "delete"]))
@click.argument("args", nargs=-1)
def firestore_commands(action, args):
    """Firestore commands."""
    if action == "indexes":
        console.print("\n[bold cyan]📊 Firestore Indexes[/bold cyan]\n")
        run_firebase_cmd(["firestore:indexes"], capture=False)
    
    elif action == "delete":
        if not args:
            console.print("[error]Collection path required[/error]")
            return
        
        collection_path = args[0]
        console.print(f"\n[bold red]🗑️  Deleting collection: {collection_path}[/bold red]\n")
        run_firebase_cmd(["firestore:delete", collection_path, "--recursive", "--force"], capture=False)


@firebase.command(name="auth")
@click.argument("action", type=click.Choice(["export", "import"]))
@click.argument("file_path", required=False)
def auth_commands(action, file_path):
    """Firebase Auth commands."""
    if action == "export":
        file_path = file_path or "users.json"
        console.print(f"\n[bold cyan]📤 Exporting users to {file_path}[/bold cyan]\n")
        run_firebase_cmd(["auth:export", file_path], capture=False)
    
    elif action == "import":
        if not file_path:
            console.print("[error]File path required[/error]")
            return
        
        console.print(f"\n[bold cyan]📥 Importing users from {file_path}[/bold cyan]\n")
        run_firebase_cmd(["auth:import", file_path], capture=False)


main = firebase

if __name__ == "__main__":
    firebase()
