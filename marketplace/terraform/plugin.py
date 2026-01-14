"""
Terraform Plugin for DJINN
Terraform infrastructure management.
"""
import click
from rich.console import Console
from rich.syntax import Syntax
import subprocess
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "terraform"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Terraform infrastructure as code management."


def run_tf(args, capture=True):
    """Run terraform command."""
    cmd = ["terraform"] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        else:
            subprocess.run(cmd)
            return True, ""
    except FileNotFoundError:
        return False, "Terraform not installed. See: https://terraform.io/downloads"


@click.group()
def tf():
    """Terraform commands."""
    pass


@tf.command(name="init")
@click.option("--upgrade", is_flag=True, help="Upgrade providers")
def tf_init(upgrade):
    """Initialize Terraform."""
    console.print("\n[bold cyan]🔧 Initializing Terraform...[/bold cyan]\n")
    
    args = ["init"]
    if upgrade:
        args.append("-upgrade")
    
    run_tf(args, capture=False)


@tf.command(name="plan")
@click.option("--out", "plan_file", help="Save plan to file")
@click.option("--var", multiple=True, help="Variables")
def tf_plan(plan_file, var):
    """Show execution plan."""
    console.print("\n[bold cyan]📋 Planning...[/bold cyan]\n")
    
    args = ["plan"]
    if plan_file:
        args.extend(["-out", plan_file])
    for v in var:
        args.extend(["-var", v])
    
    run_tf(args, capture=False)


@tf.command(name="apply")
@click.option("--auto-approve", is_flag=True, help="Skip approval")
@click.option("--plan", "plan_file", help="Apply saved plan")
@click.option("--var", multiple=True, help="Variables")
def tf_apply(auto_approve, plan_file, var):
    """Apply changes."""
    console.print("\n[bold cyan]🚀 Applying...[/bold cyan]\n")
    
    args = ["apply"]
    if auto_approve:
        args.append("-auto-approve")
    if plan_file:
        args.append(plan_file)
    for v in var:
        args.extend(["-var", v])
    
    run_tf(args, capture=False)


@tf.command(name="destroy")
@click.option("--auto-approve", is_flag=True, help="Skip approval")
def tf_destroy(auto_approve):
    """Destroy infrastructure."""
    console.print("\n[bold red]💀 Destroying...[/bold red]\n")
    
    args = ["destroy"]
    if auto_approve:
        args.append("-auto-approve")
    
    run_tf(args, capture=False)


@tf.command(name="state")
@click.argument("action", type=click.Choice(["list", "show", "rm", "mv"]))
@click.argument("args", nargs=-1)
def tf_state(action, args):
    """Manage state."""
    if action == "list":
        console.print("\n[bold cyan]📦 Resources[/bold cyan]\n")
        run_tf(["state", "list"], capture=False)
    
    elif action == "show":
        if not args:
            console.print("[error]Resource address required[/error]")
            return
        run_tf(["state", "show", args[0]], capture=False)
    
    elif action == "rm":
        if not args:
            console.print("[error]Resource address required[/error]")
            return
        run_tf(["state", "rm", args[0]], capture=False)
    
    elif action == "mv":
        if len(args) < 2:
            console.print("[error]Source and destination required[/error]")
            return
        run_tf(["state", "mv", args[0], args[1]], capture=False)


@tf.command(name="output")
@click.argument("name", required=False)
@click.option("--json", "as_json", is_flag=True)
def tf_output(name, as_json):
    """Show outputs."""
    args = ["output"]
    if as_json:
        args.append("-json")
    if name:
        args.append(name)
    
    success, output = run_tf(args)
    
    if success:
        if as_json:
            try:
                data = json.loads(output)
                formatted = json.dumps(data, indent=2)
                syntax = Syntax(formatted, "json", theme="monokai")
                console.print(syntax)
            except:
                console.print(output)
        else:
            console.print(output)
    else:
        console.print(f"[error]{output}[/error]")


@tf.command(name="fmt")
@click.option("--check", is_flag=True, help="Check if formatted")
def tf_fmt(check):
    """Format Terraform files."""
    args = ["fmt"]
    if check:
        args.append("-check")
    
    success, output = run_tf(args)
    
    if success:
        if output:
            console.print("[muted]Formatted files:[/muted]")
            console.print(output)
        else:
            console.print("[success]✓ All files formatted[/success]")
    else:
        console.print(f"[warning]Files need formatting[/warning]")


@tf.command(name="validate")
def tf_validate():
    """Validate configuration."""
    success, output = run_tf(["validate", "-json"])
    
    try:
        data = json.loads(output)
        
        if data.get("valid"):
            console.print("[success]✓ Configuration is valid[/success]")
        else:
            console.print("[error]✗ Configuration is invalid[/error]")
            
            for diag in data.get("diagnostics", []):
                severity = diag.get("severity", "error")
                summary = diag.get("summary", "")
                color = "error" if severity == "error" else "warning"
                console.print(f"[{color}]{summary}[/{color}]")
    except:
        console.print(output)


@tf.command(name="workspace")
@click.argument("action", type=click.Choice(["list", "select", "new", "delete"]))
@click.argument("name", required=False)
def tf_workspace(action, name):
    """Manage workspaces."""
    if action == "list":
        run_tf(["workspace", "list"], capture=False)
    
    elif action == "select":
        if not name:
            console.print("[error]Workspace name required[/error]")
            return
        success, output = run_tf(["workspace", "select", name])
        if success:
            console.print(f"[success]✓ Switched to workspace: {name}[/success]")
        else:
            console.print(f"[error]{output}[/error]")
    
    elif action == "new":
        if not name:
            console.print("[error]Workspace name required[/error]")
            return
        success, output = run_tf(["workspace", "new", name])
        if success:
            console.print(f"[success]✓ Created workspace: {name}[/success]")
        else:
            console.print(f"[error]{output}[/error]")
    
    elif action == "delete":
        if not name:
            console.print("[error]Workspace name required[/error]")
            return
        run_tf(["workspace", "delete", name], capture=False)


@tf.command(name="import")
@click.argument("address")
@click.argument("resource_id")
def tf_import(address, resource_id):
    """Import existing resource."""
    console.print(f"\n[bold cyan]📥 Importing {resource_id}...[/bold cyan]\n")
    run_tf(["import", address, resource_id], capture=False)


main = tf

if __name__ == "__main__":
    tf()
