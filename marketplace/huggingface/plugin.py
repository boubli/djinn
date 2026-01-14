"""
HuggingFace Plugin for DJINN
HuggingFace Hub model management.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "huggingface"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "HuggingFace Hub model management."

CONFIG_FILE = Path.home() / ".djinn" / "huggingface.json"


def get_hf_token():
    """Get HuggingFace token."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    
    if not token and CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            token = json.load(f).get("token")
    
    return token


@click.group()
def hf():
    """HuggingFace commands."""
    pass


@hf.command(name="auth")
@click.argument("token")
def set_auth(token):
    """Save HuggingFace token."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"token": token}, f)
    
    console.print("[success]✓ HuggingFace token saved![/success]")


@hf.command(name="search")
@click.argument("query")
@click.option("--type", "model_type", type=click.Choice(["model", "dataset", "space"]), default="model")
@click.option("--limit", default=10, type=int)
def search_hub(query, model_type, limit):
    """Search HuggingFace Hub."""
    try:
        from huggingface_hub import HfApi
        
        api = HfApi(token=get_hf_token())
        
        console.print(f"\n[bold cyan]🔍 Searching for '{query}'...[/bold cyan]\n")
        
        if model_type == "model":
            results = api.list_models(search=query, limit=limit)
            
            table = Table()
            table.add_column("Model", style="cyan")
            table.add_column("Downloads")
            table.add_column("Likes")
            table.add_column("Tags")
            
            for model in results:
                tags = ", ".join(model.tags[:3]) if model.tags else "-"
                table.add_row(
                    model.modelId,
                    str(model.downloads) if hasattr(model, 'downloads') else "-",
                    str(model.likes) if hasattr(model, 'likes') else "-",
                    tags[:30]
                )
            
            console.print(table)
        
        elif model_type == "dataset":
            results = api.list_datasets(search=query, limit=limit)
            
            table = Table()
            table.add_column("Dataset", style="cyan")
            table.add_column("Downloads")
            
            for dataset in results:
                table.add_row(
                    dataset.id,
                    str(getattr(dataset, 'downloads', '-'))
                )
            
            console.print(table)
        
        elif model_type == "space":
            results = api.list_spaces(search=query, limit=limit)
            
            table = Table()
            table.add_column("Space", style="cyan")
            table.add_column("SDK")
            table.add_column("Likes")
            
            for space in results:
                table.add_row(
                    space.id,
                    getattr(space, 'sdk', '-'),
                    str(getattr(space, 'likes', '-'))
                )
            
            console.print(table)
    except ImportError:
        console.print("[error]huggingface_hub not installed. Run: pip install huggingface_hub[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@hf.command(name="download")
@click.argument("model_id")
@click.option("--revision", default="main")
@click.option("--cache-dir", help="Custom cache directory")
def download_model(model_id, revision, cache_dir):
    """Download a model from Hub."""
    try:
        from huggingface_hub import snapshot_download
        
        console.print(f"\n[bold cyan]📥 Downloading {model_id}...[/bold cyan]\n")
        
        path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            cache_dir=cache_dir,
            token=get_hf_token()
        )
        
        console.print(f"[success]✓ Downloaded to: {path}[/success]")
    except ImportError:
        console.print("[error]huggingface_hub not installed. Run: pip install huggingface_hub[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@hf.command(name="info")
@click.argument("model_id")
def model_info(model_id):
    """Get model information."""
    try:
        from huggingface_hub import HfApi
        
        api = HfApi(token=get_hf_token())
        info = api.model_info(model_id)
        
        console.print(f"\n[bold cyan]📋 {model_id}[/bold cyan]\n")
        
        console.print(f"[muted]Author:[/muted] {info.author or '-'}")
        console.print(f"[muted]Downloads:[/muted] {getattr(info, 'downloads', '-')}")
        console.print(f"[muted]Likes:[/muted] {getattr(info, 'likes', '-')}")
        console.print(f"[muted]Library:[/muted] {info.library_name or '-'}")
        console.print(f"[muted]Pipeline:[/muted] {info.pipeline_tag or '-'}")
        
        if info.tags:
            console.print(f"[muted]Tags:[/muted] {', '.join(info.tags[:10])}")
        
        console.print(f"\n[muted]https://huggingface.co/{model_id}[/muted]")
    except ImportError:
        console.print("[error]huggingface_hub not installed. Run: pip install huggingface_hub[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@hf.command(name="cache")
@click.option("--scan", is_flag=True, help="Scan cache usage")
@click.option("--clean", is_flag=True, help="Clean cache")
def manage_cache(scan, clean):
    """Manage HuggingFace cache."""
    try:
        from huggingface_hub import scan_cache_dir, HfFolder
        
        cache_info = scan_cache_dir()
        
        if scan or not clean:
            console.print("\n[bold cyan]📦 HuggingFace Cache[/bold cyan]\n")
            
            total_size = sum(repo.size_on_disk for repo in cache_info.repos)
            console.print(f"[bold]Total Size:[/bold] {total_size / (1024**3):.2f} GB")
            console.print(f"[bold]Repos:[/bold] {len(cache_info.repos)}")
            
            console.print("\n[bold]Top 10 by size:[/bold]")
            
            sorted_repos = sorted(cache_info.repos, key=lambda r: r.size_on_disk, reverse=True)
            
            table = Table()
            table.add_column("Repo", style="cyan")
            table.add_column("Size")
            table.add_column("Revisions")
            
            for repo in sorted_repos[:10]:
                size = f"{repo.size_on_disk / (1024**2):.1f} MB"
                table.add_row(repo.repo_id, size, str(len(repo.revisions)))
            
            console.print(table)
        
        if clean:
            console.print("\n[bold yellow]⚠️  Use 'huggingface-cli delete-cache' for interactive cleanup[/bold yellow]")
    except ImportError:
        console.print("[error]huggingface_hub not installed. Run: pip install huggingface_hub[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@hf.command(name="repos")
@click.option("--type", "repo_type", type=click.Choice(["model", "dataset", "space"]), default="model")
def list_my_repos(repo_type):
    """List your repos."""
    try:
        from huggingface_hub import HfApi
        
        token = get_hf_token()
        if not token:
            console.print("[error]Not authenticated[/error]")
            return
        
        api = HfApi(token=token)
        user = api.whoami()
        
        console.print(f"\n[bold cyan]📁 Your {repo_type}s ({user['name']})[/bold cyan]\n")
        
        if repo_type == "model":
            repos = api.list_models(author=user["name"])
        elif repo_type == "dataset":
            repos = api.list_datasets(author=user["name"])
        elif repo_type == "space":
            repos = api.list_spaces(author=user["name"])
        
        for repo in repos:
            console.print(f"• {repo.id if hasattr(repo, 'id') else repo.modelId}")
    except ImportError:
        console.print("[error]huggingface_hub not installed. Run: pip install huggingface_hub[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@hf.command(name="upload")
@click.argument("local_path")
@click.argument("repo_id")
@click.option("--type", "repo_type", type=click.Choice(["model", "dataset", "space"]), default="model")
@click.option("--commit", default="Upload via DJINN", help="Commit message")
def upload_files(local_path, repo_id, repo_type, commit):
    """Upload files to Hub."""
    try:
        from huggingface_hub import HfApi
        
        token = get_hf_token()
        if not token:
            console.print("[error]Not authenticated[/error]")
            return
        
        api = HfApi(token=token)
        
        console.print(f"\n[bold cyan]📤 Uploading to {repo_id}...[/bold cyan]\n")
        
        local_path = Path(local_path)
        
        if local_path.is_dir():
            api.upload_folder(
                folder_path=str(local_path),
                repo_id=repo_id,
                repo_type=repo_type,
                commit_message=commit
            )
        else:
            api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=local_path.name,
                repo_id=repo_id,
                repo_type=repo_type,
                commit_message=commit
            )
        
        console.print(f"[success]✓ Uploaded to {repo_id}[/success]")
    except ImportError:
        console.print("[error]huggingface_hub not installed. Run: pip install huggingface_hub[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = hf

if __name__ == "__main__":
    hf()
