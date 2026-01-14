"""
GitHub Toolkit Plugin for DJINN
Advanced GitHub operations: PRs, Releases, Actions.
"""
import click
from rich.console import Console
from rich.table import Table
import os

console = Console()

# Plugin Metadata
PLUGIN_NAME = "github-toolkit"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Advanced GitHub operations."
PLUGIN_CATEGORY = "development"


def get_github_client():
    """Get authenticated GitHub client."""
    try:
        from github import Github
        
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            console.print("[error]GITHUB_TOKEN environment variable not set[/error]")
            console.print("[muted]Set with: export GITHUB_TOKEN=your_token[/muted]")
            return None
        
        return Github(token)
    except ImportError:
        console.print("[error]PyGithub not installed. Run: pip install PyGithub[/error]")
        return None


@click.group()
def gh():
    """GitHub toolkit commands."""
    pass


@gh.command(name="prs")
@click.argument("repo")
@click.option("--state", default="open", help="PR state: open, closed, all")
def list_prs(repo, state):
    """List pull requests for a repository."""
    g = get_github_client()
    if not g:
        return
    
    try:
        repository = g.get_repo(repo)
        prs = repository.get_pulls(state=state)
        
        console.print(f"\n[bold cyan]📋 Pull Requests for {repo}[/bold cyan]\n")
        
        table = Table()
        table.add_column("#", style="cyan")
        table.add_column("Title")
        table.add_column("Author")
        table.add_column("Status")
        
        for pr in prs[:20]:
            status_color = "green" if pr.mergeable else "yellow"
            table.add_row(
                str(pr.number),
                pr.title[:50],
                pr.user.login,
                f"[{status_color}]{pr.state}[/{status_color}]"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@gh.command(name="releases")
@click.argument("repo")
@click.option("--limit", default=10, help="Number of releases")
def list_releases(repo, limit):
    """List releases for a repository."""
    g = get_github_client()
    if not g:
        return
    
    try:
        repository = g.get_repo(repo)
        releases = repository.get_releases()
        
        console.print(f"\n[bold cyan]📦 Releases for {repo}[/bold cyan]\n")
        
        table = Table()
        table.add_column("Tag", style="cyan")
        table.add_column("Name")
        table.add_column("Date")
        table.add_column("Downloads")
        
        for release in list(releases)[:limit]:
            downloads = sum(asset.download_count for asset in release.get_assets())
            table.add_row(
                release.tag_name,
                release.title or "(no title)",
                str(release.created_at.date()),
                str(downloads)
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@gh.command(name="actions")
@click.argument("repo")
def list_actions(repo):
    """List recent GitHub Actions runs."""
    g = get_github_client()
    if not g:
        return
    
    try:
        repository = g.get_repo(repo)
        runs = repository.get_workflow_runs()
        
        console.print(f"\n[bold cyan]⚡ Actions for {repo}[/bold cyan]\n")
        
        table = Table()
        table.add_column("Workflow", style="cyan")
        table.add_column("Branch")
        table.add_column("Status")
        table.add_column("Duration")
        
        for run in list(runs)[:10]:
            status_color = "green" if run.conclusion == "success" else "red" if run.conclusion == "failure" else "yellow"
            
            table.add_row(
                run.name[:30],
                run.head_branch,
                f"[{status_color}]{run.conclusion or run.status}[/{status_color}]",
                str(run.run_started_at) if run.run_started_at else "-"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@gh.command(name="create-release")
@click.argument("repo")
@click.argument("tag")
@click.option("--name", help="Release name")
@click.option("--body", help="Release notes")
@click.option("--draft", is_flag=True, help="Create as draft")
def create_release(repo, tag, name, body, draft):
    """Create a new GitHub release."""
    g = get_github_client()
    if not g:
        return
    
    try:
        repository = g.get_repo(repo)
        
        release = repository.create_git_release(
            tag=tag,
            name=name or tag,
            message=body or f"Release {tag}",
            draft=draft
        )
        
        console.print(f"[success]✓ Release {tag} created![/success]")
        console.print(f"[muted]{release.html_url}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


# Export the main command
main = gh

if __name__ == "__main__":
    gh()
