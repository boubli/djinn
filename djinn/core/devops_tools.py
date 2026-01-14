"""
DevOps & Automation Tools for DJINN v2.2.0
"""
import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict
import socket


class SpellsManager:
    """Record and replay command sequences (macros)."""
    
    def __init__(self):
        self.spells_file = Path.home() / ".djinn" / "spells.json"
        self.spells_file.parent.mkdir(exist_ok=True)
    
    def save_spell(self, name: str, commands: List[str]):
        """Save a command sequence as a spell."""
        spells = self.load_all()
        spells[name] = {
            "commands": commands,
            "created": str(Path.cwd())
        }
        
        with open(self.spells_file, 'w') as f:
            json.dump(spells, f, indent=2)
    
    def load_all(self) -> Dict:
        """Load all saved spells."""
        if not self.spells_file.exists():
            return {}
        
        with open(self.spells_file) as f:
            return json.load(f)
    
    def cast_spell(self, name: str) -> List[str]:
        """Retrieve a spell's commands."""
        spells = self.load_all()
        return spells.get(name, {}).get("commands", [])


class CronWizard:
    """Convert natural language to crontab entries."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def generate_cron(self, description: str) -> str:
        """Generate cron expression from description."""
        prompt = f"""Convert this to a crontab expression:

"{description}"

Return ONLY the cron expression (5 fields) with no explanation.
Format: minute hour day month weekday

Examples:
- "every day at 2am" → 0 2 * * *
- "every monday at 9am" → 0 9 * * 1
- "every 5 minutes" → */5 * * * *

Cron expression:"""
        
        cron = self.engine.backend.generate(
            prompt,
            system_prompt="You are a cron expert. Return only the cron expression."
        ).strip()
        
        return cron


class DockerComposer:
    """Generate docker-compose.yml from natural language."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def generate_compose(self, description: str) -> str:
        """Generate docker-compose.yml content."""
        prompt = f"""Generate a docker-compose.yml file for:

{description}

Include:
- Proper version
- Service definitions
- Volumes if needed
- Networks if needed
- Environment variables

Return ONLY valid YAML:"""
        
        compose = self.engine.backend.generate(
            prompt,
            system_prompt="You are a Docker expert. Generate clean, valid docker-compose files."
        )
        
        return compose
    
    def save_and_run(self, compose_content: str, filename: str = "docker-compose.yml"):
        """Save compose file and start services."""
        with open(filename, 'w') as f:
            f.write(compose_content)
        
        # Start services
        subprocess.run(["docker-compose", "up", "-d"])


class PortKiller:
    """Find and kill processes on specific ports."""
    
    @staticmethod
    def find_process_on_port(port: int) -> int:
        """Find PID using a port."""
        import psutil
        
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return conn.pid
        return None
    
    @staticmethod
    def kill_port(port: int) -> bool:
        """Kill process on port."""
        import psutil
        
        pid = PortKiller.find_process_on_port(port)
        if pid:
            try:
                proc = psutil.Process(pid)
                proc.kill()
                return True
            except:
                return False
        return False


class SSLChecker:
    """Check SSL certificate expiry."""
    
    @staticmethod
    def check_ssl(domain: str) -> Dict:
        """Check SSL certificate for domain."""
        import ssl
        import socket
        from datetime import datetime
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiry date
                    expiry_str = cert['notAfter']
                    expiry = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                    days_left = (expiry - datetime.now()).days
                    
                    return {
                        "domain": domain,
                        "expiry": expiry_str,
                        "days_left": days_left,
                        "valid": days_left > 0,
                        "issuer": cert.get('issuer', 'Unknown')
                    }
        except Exception as e:
            return {
                "domain": domain,
                "error": str(e),
                "valid": False
            }


class NetworkTools:
    """Various network utilities."""
    
    @staticmethod
    def get_public_ip() -> Dict:
        """Get public IP and geolocation."""
        import requests
        
        try:
            r = requests.get('https://ipapi.co/json/', timeout=5)
            return r.json()
        except:
            return {"error": "Could not fetch IP info"}
    
    @staticmethod
    def whois_domain(domain: str) -> str:
        """Check domain availability (basic)."""
        import socket
        
        try:
            socket.gethostbyname(domain)
            return f"{domain} is registered"
        except socket.gaierror:
            return f"{domain} might be available"
    
    @staticmethod
    def check_dns_propagation(domain: str) -> Dict:
        """Check DNS propagation across servers."""
        import dns.resolver
        
        nameservers = [
            ('Google', '8.8.8.8'),
            ('Cloudflare', '1.1.1.1'),
            ('Quad9', '9.9.9.9'),
        ]
        
        results = {}
        for name, ns in nameservers:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [ns]
                answer = resolver.resolve(domain, 'A')
                results[name] = [str(rdata) for rdata in answer]
            except Exception as e:
                results[name] = f"Error: {e}"
        
        return results
    
    @staticmethod
    def speed_test() -> Dict:
        """Run network speed test."""
        try:
            import speedtest
            
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download = st.download() / 1_000_000  # Convert to Mbps
            upload = st.upload() / 1_000_000
            ping = st.results.ping
            
            return {
                "download_mbps": round(download, 2),
                "upload_mbps": round(upload, 2),
                "ping_ms": round(ping, 2)
            }
        except ImportError:
            return {"error": "speedtest-cli not installed. Run: pip install speedtest-cli"}
        except Exception as e:
            return {"error": str(e)}


class HTTPServer:
    """Simple HTTP server with auto-reload."""
    
    @staticmethod
    def serve(directory: str = ".", port: int = 8000):
        """Start HTTP server."""
        import http.server
        import socketserver
        import os
        
        os.chdir(directory)
        
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Serving at http://localhost:{port}")
            httpd.serve_forever()


class TunnelManager:
    """Tunnel local ports with ngrok/localtunnel."""
    
    @staticmethod
    def create_tunnel(port: int, service: str = "ngrok") -> str:
        """Create tunnel for local port."""
        if service == "ngrok":
            # Try ngrok
            try:
                from pyngrok import ngrok
                tunnel = ngrok.connect(port)
                return tunnel.public_url
            except:
                return "ngrok not available. Install: pip install pyngrok"
        elif service == "localtunnel":
            # Try localtunnel (requires npm install -g localtunnel)
            result = subprocess.run(
                ["lt", "--port", str(port)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Extract URL from output
                for line in result.stdout.split('\n'):
                    if 'https://' in line:
                        return line.strip()
            return "localtunnel not available. Install: npm install -g localtunnel"
        
        return "Unknown service"
