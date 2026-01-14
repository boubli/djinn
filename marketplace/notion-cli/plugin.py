"""
Notion CLI Plugin for DJINN
Manage Notion workspaces, pages, databases from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "notion-cli"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Manage Notion from terminal."


def get_notion_client():
    """Get Notion client."""
    try:
        from notion_client import Client
        
        token = os.environ.get("NOTION_TOKEN")
        if not token:
            # Try config file
            config_file = Path.home() / ".djinn" / "notion.json"
            if config_file.exists():
                with open(config_file) as f:
                    token = json.load(f).get("token")
        
        if not token:
            console.print("[error]NOTION_TOKEN not set[/error]")
            console.print("[muted]Set with: export NOTION_TOKEN=your_token[/muted]")
            console.print("[muted]Or: djinn notion auth YOUR_TOKEN[/muted]")
            return None
        
        return Client(auth=token)
    except ImportError:
        console.print("[error]notion-client not installed. Run: pip install notion-client[/error]")
        return None


@click.group()
def notion():
    """Notion commands."""
    pass


@notion.command(name="auth")
@click.argument("token")
def set_auth(token):
    """Save Notion API token."""
    config_file = Path.home() / ".djinn" / "notion.json"
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump({"token": token}, f)
    
    console.print("[success]✓ Notion token saved![/success]")


@notion.command(name="search")
@click.argument("query")
@click.option("--type", "filter_type", type=click.Choice(["page", "database"]), help="Filter by type")
def search_notion(query, filter_type):
    """Search Notion pages and databases."""
    client = get_notion_client()
    if not client:
        return
    
    console.print(f"\n[bold cyan]🔍 Searching: {query}[/bold cyan]\n")
    
    try:
        params = {"query": query}
        if filter_type:
            params["filter"] = {"property": "object", "value": filter_type}
        
        results = client.search(**params)
        
        table = Table()
        table.add_column("Type", style="cyan")
        table.add_column("Title")
        table.add_column("ID")
        
        for item in results.get("results", [])[:20]:
            obj_type = item["object"]
            
            if obj_type == "page":
                title = ""
                for prop in item.get("properties", {}).values():
                    if prop.get("type") == "title":
                        title = prop["title"][0]["plain_text"] if prop["title"] else ""
                        break
            else:
                title = item.get("title", [{}])[0].get("plain_text", "Untitled")
            
            table.add_row(obj_type, title[:40], item["id"][:12] + "...")
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@notion.command(name="databases")
def list_databases():
    """List accessible databases."""
    client = get_notion_client()
    if not client:
        return
    
    console.print("\n[bold cyan]📊 Databases[/bold cyan]\n")
    
    try:
        results = client.search(filter={"property": "object", "value": "database"})
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("ID")
        
        for db in results.get("results", []):
            title = db.get("title", [{}])[0].get("plain_text", "Untitled")
            table.add_row(title, db["id"])
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@notion.command(name="query")
@click.argument("database_id")
@click.option("--limit", default=20, help="Max results")
def query_database(database_id, limit):
    """Query a Notion database."""
    client = get_notion_client()
    if not client:
        return
    
    console.print(f"\n[bold cyan]📋 Database Contents[/bold cyan]\n")
    
    try:
        results = client.databases.query(database_id=database_id, page_size=limit)
        
        for page in results.get("results", []):
            props = page.get("properties", {})
            
            # Get title
            for prop_name, prop_value in props.items():
                if prop_value.get("type") == "title":
                    title = prop_value["title"][0]["plain_text"] if prop_value["title"] else "Untitled"
                    console.print(f"• [bold]{title}[/bold]")
                    break
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@notion.command(name="create")
@click.argument("database_id")
@click.argument("title")
@click.option("--props", help="JSON properties")
def create_page(database_id, title, props):
    """Create a page in a database."""
    client = get_notion_client()
    if not client:
        return
    
    try:
        properties = {"title": {"title": [{"text": {"content": title}}]}}
        
        if props:
            extra_props = json.loads(props)
            properties.update(extra_props)
        
        page = client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        console.print(f"[success]✓ Created page: {title}[/success]")
        console.print(f"[muted]ID: {page['id']}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@notion.command(name="page")
@click.argument("page_id")
def get_page(page_id):
    """Get page content."""
    client = get_notion_client()
    if not client:
        return
    
    try:
        page = client.pages.retrieve(page_id)
        blocks = client.blocks.children.list(page_id)
        
        # Display page title
        for prop in page.get("properties", {}).values():
            if prop.get("type") == "title":
                title = prop["title"][0]["plain_text"] if prop["title"] else "Untitled"
                console.print(f"\n[bold cyan]📄 {title}[/bold cyan]\n")
                break
        
        # Display content blocks
        for block in blocks.get("results", []):
            block_type = block["type"]
            
            if block_type == "paragraph":
                text = "".join([t["plain_text"] for t in block["paragraph"].get("rich_text", [])])
                console.print(text)
            elif block_type == "heading_1":
                text = "".join([t["plain_text"] for t in block["heading_1"].get("rich_text", [])])
                console.print(f"\n[bold]# {text}[/bold]")
            elif block_type == "heading_2":
                text = "".join([t["plain_text"] for t in block["heading_2"].get("rich_text", [])])
                console.print(f"\n[bold]## {text}[/bold]")
            elif block_type == "bulleted_list_item":
                text = "".join([t["plain_text"] for t in block["bulleted_list_item"].get("rich_text", [])])
                console.print(f"  • {text}")
            elif block_type == "to_do":
                text = "".join([t["plain_text"] for t in block["to_do"].get("rich_text", [])])
                checked = "✓" if block["to_do"].get("checked") else "○"
                console.print(f"  {checked} {text}")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = notion

if __name__ == "__main__":
    notion()
