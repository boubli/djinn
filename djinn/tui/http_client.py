"""
HTTP Client - Interactive API testing tool.
"""
import json
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table


class HTTPClient:
    """Interactive HTTP client for API testing."""
    
    def __init__(self):
        self.console = Console()
        self.history = []
        self.headers = {"User-Agent": "DJINN HTTP Client/1.0"}
        self.base_url = None
    
    def set_base_url(self, url: str):
        """Set base URL for all requests."""
        self.base_url = url.rstrip("/")
    
    def set_header(self, key: str, value: str):
        """Set a header."""
        self.headers[key] = value
    
    def set_auth_basic(self, username: str, password: str):
        """Set basic authentication."""
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers["Authorization"] = f"Basic {credentials}"
    
    def set_auth_bearer(self, token: str):
        """Set bearer token authentication."""
        self.headers["Authorization"] = f"Bearer {token}"
    
    def _make_url(self, path: str) -> str:
        """Construct full URL."""
        if path.startswith("http"):
            return path
        if self.base_url:
            return f"{self.base_url}/{path.lstrip('/')}"
        return path
    
    def request(self, method: str, url: str, data: Dict = None, 
                headers: Dict = None) -> Dict:
        """Make an HTTP request."""
        import requests
        
        full_url = self._make_url(url)
        req_headers = {**self.headers, **(headers or {})}
        
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(full_url, headers=req_headers, params=data, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(full_url, headers=req_headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(full_url, headers=req_headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(full_url, headers=req_headers, timeout=30)
            elif method.upper() == "PATCH":
                response = requests.patch(full_url, headers=req_headers, json=data, timeout=30)
            else:
                return {"error": f"Unknown method: {method}"}
            
            elapsed = time.time() - start_time
            
            result = {
                "status": response.status_code,
                "url": full_url,
                "method": method.upper(),
                "time_ms": int(elapsed * 1000),
                "headers": dict(response.headers),
                "size": len(response.content),
            }
            
            # Parse response body
            try:
                result["body"] = response.json()
                result["content_type"] = "json"
            except:
                result["body"] = response.text[:5000]
                result["content_type"] = "text"
            
            self.history.append(result)
            return result
            
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection failed"}
        except Exception as e:
            return {"error": str(e)}
    
    def get(self, url: str, params: Dict = None) -> Dict:
        """Make GET request."""
        return self.request("GET", url, params)
    
    def post(self, url: str, data: Dict = None) -> Dict:
        """Make POST request."""
        return self.request("POST", url, data)
    
    def put(self, url: str, data: Dict = None) -> Dict:
        """Make PUT request."""
        return self.request("PUT", url, data)
    
    def delete(self, url: str) -> Dict:
        """Make DELETE request."""
        return self.request("DELETE", url)
    
    def patch(self, url: str, data: Dict = None) -> Dict:
        """Make PATCH request."""
        return self.request("PATCH", url, data)
    
    def render_response(self, response: Dict) -> None:
        """Render a response nicely."""
        if "error" in response:
            self.console.print(f"[red]Error: {response['error']}[/red]")
            return
        
        # Status line
        status = response["status"]
        status_color = "green" if status < 300 else "yellow" if status < 400 else "red"
        
        self.console.print(f"\n[{status_color}]{response['method']} {response['url']}[/{status_color}]")
        self.console.print(f"[{status_color}]Status: {status}[/{status_color}] | Time: {response['time_ms']}ms | Size: {response['size']} bytes")
        
        # Body
        if response["content_type"] == "json":
            syntax = Syntax(
                json.dumps(response["body"], indent=2),
                "json",
                theme="monokai"
            )
            self.console.print(Panel(syntax, title="Response Body"))
        else:
            self.console.print(Panel(response["body"][:1000], title="Response Body"))
    
    def get_history(self) -> List[Dict]:
        """Get request history."""
        return self.history[-20:]  # Last 20 requests
    
    def export_curl(self, method: str, url: str, data: Dict = None) -> str:
        """Export request as curl command."""
        full_url = self._make_url(url)
        
        cmd = f"curl -X {method.upper()}"
        
        for key, value in self.headers.items():
            cmd += f" -H '{key}: {value}'"
        
        if data:
            cmd += f" -d '{json.dumps(data)}'"
        
        cmd += f" '{full_url}'"
        
        return cmd


class APITester:
    """Test API endpoints with predefined tests."""
    
    def __init__(self, base_url: str):
        self.client = HTTPClient()
        self.client.set_base_url(base_url)
        self.tests = []
        self.results = []
    
    def add_test(self, name: str, method: str, path: str, 
                 data: Dict = None, expected_status: int = 200):
        """Add a test case."""
        self.tests.append({
            "name": name,
            "method": method,
            "path": path,
            "data": data,
            "expected_status": expected_status,
        })
    
    def run_tests(self) -> List[Dict]:
        """Run all tests."""
        self.results = []
        
        for test in self.tests:
            response = self.client.request(test["method"], test["path"], test["data"])
            
            passed = (
                "error" not in response and 
                response.get("status") == test["expected_status"]
            )
            
            self.results.append({
                "name": test["name"],
                "passed": passed,
                "expected": test["expected_status"],
                "actual": response.get("status", "ERROR"),
                "time_ms": response.get("time_ms", 0),
            })
        
        return self.results
    
    def print_results(self) -> None:
        """Print test results."""
        console = Console()
        
        table = Table(title="API Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status")
        table.add_column("Expected")
        table.add_column("Actual")
        table.add_column("Time")
        
        for result in self.results:
            status = "[green]✓ PASS[/green]" if result["passed"] else "[red]✗ FAIL[/red]"
            table.add_row(
                result["name"],
                status,
                str(result["expected"]),
                str(result["actual"]),
                f"{result['time_ms']}ms"
            )
        
        console.print(table)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")
