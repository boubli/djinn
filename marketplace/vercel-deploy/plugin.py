"""
Vercel Deploy Plugin for DJINN
Deploy projects to Vercel from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import subprocess
import json
import os
from pathlib import Path

console = Console()

PLUGIN_NAME = "vercel-deploy"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Deploy to Vercel, manage projects and domains."


def run_vercel_cmd(args, capture=True):
    """Run vercel CLI command."""
    cmd = ["vercel"] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        else:
            subprocess.run(cmd)
            return True, ""
    except FileNotFoundError:
        return False, "Vercel CLI not installed. Run: npm i -g vercel"


@click.group()
def vercel():
    """Vercel deployment commands."""
    pass


@vercel.command(name="deploy")
@click.option("--prod", is_flag=True, help="Deploy to production")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def deploy(prod, yes):
    """Deploy current directory to Vercel."""
    console.print("\n[bold cyan]🚀 Deploying to Vercel...[/bold cyan]\n")
    
    args = []
    if prod:
        args.append("--prod")
    if yes:
        args.append("--yes")
    
    success, output = run_vercel_cmd(args, capture=False)
    
    if not success:
        console.print(f"[error]{output}[/error]")


@vercel.command(name="ls")
@click.option("--limit", default=10, help="Number of deployments")
def list_deployments(limit):
    """List recent deployments."""
    console.print("\n[bold cyan]📋 Recent Deployments[/bold cyan]\n")
    
    success, output = run_vercel_cmd(["ls", "--json"])
    
    if not success:
        console.print(f"[error]{output}[/error]")
        return
    
    try:
        # Parse JSON output
        lines = [l for l in output.split('\n') if l.strip()]
        deployments = []
        
        for line in lines:
            try:
                d = json.loads(line)
                if isinstance(d, list):
                    deployments.extend(d)
                elif isinstance(d, dict):
                    deployments.append(d)
            except:
                pass
        
        table = Table()
        table.add_column("URL", style="cyan")
        table.add_column("State")
        table.add_column("Created")
        
        for dep in deployments[:limit]:
            if isinstance(dep, dict):
                state = dep.get("state", dep.get("readyState", "unknown"))
                state_color = "green" if state == "READY" else "yellow"
                table.add_row(
                    dep.get("url", "")[:50],
                    f"[{state_color}]{state}[/{state_color}]",
                    str(dep.get("created", ""))[:10]
                )
        
        console.print(table)
    except Exception as e:
        # Fallback to text output
        console.print(output)


@vercel.command(name="logs")
@click.argument("deployment_url", required=False)
def view_logs(deployment_url):
    """View deployment logs."""
    console.print("\n[bold cyan]📜 Deployment Logs[/bold cyan]\n")
    
    args = ["logs"]
    if deployment_url:
        args.append(deployment_url)
    
    run_vercel_cmd(args, capture=False)


@vercel.command(name="env")
@click.argument("action", type=click.Choice(["ls", "add", "rm"]))
@click.argument("name", required=False)
@click.argument("value", required=False)
@click.option("--production", is_flag=True)
@click.option("--preview", is_flag=True)
@click.option("--development", is_flag=True)
def manage_env(action, name, value, production, preview, development):
    """Manage environment variables."""
    if action == "ls":
        console.print("\n[bold cyan]🔐 Environment Variables[/bold cyan]\n")
        run_vercel_cmd(["env", "ls"], capture=False)
    
    elif action == "add":
        if not name or not value:
            console.print("[error]Usage: djinn vercel env add NAME VALUE[/error]")
            return
        
        args = ["env", "add", name, value]
        if production:
            args.extend(["--scope", "production"])
        if preview:
            args.extend(["--scope", "preview"])
        if development:
            args.extend(["--scope", "development"])
        
        success, output = run_vercel_cmd(args)
        if success:
            console.print(f"[success]✓ Added {name}[/success]")
        else:
            console.print(f"[error]{output}[/error]")
    
    elif action == "rm":
        if not name:
            console.print("[error]Usage: djinn vercel env rm NAME[/error]")
            return
        
        success, output = run_vercel_cmd(["env", "rm", name, "--yes"])
        if success:
            console.print(f"[success]✓ Removed {name}[/success]")
        else:
            console.print(f"[error]{output}[/error]")


@vercel.command(name="domains")
@click.argument("action", type=click.Choice(["ls", "add", "rm"]))
@click.argument("domain", required=False)
def manage_domains(action, domain):
    """Manage custom domains."""
    if action == "ls":
        console.print("\n[bold cyan]🌐 Domains[/bold cyan]\n")
        run_vercel_cmd(["domains", "ls"], capture=False)
    
    elif action == "add":
        if not domain:
            console.print("[error]Usage: djinn vercel domains add DOMAIN[/error]")
            return
        
        success, output = run_vercel_cmd(["domains", "add", domain])
        if success:
            console.print(f"[success]✓ Added {domain}[/success]")
        else:
            console.print(f"[error]{output}[/error]")
    
    elif action == "rm":
        if not domain:
            console.print("[error]Usage: djinn vercel domains rm DOMAIN[/error]")
            return
        
        success, output = run_vercel_cmd(["domains", "rm", domain, "--yes"])
        if success:
            console.print(f"[success]✓ Removed {domain}[/success]")
        else:
            console.print(f"[error]{output}[/error]")


@vercel.command(name="rollback")
@click.argument("deployment_url")
def rollback(deployment_url):
    """Rollback to a previous deployment."""
    console.print(f"\n[bold yellow]↩️  Rolling back to {deployment_url}[/bold yellow]\n")
    
    success, output = run_vercel_cmd(["rollback", deployment_url])
    
    if success:
        console.print("[success]✓ Rollback complete![/success]")
    else:
        console.print(f"[error]{output}[/error]")


@vercel.command(name="promote")
@click.argument("deployment_url")
def promote(deployment_url):
    """Promote a preview deployment to production."""
    console.print(f"\n[bold green]⬆️  Promoting to production[/bold green]\n")
    
    success, output = run_vercel_cmd(["promote", deployment_url])
    
    if success:
        console.print("[success]✓ Promoted to production![/success]")
    else:
        console.print(f"[error]{output}[/error]")


main = vercel

if __name__ == "__main__":
    vercel()
