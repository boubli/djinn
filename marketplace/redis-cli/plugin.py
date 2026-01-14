"""
Redis CLI Plugin for DJINN
Redis database management from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "redis-cli"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Redis database client."


def get_redis_client(host="localhost", port=6379, db=0, password=None):
    """Get Redis client."""
    try:
        import redis
        return redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)
    except ImportError:
        console.print("[error]redis not installed. Run: pip install redis[/error]")
        return None


@click.group()
@click.option("--host", default="localhost", help="Redis host")
@click.option("--port", default=6379, type=int, help="Redis port")
@click.option("--db", default=0, type=int, help="Database number")
@click.option("--password", help="Redis password")
@click.pass_context
def redis_cli(ctx, host, port, db, password):
    """Redis commands."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = get_redis_client(host, port, db, password)


@redis_cli.command(name="get")
@click.argument("key")
@click.pass_context
def get_key(ctx, key):
    """Get value by key."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        value = client.get(key)
        
        if value:
            console.print(f"[success]{value}[/success]")
        else:
            console.print(f"[muted](nil)[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="set")
@click.argument("key")
@click.argument("value")
@click.option("--ttl", type=int, help="Expiry in seconds")
@click.pass_context
def set_key(ctx, key, value, ttl):
    """Set key value."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        if ttl:
            client.setex(key, ttl, value)
        else:
            client.set(key, value)
        
        console.print(f"[success]OK[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="del")
@click.argument("keys", nargs=-1)
@click.pass_context
def delete_keys(ctx, keys):
    """Delete keys."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        deleted = client.delete(*keys)
        console.print(f"[success]Deleted {deleted} key(s)[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="keys")
@click.argument("pattern", default="*")
@click.pass_context
def list_keys(ctx, pattern):
    """List keys matching pattern."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        keys = client.keys(pattern)
        
        console.print(f"\n[bold cyan]🔑 Keys matching '{pattern}'[/bold cyan]\n")
        
        for key in keys[:50]:
            key_type = client.type(key)
            console.print(f"[cyan]{key}[/cyan] ({key_type})")
        
        if len(keys) > 50:
            console.print(f"\n[muted]... and {len(keys) - 50} more[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="info")
@click.pass_context
def server_info(ctx):
    """Get server info."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        info = client.info()
        
        console.print("\n[bold cyan]📊 Redis Server Info[/bold cyan]\n")
        
        table = Table()
        table.add_column("Property", style="cyan")
        table.add_column("Value")
        
        important_keys = ["redis_version", "connected_clients", "used_memory_human", 
                         "total_connections_received", "uptime_in_days", "db0"]
        
        for key in important_keys:
            if key in info:
                table.add_row(key, str(info[key]))
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="flush")
@click.option("--confirm", is_flag=True, help="Confirm flush")
@click.pass_context
def flush_db(ctx, confirm):
    """Flush current database."""
    if not confirm:
        console.print("[error]Use --confirm to flush database[/error]")
        return
    
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        client.flushdb()
        console.print(f"[success]Database flushed[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="hget")
@click.argument("key")
@click.argument("field", required=False)
@click.pass_context
def hash_get(ctx, key, field):
    """Get hash value."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        if field:
            value = client.hget(key, field)
            console.print(f"[success]{value}[/success]")
        else:
            values = client.hgetall(key)
            for k, v in values.items():
                console.print(f"[cyan]{k}[/cyan]: {v}")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@redis_cli.command(name="hset")
@click.argument("key")
@click.argument("field")
@click.argument("value")
@click.pass_context
def hash_set(ctx, key, field, value):
    """Set hash field."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        client.hset(key, field, value)
        console.print(f"[success]OK[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = redis_cli

if __name__ == "__main__":
    redis_cli()
