"""
Supabase Plugin for DJINN
Supabase database and auth management.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "supabase"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Supabase database, auth, and storage."

CONFIG_FILE = Path.home() / ".djinn" / "supabase.json"


def get_supabase_client():
    """Get Supabase client."""
    try:
        from supabase import create_client, Client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
                    url = config.get("url")
                    key = config.get("key")
        
        if not url or not key:
            console.print("[error]Supabase credentials not set[/error]")
            console.print("[muted]Run: djinn supabase auth URL KEY[/muted]")
            return None
        
        return create_client(url, key)
    except ImportError:
        console.print("[error]supabase not installed. Run: pip install supabase[/error]")
        return None


@click.group()
def supabase():
    """Supabase commands."""
    pass


@supabase.command(name="auth")
@click.argument("url")
@click.argument("key")
def set_auth(url, key):
    """Save Supabase credentials."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"url": url, "key": key}, f)
    
    console.print("[success]✓ Supabase credentials saved![/success]")


@supabase.command(name="tables")
def list_tables():
    """List database tables."""
    client = get_supabase_client()
    if not client:
        return
    
    console.print("\n[bold cyan]📊 Tables[/bold cyan]\n")
    
    try:
        # Query pg_tables
        result = client.rpc("get_tables", {}).execute()
        
        if result.data:
            for table in result.data:
                console.print(f"• {table}")
        else:
            console.print("[muted]No tables found or function not available[/muted]")
            console.print("[muted]Create RPC function 'get_tables' or use dashboard[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")
        console.print("[muted]Tip: View tables in Supabase Dashboard[/muted]")


@supabase.command(name="select")
@click.argument("table")
@click.option("--columns", default="*", help="Columns to select")
@click.option("--limit", default=20, type=int)
@click.option("--filter", "filter_expr", help="Filter (e.g., 'id.eq.1')")
def select_data(table, columns, limit, filter_expr):
    """Select data from a table."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        query = client.table(table).select(columns).limit(limit)
        
        if filter_expr:
            # Parse filter like "column.op.value"
            parts = filter_expr.split(".", 2)
            if len(parts) == 3:
                col, op, val = parts
                if op == "eq":
                    query = query.eq(col, val)
                elif op == "neq":
                    query = query.neq(col, val)
                elif op == "gt":
                    query = query.gt(col, val)
                elif op == "lt":
                    query = query.lt(col, val)
                elif op == "like":
                    query = query.like(col, f"%{val}%")
        
        result = query.execute()
        
        console.print(f"\n[bold cyan]📋 {table}[/bold cyan]\n")
        
        if result.data:
            data_json = json.dumps(result.data, indent=2, default=str)
            syntax = Syntax(data_json, "json", theme="monokai")
            console.print(syntax)
            console.print(f"\n[muted]{len(result.data)} rows[/muted]")
        else:
            console.print("[muted]No data[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@supabase.command(name="insert")
@click.argument("table")
@click.argument("data")
def insert_data(table, data):
    """Insert data into a table."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        parsed_data = json.loads(data)
        
        result = client.table(table).insert(parsed_data).execute()
        
        console.print(f"[success]✓ Inserted into {table}[/success]")
        
        if result.data:
            console.print(f"[muted]ID: {result.data[0].get('id', 'N/A')}[/muted]")
    except json.JSONDecodeError:
        console.print("[error]Invalid JSON data[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@supabase.command(name="update")
@click.argument("table")
@click.argument("data")
@click.option("--filter", "filter_expr", required=True, help="Filter (e.g., 'id.eq.1')")
def update_data(table, data, filter_expr):
    """Update data in a table."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        parsed_data = json.loads(data)
        
        query = client.table(table).update(parsed_data)
        
        # Parse filter
        parts = filter_expr.split(".", 2)
        if len(parts) == 3:
            col, op, val = parts
            if op == "eq":
                query = query.eq(col, val)
        
        result = query.execute()
        
        console.print(f"[success]✓ Updated {len(result.data)} row(s) in {table}[/success]")
    except json.JSONDecodeError:
        console.print("[error]Invalid JSON data[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@supabase.command(name="delete")
@click.argument("table")
@click.option("--filter", "filter_expr", required=True, help="Filter (e.g., 'id.eq.1')")
@click.option("--confirm", is_flag=True)
def delete_data(table, filter_expr, confirm):
    """Delete data from a table."""
    if not confirm:
        console.print("[error]Use --confirm to delete[/error]")
        return
    
    client = get_supabase_client()
    if not client:
        return
    
    try:
        query = client.table(table).delete()
        
        # Parse filter
        parts = filter_expr.split(".", 2)
        if len(parts) == 3:
            col, op, val = parts
            if op == "eq":
                query = query.eq(col, val)
        
        result = query.execute()
        
        console.print(f"[success]✓ Deleted from {table}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@supabase.command(name="rpc")
@click.argument("function_name")
@click.option("--params", default="{}", help="JSON params")
def call_rpc(function_name, params):
    """Call a database function."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        parsed_params = json.loads(params)
        
        result = client.rpc(function_name, parsed_params).execute()
        
        console.print(f"\n[bold cyan]📋 Result[/bold cyan]\n")
        
        if result.data:
            data_json = json.dumps(result.data, indent=2, default=str)
            syntax = Syntax(data_json, "json", theme="monokai")
            console.print(syntax)
        else:
            console.print("[muted]No result[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@supabase.command(name="storage")
@click.argument("action", type=click.Choice(["list", "upload", "download", "delete"]))
@click.argument("bucket")
@click.argument("path", required=False)
@click.option("--local", help="Local file path")
def storage_ops(action, bucket, path, local):
    """Storage operations."""
    client = get_supabase_client()
    if not client:
        return
    
    try:
        if action == "list":
            result = client.storage.from_(bucket).list(path or "")
            
            console.print(f"\n[bold cyan]📁 {bucket}/{path or ''}[/bold cyan]\n")
            
            for item in result:
                icon = "📁" if item.get("id") is None else "📄"
                console.print(f"{icon} {item['name']}")
        
        elif action == "upload":
            if not path or not local:
                console.print("[error]--local and path required[/error]")
                return
            
            with open(local, 'rb') as f:
                client.storage.from_(bucket).upload(path, f)
            
            console.print(f"[success]✓ Uploaded to {bucket}/{path}[/success]")
        
        elif action == "download":
            if not path or not local:
                console.print("[error]--local and path required[/error]")
                return
            
            data = client.storage.from_(bucket).download(path)
            
            with open(local, 'wb') as f:
                f.write(data)
            
            console.print(f"[success]✓ Downloaded to {local}[/success]")
        
        elif action == "delete":
            if not path:
                console.print("[error]path required[/error]")
                return
            
            client.storage.from_(bucket).remove([path])
            console.print(f"[success]✓ Deleted {path}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = supabase

if __name__ == "__main__":
    supabase()
