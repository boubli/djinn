"""
Elasticsearch Plugin for DJINN
Elasticsearch cluster management and queries.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
import json

console = Console()

PLUGIN_NAME = "elasticsearch"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Elasticsearch management and queries."


def get_es_client(host="localhost", port=9200):
    """Get Elasticsearch client."""
    try:
        from elasticsearch import Elasticsearch
        return Elasticsearch([f"http://{host}:{port}"])
    except ImportError:
        console.print("[error]elasticsearch not installed. Run: pip install elasticsearch[/error]")
        return None


@click.group()
@click.option("--host", default="localhost", help="ES host")
@click.option("--port", default=9200, type=int, help="ES port")
@click.pass_context
def es(ctx, host, port):
    """Elasticsearch commands."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = get_es_client(host, port)


@es.command(name="health")
@click.pass_context
def cluster_health(ctx):
    """Check cluster health."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        health = client.cluster.health()
        
        status = health["status"]
        status_color = {"green": "success", "yellow": "warning", "red": "error"}
        color = status_color.get(status, "white")
        
        console.print(f"\n[bold cyan]🏥 Cluster Health[/bold cyan]\n")
        console.print(f"Status: [{color}]{status}[/{color}]")
        console.print(f"Nodes: {health['number_of_nodes']}")
        console.print(f"Shards: {health['active_shards']} active, {health['unassigned_shards']} unassigned")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@es.command(name="indices")
@click.pass_context
def list_indices(ctx):
    """List all indices."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        indices = client.cat.indices(format="json")
        
        console.print("\n[bold cyan]📊 Indices[/bold cyan]\n")
        
        table = Table()
        table.add_column("Index", style="cyan")
        table.add_column("Health")
        table.add_column("Docs")
        table.add_column("Size")
        
        for idx in indices:
            health = idx.get("health", "unknown")
            health_color = {"green": "success", "yellow": "warning", "red": "error"}
            color = health_color.get(health, "white")
            
            table.add_row(
                idx.get("index", ""),
                f"[{color}]{health}[/{color}]",
                str(idx.get("docs.count", 0)),
                idx.get("store.size", "")
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@es.command(name="search")
@click.argument("index")
@click.argument("query")
@click.option("--size", default=10, help="Number of results")
@click.pass_context
def search_index(ctx, index, query, size):
    """Search an index."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        # Try to parse as JSON first, otherwise use query string
        try:
            query_body = json.loads(query)
        except:
            query_body = {"query": {"query_string": {"query": query}}}
        
        results = client.search(index=index, body=query_body, size=size)
        
        console.print(f"\n[bold cyan]🔍 Results ({results['hits']['total']['value']} total)[/bold cyan]\n")
        
        for hit in results["hits"]["hits"]:
            console.print(f"[cyan]ID:[/cyan] {hit['_id']} (score: {hit['_score']:.2f})")
            
            source = json.dumps(hit["_source"], indent=2)
            if len(source) > 200:
                source = source[:200] + "..."
            
            syntax = Syntax(source, "json", theme="monokai")
            console.print(syntax)
            console.print()
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@es.command(name="create")
@click.argument("index")
@click.option("--shards", default=1, type=int)
@click.option("--replicas", default=0, type=int)
@click.pass_context
def create_index(ctx, index, shards, replicas):
    """Create an index."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        body = {
            "settings": {
                "number_of_shards": shards,
                "number_of_replicas": replicas
            }
        }
        
        client.indices.create(index=index, body=body)
        console.print(f"[success]✓ Index '{index}' created[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@es.command(name="delete")
@click.argument("index")
@click.option("--confirm", is_flag=True)
@click.pass_context
def delete_index(ctx, index, confirm):
    """Delete an index."""
    if not confirm:
        console.print("[error]Use --confirm to delete index[/error]")
        return
    
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        client.indices.delete(index=index)
        console.print(f"[success]✓ Index '{index}' deleted[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@es.command(name="doc")
@click.argument("index")
@click.argument("doc_id")
@click.pass_context
def get_document(ctx, index, doc_id):
    """Get a document by ID."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        doc = client.get(index=index, id=doc_id)
        
        source = json.dumps(doc["_source"], indent=2)
        syntax = Syntax(source, "json", theme="monokai")
        console.print(syntax)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@es.command(name="index-doc")
@click.argument("index")
@click.argument("json_data")
@click.option("--id", "doc_id", help="Document ID")
@click.pass_context
def index_document(ctx, index, json_data, doc_id):
    """Index a document."""
    client = ctx.obj["client"]
    if not client:
        return
    
    try:
        body = json.loads(json_data)
        
        params = {"index": index, "body": body}
        if doc_id:
            params["id"] = doc_id
        
        result = client.index(**params)
        console.print(f"[success]✓ Indexed with ID: {result['_id']}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = es

if __name__ == "__main__":
    es()
