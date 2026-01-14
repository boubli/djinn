"""
Security Tools for DJINN v2.2.0
"""
import subprocess
import re
from pathlib import Path
from typing import List, Dict


class DependencyAuditor:
    """Check dependencies for known vulnerabilities."""
    
    @staticmethod
    def audit_python(requirements_file: str = "requirements.txt") -> Dict:
        """Audit Python dependencies."""
        try:
            result = subprocess.run(
                ["pip-audit", "-r", requirements_file],
                capture_output=True,
                text=True
            )
            
            return {
                "vulnerable": result.returncode != 0,
                "output": result.stdout + result.stderr
            }
        except FileNotFoundError:
            return {"error": "pip-audit not installed. Run: pip install pip-audit"}
    
    @staticmethod
    def audit_node(package_file: str = "package.json") -> Dict:
        """Audit Node dependencies."""
        try:
            result = subprocess.run(
                ["npm", "audit"],
                capture_output=True,
                text=True
            )
            
            return {
                "output": result.stdout
            }
        except FileNotFoundError:
            return {"error": "npm not found"}


class SecretScanner:
    """Scan for secrets in code before commit."""
    
    PATTERNS = {
        "AWS Key": r'AKIA[0-9A-Z]{16}',
        "API Key": r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]+)["\']',
        "Private Key": r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
        "Password": r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        "Token": r'token["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]+)["\']',
    }
    
    @staticmethod
    def scan_file(file_path: str) -> List[Dict]:
        """Scan a single file for secrets."""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for secret_type, pattern in SecretScanner.PATTERNS.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        findings.append({
                            "type": secret_type,
                            "file": file_path,
                            "match": match.group(0)[:50] + "...",
                            "line": content[:match.start()].count('\n') + 1
                        })
        except:
            pass
        
        return findings
    
    @staticmethod
    def scan_directory(directory: str = ".") -> List[Dict]:
        """Scan directory for secrets."""
        all_findings = []
        
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.go', '.rb', '.env', '.yml', '.yaml', '.json']:
                findings = SecretScanner.scan_file(str(file_path))
                all_findings.extend(findings)
        
        return all_findings
    
    @staticmethod
    def check_staged_files() -> List[Dict]:
        """Check git staged files for secrets."""
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True
            )
            
            staged_files = result.stdout.strip().split('\n')
            all_findings = []
            
            for file in staged_files:
                if file and Path(file).exists():
                    findings = SecretScanner.scan_file(file)
                    all_findings.extend(findings)
            
            return all_findings
        except:
            return []


class PermissionFixer:
    """Fix file permissions for common use cases."""
    
    @staticmethod
    def fix_ssh_keys():
        """Fix SSH key permissions."""
        ssh_dir = Path.home() / ".ssh"
        
        if not ssh_dir.exists():
            return "No .ssh directory found"
        
        fixed = []
        
        # Fix directory
        ssh_dir.chmod(0o700)
        fixed.append(f"{ssh_dir}: 700")
        
        # Fix private keys
        for key_file in ssh_dir.glob('id_*'):
            if not key_file.suffix == '.pub':
                key_file.chmod(0o600)
                fixed.append(f"{key_file.name}: 600")
        
        # Fix public keys
        for pub_file in ssh_dir.glob('*.pub'):
            pub_file.chmod(0o644)
            fixed.append(f"{pub_file.name}: 644")
        
        return "\n".join(fixed)
    
    @staticmethod
    def fix_script_permissions(directory: str = "."):
        """Make shell scripts executable."""
        fixed = []
        
        for script in Path(directory).rglob('*.sh'):
            script.chmod(0o755)
            fixed.append(str(script))
        
        return fixed


class DisposableEmail:
    """Generate temporary email addresses."""
    
    @staticmethod
    def get_temp_email() -> Dict:
        """Get a temporary email address."""
        import requests
        
        try:
            # Use temp-mail.org API (example)
            r = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
            email = r.json()[0]
            
            return {
                "email": email,
                "note": "Check messages at https://www.1secmail.com"
            }
        except:
            return {"error": "Could not generate temp email"}
    
    @staticmethod
    def check_inbox(email: str) -> List[Dict]:
        """Check inbox for temp email."""
        import requests
        
        try:
            login, domain = email.split('@')
            r = requests.get(
                f'https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}'
            )
            return r.json()
        except:
            return []
