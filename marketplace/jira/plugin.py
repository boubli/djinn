"""
Jira Plugin for DJINN
Jira issue tracking from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
import requests
from pathlib import Path
from base64 import b64encode

console = Console()

PLUGIN_NAME = "jira"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Jira issue tracking from terminal."

CONFIG_FILE = Path.home() / ".djinn" / "jira.json"


def get_config():
    """Get Jira config."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    
    # Try environment variables
    domain = os.environ.get("JIRA_DOMAIN")
    email = os.environ.get("JIRA_EMAIL")
    token = os.environ.get("JIRA_API_TOKEN")
    
    if domain and email and token:
        return {"domain": domain, "email": email, "token": token}
    
    return None


def jira_request(method, endpoint, data=None):
    """Make Jira API request."""
    config = get_config()
    
    if not config:
        console.print("[error]Jira not configured[/error]")
        console.print("[muted]Run: djinn jira auth DOMAIN EMAIL TOKEN[/muted]")
        return None
    
    url = f"https://{config['domain']}.atlassian.net/rest/api/3{endpoint}"
    
    auth = b64encode(f"{config['email']}:{config['token']}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=30)
        
        if resp.status_code >= 400:
            console.print(f"[error]API Error: {resp.status_code}[/error]")
            return None
        
        return resp.json() if resp.text else {}
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        return None


@click.group()
def jira():
    """Jira commands."""
    pass


@jira.command(name="auth")
@click.argument("domain")
@click.argument("email")
@click.argument("token")
def set_auth(domain, email, token):
    """Save Jira credentials."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"domain": domain, "email": email, "token": token}, f)
    
    console.print("[success]✓ Jira credentials saved![/success]")


@jira.command(name="issues")
@click.option("--project", "-p", help="Project key")
@click.option("--assignee", help="Assignee (use 'me' for current user)")
@click.option("--status", help="Status filter")
@click.option("--jql", help="Custom JQL query")
@click.option("--limit", default=20, type=int)
def list_issues(project, assignee, status, jql, limit):
    """List issues."""
    if jql:
        query = jql
    else:
        clauses = []
        if project:
            clauses.append(f'project = "{project}"')
        if assignee:
            if assignee == "me":
                clauses.append("assignee = currentUser()")
            else:
                clauses.append(f'assignee = "{assignee}"')
        if status:
            clauses.append(f'status = "{status}"')
        
        query = " AND ".join(clauses) if clauses else "ORDER BY updated DESC"
    
    data = jira_request("GET", f"/search?jql={query}&maxResults={limit}")
    
    if not data:
        return
    
    console.print("\n[bold cyan]📋 Issues[/bold cyan]\n")
    
    table = Table()
    table.add_column("Key", style="cyan")
    table.add_column("Summary")
    table.add_column("Status")
    table.add_column("Assignee")
    table.add_column("Priority")
    
    for issue in data.get("issues", []):
        fields = issue["fields"]
        
        status_name = fields["status"]["name"]
        assignee_name = fields.get("assignee", {})
        assignee_name = assignee_name.get("displayName", "Unassigned") if assignee_name else "Unassigned"
        priority_name = fields.get("priority", {})
        priority_name = priority_name.get("name", "-") if priority_name else "-"
        
        table.add_row(
            issue["key"],
            fields["summary"][:40],
            status_name,
            assignee_name,
            priority_name
        )
    
    console.print(table)
    console.print(f"\n[muted]Total: {data.get('total', 0)} issues[/muted]")


@jira.command(name="view")
@click.argument("issue_key")
def view_issue(issue_key):
    """View issue details."""
    data = jira_request("GET", f"/issue/{issue_key}")
    
    if not data:
        return
    
    fields = data["fields"]
    
    console.print(f"\n[bold cyan]{data['key']}[/bold cyan]: {fields['summary']}")
    console.print(f"[muted]Status:[/muted] {fields['status']['name']}")
    console.print(f"[muted]Type:[/muted] {fields['issuetype']['name']}")
    
    if fields.get("priority"):
        console.print(f"[muted]Priority:[/muted] {fields['priority']['name']}")
    
    if fields.get("assignee"):
        console.print(f"[muted]Assignee:[/muted] {fields['assignee']['displayName']}")
    else:
        console.print("[muted]Assignee:[/muted] Unassigned")
    
    if fields.get("reporter"):
        console.print(f"[muted]Reporter:[/muted] {fields['reporter']['displayName']}")
    
    if fields.get("description"):
        desc_content = fields["description"].get("content", [])
        if desc_content:
            console.print(f"\n[bold]Description:[/bold]")
            for block in desc_content:
                if block.get("type") == "paragraph":
                    for content in block.get("content", []):
                        if content.get("type") == "text":
                            console.print(content.get("text", ""))
    
    config = get_config()
    if config:
        console.print(f"\n[muted]https://{config['domain']}.atlassian.net/browse/{data['key']}[/muted]")


@jira.command(name="create")
@click.argument("project")
@click.argument("summary")
@click.option("--type", "issue_type", default="Task", help="Issue type")
@click.option("--description", "-d", help="Description")
@click.option("--assignee", help="Assignee email")
@click.option("--priority", help="Priority name")
def create_issue(project, summary, issue_type, description, assignee, priority):
    """Create a new issue."""
    # Get project and issue type IDs
    project_data = jira_request("GET", f"/project/{project}")
    if not project_data:
        console.print(f"[error]Project '{project}' not found[/error]")
        return
    
    issue_types = jira_request("GET", f"/issuetype")
    issue_type_id = None
    for it in issue_types:
        if it["name"].lower() == issue_type.lower():
            issue_type_id = it["id"]
            break
    
    if not issue_type_id:
        console.print(f"[error]Issue type '{issue_type}' not found[/error]")
        return
    
    payload = {
        "fields": {
            "project": {"key": project},
            "summary": summary,
            "issuetype": {"id": issue_type_id}
        }
    }
    
    if description:
        payload["fields"]["description"] = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description}]
                }
            ]
        }
    
    data = jira_request("POST", "/issue", payload)
    
    if data:
        config = get_config()
        console.print(f"[success]✓ Created {data['key']}[/success]")
        if config:
            console.print(f"[muted]https://{config['domain']}.atlassian.net/browse/{data['key']}[/muted]")


@jira.command(name="transition")
@click.argument("issue_key")
@click.argument("status")
def transition_issue(issue_key, status):
    """Change issue status."""
    # Get available transitions
    transitions = jira_request("GET", f"/issue/{issue_key}/transitions")
    
    if not transitions:
        return
    
    transition_id = None
    for t in transitions.get("transitions", []):
        if t["name"].lower() == status.lower():
            transition_id = t["id"]
            break
    
    if not transition_id:
        console.print(f"[error]Status '{status}' not available[/error]")
        console.print("[muted]Available transitions:[/muted]")
        for t in transitions.get("transitions", []):
            console.print(f"  • {t['name']}")
        return
    
    result = jira_request("POST", f"/issue/{issue_key}/transitions", {"transition": {"id": transition_id}})
    
    if result is not None:
        console.print(f"[success]✓ {issue_key} moved to {status}[/success]")


@jira.command(name="comment")
@click.argument("issue_key")
@click.argument("text")
def add_comment(issue_key, text):
    """Add comment to issue."""
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": text}]
                }
            ]
        }
    }
    
    result = jira_request("POST", f"/issue/{issue_key}/comment", payload)
    
    if result:
        console.print(f"[success]✓ Comment added to {issue_key}[/success]")


@jira.command(name="projects")
def list_projects():
    """List projects."""
    data = jira_request("GET", "/project")
    
    if not data:
        return
    
    console.print("\n[bold cyan]📁 Projects[/bold cyan]\n")
    
    table = Table()
    table.add_column("Key", style="cyan")
    table.add_column("Name")
    table.add_column("Type")
    
    for project in data:
        table.add_row(project["key"], project["name"], project.get("projectTypeKey", "-"))
    
    console.print(table)


main = jira

if __name__ == "__main__":
    jira()
