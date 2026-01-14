"""
API Tester Plugin for DJINN
Postman-like HTTP client from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
import requests
import json
import time
from pathlib import Path

console = Console()

PLUGIN_NAME = "api-tester"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "HTTP API testing client like Postman."

COLLECTIONS_FILE = Path.home() / ".djinn" / "api_collections.json"


def load_collections():
    """Load saved API collections."""
    if COLLECTIONS_FILE.exists():
        with open(COLLECTIONS_FILE) as f:
            return json.load(f)
    return {}


def save_collections(collections):
    """Save API collections."""
    COLLECTIONS_FILE.parent.mkdir(exist_ok=True)
    with open(COLLECTIONS_FILE, 'w') as f:
        json.dump(collections, f, indent=2)


@click.group()
def api():
    """API testing commands."""
    pass


@api.command(name="get")
@click.argument("url")
@click.option("--header", "-H", multiple=True, help="Headers (key:value)")
@click.option("--auth", help="Bearer token")
@click.option("--save", help="Save request as named endpoint")
def http_get(url, header, auth, save):
    """Make GET request."""
    headers = {}
    
    for h in header:
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    
    console.print(f"\n[bold cyan]GET[/bold cyan] {url}\n")
    
    start = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=30)
        elapsed = (time.time() - start) * 1000
        
        _display_response(response, elapsed)
        
        if save:
            _save_request(save, "GET", url, headers)
    
    except Exception as e:
        console.print(f"[error]Request failed: {e}[/error]")


@api.command(name="post")
@click.argument("url")
@click.option("--data", "-d", help="JSON body")
@click.option("--file", "-f", "file_path", help="JSON file for body")
@click.option("--header", "-H", multiple=True, help="Headers (key:value)")
@click.option("--auth", help="Bearer token")
@click.option("--save", help="Save request as named endpoint")
def http_post(url, data, file_path, header, auth, save):
    """Make POST request."""
    headers = {"Content-Type": "application/json"}
    
    for h in header:
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    
    body = None
    if file_path:
        with open(file_path) as f:
            body = json.load(f)
    elif data:
        body = json.loads(data)
    
    console.print(f"\n[bold green]POST[/bold green] {url}\n")
    
    start = time.time()
    try:
        response = requests.post(url, json=body, headers=headers, timeout=30)
        elapsed = (time.time() - start) * 1000
        
        _display_response(response, elapsed)
        
        if save:
            _save_request(save, "POST", url, headers, body)
    
    except Exception as e:
        console.print(f"[error]Request failed: {e}[/error]")


@api.command(name="put")
@click.argument("url")
@click.option("--data", "-d", help="JSON body")
@click.option("--header", "-H", multiple=True)
@click.option("--auth", help="Bearer token")
def http_put(url, data, header, auth):
    """Make PUT request."""
    headers = {"Content-Type": "application/json"}
    
    for h in header:
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    
    body = json.loads(data) if data else None
    
    console.print(f"\n[bold yellow]PUT[/bold yellow] {url}\n")
    
    start = time.time()
    try:
        response = requests.put(url, json=body, headers=headers, timeout=30)
        elapsed = (time.time() - start) * 1000
        
        _display_response(response, elapsed)
    
    except Exception as e:
        console.print(f"[error]Request failed: {e}[/error]")


@api.command(name="delete")
@click.argument("url")
@click.option("--header", "-H", multiple=True)
@click.option("--auth", help="Bearer token")
def http_delete(url, header, auth):
    """Make DELETE request."""
    headers = {}
    
    for h in header:
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    
    if auth:
        headers["Authorization"] = f"Bearer {auth}"
    
    console.print(f"\n[bold red]DELETE[/bold red] {url}\n")
    
    start = time.time()
    try:
        response = requests.delete(url, headers=headers, timeout=30)
        elapsed = (time.time() - start) * 1000
        
        _display_response(response, elapsed)
    
    except Exception as e:
        console.print(f"[error]Request failed: {e}[/error]")


@api.command(name="saved")
def list_saved():
    """List saved requests."""
    collections = load_collections()
    
    if not collections:
        console.print("[muted]No saved requests[/muted]")
        return
    
    console.print("\n[bold cyan]📋 Saved Requests[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Method")
    table.add_column("URL")
    
    for name, req in collections.items():
        method_color = {"GET": "cyan", "POST": "green", "PUT": "yellow", "DELETE": "red"}
        color = method_color.get(req["method"], "white")
        table.add_row(name, f"[{color}]{req['method']}[/{color}]", req["url"][:50])
    
    console.print(table)


@api.command(name="run")
@click.argument("name")
def run_saved(name):
    """Run a saved request."""
    collections = load_collections()
    
    if name not in collections:
        console.print(f"[error]Request '{name}' not found[/error]")
        return
    
    req = collections[name]
    method = req["method"]
    url = req["url"]
    headers = req.get("headers", {})
    body = req.get("body")
    
    console.print(f"\n[bold]{method}[/bold] {url}\n")
    
    start = time.time()
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=body, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=body, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            console.print(f"[error]Unknown method: {method}[/error]")
            return
        
        elapsed = (time.time() - start) * 1000
        _display_response(response, elapsed)
    
    except Exception as e:
        console.print(f"[error]Request failed: {e}[/error]")


def _display_response(response, elapsed_ms):
    """Display HTTP response."""
    status_color = "green" if response.status_code < 400 else "red"
    
    console.print(f"[{status_color}]Status: {response.status_code} {response.reason}[/{status_color}]")
    console.print(f"[muted]Time: {elapsed_ms:.0f}ms | Size: {len(response.content)} bytes[/muted]\n")
    
    # Headers
    console.print("[bold]Response Headers:[/bold]")
    for key, value in list(response.headers.items())[:5]:
        console.print(f"  [muted]{key}:[/muted] {value[:50]}")
    
    # Body
    console.print("\n[bold]Response Body:[/bold]")
    try:
        json_data = response.json()
        formatted = json.dumps(json_data, indent=2)
        if len(formatted) > 2000:
            formatted = formatted[:2000] + "\n... (truncated)"
        syntax = Syntax(formatted, "json", theme="monokai")
        console.print(syntax)
    except:
        body = response.text[:1000]
        console.print(body)


def _save_request(name, method, url, headers, body=None):
    """Save request to collections."""
    collections = load_collections()
    collections[name] = {
        "method": method,
        "url": url,
        "headers": headers,
        "body": body
    }
    save_collections(collections)
    console.print(f"\n[success]✓ Saved as '{name}'[/success]")


main = api

if __name__ == "__main__":
    api()
