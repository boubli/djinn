"""
Linear Plugin for DJINN
Linear issue tracking from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
import requests
from pathlib import Path

console = Console()

PLUGIN_NAME = "linear"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Linear issue tracking from terminal."

CONFIG_FILE = Path.home() / ".djinn" / "linear.json"
API_URL = "https://api.linear.app/graphql"


def get_api_key():
    """Get Linear API key."""
    api_key = os.environ.get("LINEAR_API_KEY")
    if not api_key and CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            api_key = json.load(f).get("api_key")
    return api_key


def graphql_request(query, variables=None):
    """Make GraphQL request to Linear."""
    api_key = get_api_key()
    
    if not api_key:
        console.print("[error]LINEAR_API_KEY not set[/error]")
        console.print("[muted]Run: djinn linear auth YOUR_API_KEY[/muted]")
        return None
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        data = resp.json()
        
        if "errors" in data:
            for error in data["errors"]:
                console.print(f"[error]{error['message']}[/error]")
            return None
        
        return data.get("data")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        return None


@click.group()
def linear():
    """Linear commands."""
    pass


@linear.command(name="auth")
@click.argument("api_key")
def set_auth(api_key):
    """Save Linear API key."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)
    
    console.print("[success]✓ Linear API key saved![/success]")


@linear.command(name="me")
def get_me():
    """Get current user info."""
    query = """
    query {
        viewer {
            id
            name
            email
            organization {
                name
            }
        }
    }
    """
    
    data = graphql_request(query)
    if not data:
        return
    
    user = data["viewer"]
    
    console.print(f"\n[bold cyan]👤 {user['name']}[/bold cyan]")
    console.print(f"Email: {user['email']}")
    console.print(f"Organization: {user['organization']['name']}")


@linear.command(name="issues")
@click.option("--assigned", is_flag=True, help="Only assigned to me")
@click.option("--team", help="Filter by team key")
@click.option("--status", help="Filter by status")
@click.option("--limit", default=20, type=int)
def list_issues(assigned, team, status, limit):
    """List issues."""
    filters = []
    
    if assigned:
        filters.append('assignee: { isMe: { eq: true } }')
    if team:
        filters.append(f'team: {{ key: {{ eq: "{team}" }} }}')
    if status:
        filters.append(f'state: {{ name: {{ eq: "{status}" }} }}')
    
    filter_str = ", ".join(filters) if filters else ""
    filter_arg = f"filter: {{ {filter_str} }}" if filter_str else ""
    
    query = f"""
    query {{
        issues(first: {limit}, {filter_arg}) {{
            nodes {{
                id
                identifier
                title
                priority
                state {{
                    name
                    color
                }}
                assignee {{
                    name
                }}
                team {{
                    key
                }}
            }}
        }}
    }}
    """
    
    data = graphql_request(query)
    if not data:
        return
    
    issues = data["issues"]["nodes"]
    
    console.print("\n[bold cyan]📋 Issues[/bold cyan]\n")
    
    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Assignee")
    table.add_column("Priority")
    
    priority_icons = {0: "⚪", 1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢"}
    
    for issue in issues:
        table.add_row(
            issue["identifier"],
            issue["title"][:40],
            issue["state"]["name"],
            issue["assignee"]["name"] if issue["assignee"] else "-",
            priority_icons.get(issue["priority"], "⚪")
        )
    
    console.print(table)


@linear.command(name="create")
@click.argument("title")
@click.option("--team", required=True, help="Team key")
@click.option("--description", "-d", help="Issue description")
@click.option("--priority", type=click.Choice(["0", "1", "2", "3", "4"]), default="0")
def create_issue(title, team, description, priority):
    """Create a new issue."""
    # First get team ID
    team_query = f"""
    query {{
        teams(filter: {{ key: {{ eq: "{team}" }} }}) {{
            nodes {{
                id
            }}
        }}
    }}
    """
    
    team_data = graphql_request(team_query)
    if not team_data or not team_data["teams"]["nodes"]:
        console.print(f"[error]Team '{team}' not found[/error]")
        return
    
    team_id = team_data["teams"]["nodes"][0]["id"]
    
    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
        issueCreate(input: $input) {
            success
            issue {
                id
                identifier
                title
                url
            }
        }
    }
    """
    
    variables = {
        "input": {
            "teamId": team_id,
            "title": title,
            "priority": int(priority)
        }
    }
    
    if description:
        variables["input"]["description"] = description
    
    data = graphql_request(mutation, variables)
    if not data:
        return
    
    if data["issueCreate"]["success"]:
        issue = data["issueCreate"]["issue"]
        console.print(f"[success]✓ Created {issue['identifier']}: {issue['title']}[/success]")
        console.print(f"[muted]{issue['url']}[/muted]")
    else:
        console.print("[error]Failed to create issue[/error]")


@linear.command(name="view")
@click.argument("issue_id")
def view_issue(issue_id):
    """View issue details."""
    query = f"""
    query {{
        issue(id: "{issue_id}") {{
            id
            identifier
            title
            description
            priority
            url
            state {{
                name
            }}
            assignee {{
                name
            }}
            creator {{
                name
            }}
            labels {{
                nodes {{
                    name
                    color
                }}
            }}
            comments {{
                nodes {{
                    body
                    user {{
                        name
                    }}
                    createdAt
                }}
            }}
        }}
    }}
    """
    
    # Try by identifier first
    by_id_query = f"""
    query {{
        issueSearch(query: "{issue_id}", first: 1) {{
            nodes {{
                id
                identifier
                title
                description
                priority
                url
                state {{
                    name
                }}
                assignee {{
                    name
                }}
                creator {{
                    name
                }}
            }}
        }}
    }}
    """
    
    data = graphql_request(by_id_query)
    if not data or not data["issueSearch"]["nodes"]:
        console.print(f"[error]Issue '{issue_id}' not found[/error]")
        return
    
    issue = data["issueSearch"]["nodes"][0]
    
    console.print(f"\n[bold cyan]{issue['identifier']}[/bold cyan]: {issue['title']}")
    console.print(f"[muted]Status:[/muted] {issue['state']['name']}")
    console.print(f"[muted]Assignee:[/muted] {issue['assignee']['name'] if issue['assignee'] else 'Unassigned'}")
    console.print(f"[muted]Creator:[/muted] {issue['creator']['name'] if issue['creator'] else '-'}")
    
    if issue.get("description"):
        console.print(f"\n[bold]Description:[/bold]\n{issue['description'][:500]}")
    
    console.print(f"\n[muted]{issue['url']}[/muted]")


@linear.command(name="teams")
def list_teams():
    """List teams."""
    query = """
    query {
        teams {
            nodes {
                id
                key
                name
            }
        }
    }
    """
    
    data = graphql_request(query)
    if not data:
        return
    
    console.print("\n[bold cyan]👥 Teams[/bold cyan]\n")
    
    table = Table()
    table.add_column("Key", style="cyan")
    table.add_column("Name")
    
    for team in data["teams"]["nodes"]:
        table.add_row(team["key"], team["name"])
    
    console.print(table)


@linear.command(name="cycles")
@click.option("--team", help="Team key")
def list_cycles(team):
    """List active cycles."""
    filter_arg = ""
    if team:
        filter_arg = f'filter: {{ team: {{ key: {{ eq: "{team}" }} }} }}'
    
    query = f"""
    query {{
        cycles(first: 10, {filter_arg}) {{
            nodes {{
                id
                number
                name
                startsAt
                endsAt
                progress
                team {{
                    key
                }}
            }}
        }}
    }}
    """
    
    data = graphql_request(query)
    if not data:
        return
    
    console.print("\n[bold cyan]🔄 Cycles[/bold cyan]\n")
    
    table = Table()
    table.add_column("Team", style="cyan")
    table.add_column("Cycle")
    table.add_column("Progress")
    table.add_column("Dates")
    
    for cycle in data["cycles"]["nodes"]:
        progress = int(cycle["progress"] * 100)
        bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        
        dates = f"{cycle['startsAt'][:10]} → {cycle['endsAt'][:10]}"
        
        table.add_row(
            cycle["team"]["key"],
            cycle["name"] or f"Cycle {cycle['number']}",
            f"{bar} {progress}%",
            dates
        )
    
    console.print(table)


main = linear

if __name__ == "__main__":
    linear()
