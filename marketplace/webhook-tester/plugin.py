"""
Webhook Tester Plugin for DJINN
Test webhooks and expose local servers.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
import http.server
import socketserver
import threading
import json
import time
from pathlib import Path
from datetime import datetime

console = Console()

PLUGIN_NAME = "webhook-tester"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Test webhooks and capture HTTP requests."

REQUESTS_LOG = []


class WebhookHandler(http.server.BaseHTTPRequestHandler):
    """Handle incoming webhook requests."""
    
    def log_message(self, format, *args):
        pass  # Suppress default logging
    
    def _handle_request(self, method):
        """Handle any HTTP method."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""
        
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "path": self.path,
            "headers": dict(self.headers),
            "body": body
        }
        
        REQUESTS_LOG.append(request_data)
        
        # Print to console
        console.print(f"\n[bold green]📥 {method}[/bold green] {self.path}")
        console.print(f"[muted]Headers: {len(self.headers)} | Body: {len(body)} bytes[/muted]")
        
        if body:
            try:
                parsed = json.loads(body)
                formatted = json.dumps(parsed, indent=2)
                syntax = Syntax(formatted[:500], "json", theme="monokai")
                console.print(syntax)
            except:
                console.print(f"[muted]{body[:200]}[/muted]")
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "received", "timestamp": request_data["timestamp"]}
        self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        self._handle_request("GET")
    
    def do_POST(self):
        self._handle_request("POST")
    
    def do_PUT(self):
        self._handle_request("PUT")
    
    def do_DELETE(self):
        self._handle_request("DELETE")
    
    def do_PATCH(self):
        self._handle_request("PATCH")


@click.group()
def webhook():
    """Webhook testing commands."""
    pass


@webhook.command(name="listen")
@click.option("--port", default=8080, type=int, help="Port to listen on")
@click.option("--save", help="Save requests to file")
def start_listener(port, save):
    """Start webhook listener server."""
    console.print(f"\n[bold cyan]🎯 Webhook Listener[/bold cyan]")
    console.print(f"[success]Listening on http://localhost:{port}[/success]")
    console.print("[muted]Press Ctrl+C to stop[/muted]\n")
    console.print("[bold]Waiting for requests...[/bold]\n")
    
    try:
        with socketserver.TCPServer(("", port), WebhookHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[muted]Stopping server...[/muted]")
        
        if save and REQUESTS_LOG:
            with open(save, 'w') as f:
                json.dump(REQUESTS_LOG, f, indent=2)
            console.print(f"[success]✓ Saved {len(REQUESTS_LOG)} requests to {save}[/success]")


@webhook.command(name="send")
@click.argument("url")
@click.option("--method", default="POST", help="HTTP method")
@click.option("--data", "-d", help="JSON data")
@click.option("--header", "-H", multiple=True, help="Headers")
@click.option("--repeat", default=1, type=int, help="Number of times to send")
@click.option("--delay", default=0, type=float, help="Delay between requests")
def send_webhook(url, method, data, header, repeat, delay):
    """Send test webhook request."""
    import requests
    
    headers = {"Content-Type": "application/json"}
    for h in header:
        key, value = h.split(":", 1)
        headers[key.strip()] = value.strip()
    
    body = json.loads(data) if data else {"test": True, "timestamp": datetime.now().isoformat()}
    
    console.print(f"\n[bold cyan]📤 Sending Webhook[/bold cyan]")
    console.print(f"[muted]{method} {url}[/muted]\n")
    
    for i in range(repeat):
        try:
            start = time.time()
            
            if method.upper() == "GET":
                resp = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                resp = requests.post(url, json=body, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                resp = requests.put(url, json=body, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                resp = requests.delete(url, headers=headers, timeout=30)
            else:
                resp = requests.request(method.upper(), url, json=body, headers=headers, timeout=30)
            
            elapsed = (time.time() - start) * 1000
            
            status_color = "green" if resp.status_code < 400 else "red"
            console.print(f"[{status_color}]{resp.status_code}[/{status_color}] - {elapsed:.0f}ms")
            
            if repeat > 1 and i < repeat - 1 and delay > 0:
                time.sleep(delay)
        
        except Exception as e:
            console.print(f"[error]Error: {e}[/error]")
    
    if repeat > 1:
        console.print(f"\n[success]✓ Sent {repeat} requests[/success]")


@webhook.command(name="mock")
@click.option("--port", default=8080, type=int)
@click.option("--response", default='{"status": "ok"}', help="JSON response")
@click.option("--status", default=200, type=int, help="HTTP status code")
@click.option("--delay", default=0, type=float, help="Response delay in seconds")
def mock_server(port, response, status, delay):
    """Start mock API server with custom responses."""
    
    class MockHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
        
        def _respond(self):
            if delay > 0:
                time.sleep(delay)
            
            self.send_response(status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
            
            console.print(f"[green]→[/green] {self.command} {self.path} → {status}")
        
        def do_GET(self): self._respond()
        def do_POST(self): self._respond()
        def do_PUT(self): self._respond()
        def do_DELETE(self): self._respond()
    
    console.print(f"\n[bold cyan]🎭 Mock Server[/bold cyan]")
    console.print(f"[success]Listening on http://localhost:{port}[/success]")
    console.print(f"[muted]Response: {response[:50]}...[/muted]")
    console.print(f"[muted]Status: {status}[/muted]")
    console.print("[muted]Press Ctrl+C to stop[/muted]\n")
    
    try:
        with socketserver.TCPServer(("", port), MockHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[muted]Server stopped[/muted]")


@webhook.command(name="inspect")
@click.argument("file_path")
def inspect_requests(file_path):
    """Inspect saved webhook requests."""
    try:
        with open(file_path) as f:
            requests_data = json.load(f)
        
        console.print(f"\n[bold cyan]📋 Saved Requests ({len(requests_data)})[/bold cyan]\n")
        
        table = Table()
        table.add_column("#")
        table.add_column("Method", style="cyan")
        table.add_column("Path")
        table.add_column("Time")
        table.add_column("Body Size")
        
        for i, req in enumerate(requests_data, 1):
            table.add_row(
                str(i),
                req["method"],
                req["path"][:30],
                req["timestamp"][11:19],
                f"{len(req.get('body', ''))} bytes"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = webhook

if __name__ == "__main__":
    webhook()
