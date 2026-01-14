"""
Database CLI Plugin for DJINN
Connect to PostgreSQL, MySQL, SQLite, MongoDB from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "database-cli"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Universal database client for PostgreSQL, MySQL, SQLite, MongoDB."

CONNECTIONS_FILE = Path.home() / ".djinn" / "db_connections.json"


def load_connections():
    """Load saved database connections."""
    if CONNECTIONS_FILE.exists():
        with open(CONNECTIONS_FILE) as f:
            return json.load(f)
    return {}


def save_connections(connections):
    """Save database connections."""
    CONNECTIONS_FILE.parent.mkdir(exist_ok=True)
    with open(CONNECTIONS_FILE, 'w') as f:
        json.dump(connections, f, indent=2)


@click.group()
def db():
    """Database CLI commands."""
    pass


@db.command(name="connect")
@click.argument("alias")
@click.option("--type", "db_type", type=click.Choice(["postgres", "mysql", "sqlite", "mongodb"]), required=True)
@click.option("--host", default="localhost")
@click.option("--port", type=int)
@click.option("--database", required=True)
@click.option("--user")
@click.option("--password", hide_input=True)
def add_connection(alias, db_type, host, port, database, user, password):
    """Save a database connection."""
    default_ports = {"postgres": 5432, "mysql": 3306, "mongodb": 27017}
    
    connections = load_connections()
    connections[alias] = {
        "type": db_type,
        "host": host,
        "port": port or default_ports.get(db_type),
        "database": database,
        "user": user,
        "password": password
    }
    save_connections(connections)
    
    console.print(f"[success]✓ Connection '{alias}' saved![/success]")


@db.command(name="list")
def list_connections():
    """List saved connections."""
    connections = load_connections()
    
    if not connections:
        console.print("[muted]No saved connections[/muted]")
        return
    
    console.print("\n[bold cyan]📊 Database Connections[/bold cyan]\n")
    
    table = Table()
    table.add_column("Alias", style="cyan")
    table.add_column("Type")
    table.add_column("Host")
    table.add_column("Database")
    
    for alias, conn in connections.items():
        table.add_row(alias, conn["type"], f"{conn['host']}:{conn.get('port', '')}", conn["database"])
    
    console.print(table)


@db.command(name="query")
@click.argument("alias")
@click.argument("sql")
@click.option("--limit", default=50, help="Max rows to show")
def run_query(alias, sql, limit):
    """Run SQL query on a connection."""
    connections = load_connections()
    
    if alias not in connections:
        console.print(f"[error]Connection '{alias}' not found[/error]")
        return
    
    conn_info = connections[alias]
    db_type = conn_info["type"]
    
    try:
        if db_type == "postgres":
            import psycopg2
            conn = psycopg2.connect(
                host=conn_info["host"],
                port=conn_info["port"],
                database=conn_info["database"],
                user=conn_info["user"],
                password=conn_info["password"]
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchmany(limit)
                
                table = Table()
                for col in columns:
                    table.add_column(col)
                
                for row in rows:
                    table.add_row(*[str(v) for v in row])
                
                console.print(table)
                console.print(f"\n[muted]Showing {len(rows)} rows[/muted]")
            else:
                conn.commit()
                console.print(f"[success]✓ Query executed. Rows affected: {cursor.rowcount}[/success]")
            
            conn.close()
        
        elif db_type == "mysql":
            import mysql.connector
            conn = mysql.connector.connect(
                host=conn_info["host"],
                port=conn_info["port"],
                database=conn_info["database"],
                user=conn_info["user"],
                password=conn_info["password"]
            )
            cursor = conn.cursor()
            cursor.execute(sql)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchmany(limit)
                
                table = Table()
                for col in columns:
                    table.add_column(col)
                
                for row in rows:
                    table.add_row(*[str(v) for v in row])
                
                console.print(table)
            else:
                conn.commit()
                console.print(f"[success]✓ Query executed[/success]")
            
            conn.close()
        
        elif db_type == "sqlite":
            import sqlite3
            conn = sqlite3.connect(conn_info["database"])
            cursor = conn.cursor()
            cursor.execute(sql)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchmany(limit)
                
                table = Table()
                for col in columns:
                    table.add_column(col)
                
                for row in rows:
                    table.add_row(*[str(v) for v in row])
                
                console.print(table)
            else:
                conn.commit()
                console.print(f"[success]✓ Query executed[/success]")
            
            conn.close()
        
        elif db_type == "mongodb":
            from pymongo import MongoClient
            
            client = MongoClient(
                host=conn_info["host"],
                port=conn_info["port"],
                username=conn_info.get("user"),
                password=conn_info.get("password")
            )
            
            db = client[conn_info["database"]]
            # Parse MongoDB query (simplified - expects collection.find format)
            console.print("[muted]Use: djinn db mongo <alias> for MongoDB operations[/muted]")
    
    except ImportError as e:
        console.print(f"[error]Missing driver: {e}[/error]")
        console.print("[muted]Install with: pip install psycopg2-binary / mysql-connector-python / pymongo[/muted]")
    except Exception as e:
        console.print(f"[error]Query error: {e}[/error]")


@db.command(name="tables")
@click.argument("alias")
def show_tables(alias):
    """List tables in database."""
    connections = load_connections()
    
    if alias not in connections:
        console.print(f"[error]Connection '{alias}' not found[/error]")
        return
    
    conn_info = connections[alias]
    db_type = conn_info["type"]
    
    table_queries = {
        "postgres": "SELECT tablename FROM pg_tables WHERE schemaname = 'public'",
        "mysql": "SHOW TABLES",
        "sqlite": "SELECT name FROM sqlite_master WHERE type='table'"
    }
    
    if db_type in table_queries:
        # Reuse query command
        run_query.callback(alias, table_queries[db_type], 100)
    else:
        console.print(f"[muted]Use 'show collections' for MongoDB[/muted]")


@db.command(name="schema")
@click.argument("alias")
@click.argument("table_name")
def show_schema(alias, table_name):
    """Show table schema."""
    connections = load_connections()
    
    if alias not in connections:
        console.print(f"[error]Connection '{alias}' not found[/error]")
        return
    
    conn_info = connections[alias]
    db_type = conn_info["type"]
    
    schema_queries = {
        "postgres": f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table_name}'",
        "mysql": f"DESCRIBE {table_name}",
        "sqlite": f"PRAGMA table_info({table_name})"
    }
    
    if db_type in schema_queries:
        run_query.callback(alias, schema_queries[db_type], 100)


main = db

if __name__ == "__main__":
    db()
