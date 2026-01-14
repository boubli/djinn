"""
Netlify Plugin for DJINN
Netlify deployment and site management.
"""
import click
from rich.console import Console
from rich.table import Table
import subprocess
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "netlify"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Netlify deployment and site management."


def run_netlify(args, capture=True):
    """Run Netlify CLI command."""
    cmd = ["netlify"] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        else:
            subprocess.run(cmd)
            return True, ""
    except FileNotFoundError:
        return False, "Netlify CLI not installed. Run: npm i -g netlify-cli"


@click.group()
def netlify():
    """Netlify commands."""
    pass


@netlify.command(name="login")
def login():
    """Login to Netlify."""
    run_netlify(["login"], capture=False)


@netlify.command(name="deploy")
@click.option("--prod", is_flag=True, help="Deploy to production")
@click.option("--dir", "deploy_dir", default=".", help="Directory to deploy")
@click.option("--message", "-m", help="Deploy message")
def deploy(prod, deploy_dir, message):
    """Deploy site to Netlify."""
    console.print("\n[bold cyan]🚀 Deploying to Netlify...[/bold cyan]\n")
    
    args = ["deploy", "--dir", deploy_dir]
    
    if prod:
        args.append("--prod")
    if message:
        args.extend(["--message", message])
    
    run_netlify(args, capture=False)


@netlify.command(name="sites")
def list_sites():
    """List your Netlify sites."""
    console.print("\n[bold cyan]🌐 Your Sites[/bold cyan]\n")
    
    success, output = run_netlify(["sites:list", "--json"])
    
    if not success:
        console.print(f"[error]{output}[/error]")
        return
    
    try:
        sites = json.loads(output)
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("URL")
        table.add_column("ID")
        
        for site in sites:
            table.add_row(
                site.get("name", ""),
                site.get("ssl_url", site.get("url", "")),
                site.get("id", "")[:12] + "..."
            )
        
        console.print(table)
    except:
        console.print(output)


@netlify.command(name="open")
@click.option("--admin", is_flag=True, help="Open admin panel")
def open_site(admin):
    """Open site in browser."""
    args = ["open"]
    if admin:
        args.append("--admin")
    
    run_netlify(args, capture=False)


@netlify.command(name="status")
def site_status():
    """Show current site status."""
    run_netlify(["status"], capture=False)


@netlify.command(name="init")
def init_site():
    """Initialize new Netlify site."""
    run_netlify(["init"], capture=False)


@netlify.command(name="link")
@click.option("--name", help="Site name to link")
def link_site(name):
    """Link local directory to Netlify site."""
    args = ["link"]
    if name:
        args.extend(["--name", name])
    
    run_netlify(args, capture=False)


@netlify.command(name="unlink")
def unlink_site():
    """Unlink from Netlify site."""
    run_netlify(["unlink"], capture=False)


@netlify.command(name="env")
@click.argument("action", type=click.Choice(["list", "set", "unset", "import"]))
@click.argument("args", nargs=-1)
def manage_env(action, args):
    """Manage environment variables."""
    if action == "list":
        run_netlify(["env:list"], capture=False)
    
    elif action == "set":
        if len(args) < 2:
            console.print("[error]Usage: djinn netlify env set KEY VALUE[/error]")
            return
        run_netlify(["env:set", args[0], args[1]], capture=False)
    
    elif action == "unset":
        if not args:
            console.print("[error]Usage: djinn netlify env unset KEY[/error]")
            return
        run_netlify(["env:unset", args[0]], capture=False)
    
    elif action == "import":
        if not args:
            console.print("[error]Usage: djinn netlify env import .env[/error]")
            return
        run_netlify(["env:import", args[0]], capture=False)


@netlify.command(name="functions")
@click.argument("action", type=click.Choice(["list", "create", "invoke"]))
@click.argument("args", nargs=-1)
def manage_functions(action, args):
    """Manage serverless functions."""
    if action == "list":
        run_netlify(["functions:list"], capture=False)
    
    elif action == "create":
        name = args[0] if args else "my-function"
        run_netlify(["functions:create", name], capture=False)
    
    elif action == "invoke":
        if not args:
            console.print("[error]Usage: djinn netlify functions invoke FUNCTION_NAME[/error]")
            return
        run_netlify(["functions:invoke", args[0]], capture=False)


@netlify.command(name="logs")
@click.option("--function", "-f", "function_name", help="Function name")
def view_logs(function_name):
    """View function logs."""
    args = ["logs"]
    if function_name:
        args.extend(["-f", function_name])
    
    run_netlify(args, capture=False)


@netlify.command(name="dev")
@click.option("--port", default=8888, type=int)
def local_dev(port):
    """Start local development server."""
    console.print(f"\n[bold cyan]🔧 Starting local dev server on port {port}...[/bold cyan]\n")
    run_netlify(["dev", "--port", str(port)], capture=False)


@netlify.command(name="build")
def build_site():
    """Build site locally."""
    console.print("\n[bold cyan]🔨 Building site...[/bold cyan]\n")
    run_netlify(["build"], capture=False)


main = netlify

if __name__ == "__main__":
    netlify()
