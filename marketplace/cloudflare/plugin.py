"""
Cloudflare Plugin for DJINN
DNS, Workers, and Pages management.
"""
import click
from rich.console import Console
from rich.table import Table
import requests
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "cloudflare"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Cloudflare DNS, Workers, and Pages."


def get_cf_headers():
    """Get Cloudflare API headers."""
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        config_file = Path.home() / ".djinn" / "cloudflare.json"
        if config_file.exists():
            with open(config_file) as f:
                token = json.load(f).get("token")
    
    if not token:
        console.print("[error]CLOUDFLARE_API_TOKEN not set[/error]")
        console.print("[muted]Set with: djinn cf auth YOUR_TOKEN[/muted]")
        return None
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def cf_request(method, endpoint, data=None):
    """Make Cloudflare API request."""
    headers = get_cf_headers()
    if not headers:
        return None
    
    url = f"https://api.cloudflare.com/client/v4{endpoint}"
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=30)
        
        return resp.json()
    except Exception as e:
        console.print(f"[error]API Error: {e}[/error]")
        return None


@click.group()
def cf():
    """Cloudflare commands."""
    pass


@cf.command(name="auth")
@click.argument("token")
def set_auth(token):
    """Save Cloudflare API token."""
    config_file = Path.home() / ".djinn" / "cloudflare.json"
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump({"token": token}, f)
    
    console.print("[success]✓ Cloudflare token saved![/success]")


@cf.command(name="zones")
def list_zones():
    """List DNS zones."""
    result = cf_request("GET", "/zones")
    
    if not result or not result.get("success"):
        console.print(f"[error]Failed to fetch zones[/error]")
        return
    
    console.print("\n[bold cyan]🌐 DNS Zones[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Status")
    table.add_column("ID")
    
    for zone in result.get("result", []):
        status = zone["status"]
        status_color = "green" if status == "active" else "yellow"
        
        table.add_row(zone["name"], f"[{status_color}]{status}[/{status_color}]", zone["id"][:12] + "...")
    
    console.print(table)


@cf.command(name="dns")
@click.argument("zone_id")
@click.option("--type", "record_type", help="Filter by type")
def list_dns_records(zone_id, record_type):
    """List DNS records for a zone."""
    endpoint = f"/zones/{zone_id}/dns_records"
    if record_type:
        endpoint += f"?type={record_type}"
    
    result = cf_request("GET", endpoint)
    
    if not result or not result.get("success"):
        console.print(f"[error]Failed to fetch records[/error]")
        return
    
    console.print("\n[bold cyan]📋 DNS Records[/bold cyan]\n")
    
    table = Table()
    table.add_column("Type", style="cyan")
    table.add_column("Name")
    table.add_column("Content")
    table.add_column("Proxied")
    table.add_column("ID")
    
    for record in result.get("result", []):
        proxied = "🛡️" if record.get("proxied") else ""
        
        table.add_row(
            record["type"],
            record["name"],
            record["content"][:30],
            proxied,
            record["id"][:12] + "..."
        )
    
    console.print(table)


@cf.command(name="dns-add")
@click.argument("zone_id")
@click.argument("record_type")
@click.argument("name")
@click.argument("content")
@click.option("--proxied", is_flag=True)
@click.option("--ttl", default=1, type=int)
def add_dns_record(zone_id, record_type, name, content, proxied, ttl):
    """Add a DNS record."""
    data = {
        "type": record_type.upper(),
        "name": name,
        "content": content,
        "proxied": proxied,
        "ttl": ttl
    }
    
    result = cf_request("POST", f"/zones/{zone_id}/dns_records", data)
    
    if result and result.get("success"):
        console.print(f"[success]✓ Created {record_type} record for {name}[/success]")
    else:
        errors = result.get("errors", []) if result else []
        console.print(f"[error]Failed: {errors}[/error]")


@cf.command(name="dns-delete")
@click.argument("zone_id")
@click.argument("record_id")
def delete_dns_record(zone_id, record_id):
    """Delete a DNS record."""
    result = cf_request("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")
    
    if result and result.get("success"):
        console.print(f"[success]✓ Deleted record[/success]")
    else:
        console.print(f"[error]Failed to delete[/error]")


@cf.command(name="purge")
@click.argument("zone_id")
@click.option("--all", "purge_all", is_flag=True, help="Purge everything")
@click.option("--urls", help="Comma-separated URLs to purge")
def purge_cache(zone_id, purge_all, urls):
    """Purge cache for a zone."""
    if purge_all:
        data = {"purge_everything": True}
    elif urls:
        data = {"files": urls.split(",")}
    else:
        console.print("[error]Use --all or --urls[/error]")
        return
    
    result = cf_request("POST", f"/zones/{zone_id}/purge_cache", data)
    
    if result and result.get("success"):
        console.print(f"[success]✓ Cache purged![/success]")
    else:
        console.print(f"[error]Failed to purge[/error]")


@cf.command(name="workers")
def list_workers():
    """List Workers scripts."""
    result = cf_request("GET", "/accounts")
    
    if not result or not result.get("success"):
        console.print(f"[error]Failed to fetch account[/error]")
        return
    
    account_id = result["result"][0]["id"]
    
    workers = cf_request("GET", f"/accounts/{account_id}/workers/scripts")
    
    if not workers or not workers.get("success"):
        console.print(f"[error]Failed to fetch workers[/error]")
        return
    
    console.print("\n[bold cyan]⚡ Workers[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Modified")
    
    for worker in workers.get("result", []):
        table.add_row(worker["id"], worker.get("modified_on", "")[:10])
    
    console.print(table)


@cf.command(name="pages")
def list_pages_projects():
    """List Pages projects."""
    result = cf_request("GET", "/accounts")
    
    if not result or not result.get("success"):
        console.print(f"[error]Failed to fetch account[/error]")
        return
    
    account_id = result["result"][0]["id"]
    
    pages = cf_request("GET", f"/accounts/{account_id}/pages/projects")
    
    if not pages or not pages.get("success"):
        console.print(f"[error]Failed to fetch pages[/error]")
        return
    
    console.print("\n[bold cyan]📄 Pages Projects[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Subdomain")
    table.add_column("Custom Domains")
    
    for project in pages.get("result", []):
        subdomain = f"{project['subdomain']}.pages.dev"
        domains = ", ".join(project.get("domains", []))
        
        table.add_row(project["name"], subdomain, domains or "-")
    
    console.print(table)


main = cf

if __name__ == "__main__":
    cf()
