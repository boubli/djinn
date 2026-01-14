"""
Ollama Manager Plugin for DJINN
Manage local Ollama models.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import requests
import json

console = Console()

PLUGIN_NAME = "ollama-manager"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Manage local Ollama LLM models."

OLLAMA_HOST = "http://localhost:11434"


def ollama_request(method, endpoint, json_data=None, stream=False):
    """Make request to Ollama API."""
    url = f"{OLLAMA_HOST}/api/{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=30)
        elif method == "POST":
            resp = requests.post(url, json=json_data, timeout=300, stream=stream)
        elif method == "DELETE":
            resp = requests.delete(url, json=json_data, timeout=30)
        return resp
    except requests.exceptions.ConnectionError:
        console.print("[error]Cannot connect to Ollama. Is it running?[/error]")
        console.print("[muted]Start with: ollama serve[/muted]")
        return None


@click.group()
def ollama():
    """Ollama model management."""
    pass


@ollama.command(name="list")
def list_models():
    """List downloaded models."""
    resp = ollama_request("GET", "tags")
    if not resp:
        return
    
    console.print("\n[bold cyan]🤖 Downloaded Models[/bold cyan]\n")
    
    try:
        data = resp.json()
        models = data.get("models", [])
        
        if not models:
            console.print("[muted]No models downloaded. Run: djinn ollama pull llama3[/muted]")
            return
        
        table = Table()
        table.add_column("Model", style="cyan")
        table.add_column("Size")
        table.add_column("Modified")
        
        for model in models:
            name = model.get("name", "")
            size = model.get("size", 0)
            size_gb = f"{size / (1024**3):.1f} GB"
            modified = model.get("modified_at", "")[:10]
            
            table.add_row(name, size_gb, modified)
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ollama.command(name="pull")
@click.argument("model_name")
def pull_model(model_name):
    """Download a model."""
    console.print(f"\n[bold cyan]📥 Pulling {model_name}...[/bold cyan]\n")
    
    resp = ollama_request("POST", "pull", {"name": model_name}, stream=True)
    if not resp:
        return
    
    try:
        with Progress() as progress:
            task = None
            
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get("status", "")
                    
                    if "pulling" in status and "total" in data:
                        total = data["total"]
                        completed = data.get("completed", 0)
                        
                        if task is None:
                            task = progress.add_task(f"[cyan]{status}", total=total)
                        
                        progress.update(task, completed=completed)
                    elif "success" in status:
                        console.print(f"\n[success]✓ {model_name} downloaded![/success]")
                        return
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ollama.command(name="rm")
@click.argument("model_name")
def remove_model(model_name):
    """Remove a model."""
    resp = ollama_request("DELETE", "delete", {"name": model_name})
    if not resp:
        return
    
    if resp.status_code == 200:
        console.print(f"[success]✓ Removed {model_name}[/success]")
    else:
        console.print(f"[error]Failed to remove {model_name}[/error]")


@ollama.command(name="show")
@click.argument("model_name")
def show_model(model_name):
    """Show model details."""
    resp = ollama_request("POST", "show", {"name": model_name})
    if not resp:
        return
    
    try:
        data = resp.json()
        
        console.print(f"\n[bold cyan]📋 {model_name}[/bold cyan]\n")
        
        # Model file
        if "modelfile" in data:
            console.print("[bold]Modelfile:[/bold]")
            console.print(data["modelfile"][:500])
        
        # Parameters
        if "parameters" in data:
            console.print("\n[bold]Parameters:[/bold]")
            console.print(data["parameters"])
        
        # Template
        if "template" in data:
            console.print("\n[bold]Template:[/bold]")
            console.print(data["template"][:200])
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ollama.command(name="run")
@click.argument("model_name")
@click.argument("prompt", nargs=-1)
def run_model(model_name, prompt):
    """Run a quick prompt."""
    prompt_text = " ".join(prompt)
    
    if not prompt_text:
        console.print("[error]Provide a prompt[/error]")
        return
    
    console.print(f"\n[bold cyan]💬 {model_name}[/bold cyan]\n")
    
    resp = ollama_request("POST", "generate", {
        "model": model_name,
        "prompt": prompt_text,
        "stream": True
    }, stream=True)
    
    if not resp:
        return
    
    try:
        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                response = data.get("response", "")
                print(response, end="", flush=True)
                
                if data.get("done"):
                    print("\n")
    except Exception as e:
        console.print(f"\n[error]Error: {e}[/error]")


@ollama.command(name="ps")
def running_models():
    """Show running models."""
    resp = ollama_request("GET", "ps")
    if not resp:
        return
    
    console.print("\n[bold cyan]⚡ Running Models[/bold cyan]\n")
    
    try:
        data = resp.json()
        models = data.get("models", [])
        
        if not models:
            console.print("[muted]No models currently loaded[/muted]")
            return
        
        table = Table()
        table.add_column("Model", style="cyan")
        table.add_column("Size")
        table.add_column("VRAM")
        
        for model in models:
            name = model.get("name", "")
            size = model.get("size", 0)
            size_gb = f"{size / (1024**3):.1f} GB"
            vram = model.get("size_vram", 0)
            vram_gb = f"{vram / (1024**3):.1f} GB"
            
            table.add_row(name, size_gb, vram_gb)
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ollama.command(name="copy")
@click.argument("source")
@click.argument("destination")
def copy_model(source, destination):
    """Copy a model."""
    resp = ollama_request("POST", "copy", {
        "source": source,
        "destination": destination
    })
    
    if resp and resp.status_code == 200:
        console.print(f"[success]✓ Copied {source} to {destination}[/success]")
    else:
        console.print(f"[error]Failed to copy model[/error]")


main = ollama

if __name__ == "__main__":
    ollama()
