"""
Dependency Scanner - Check for outdated and vulnerable dependencies.
"""
import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path


class DependencyScanner:
    """Scans project dependencies for issues."""
    
    def __init__(self, directory: str = None):
        self.directory = Path(directory) if directory else Path.cwd()
    
    def detect_project_type(self) -> List[str]:
        """Detect what type of project this is."""
        types = []
        
        if (self.directory / "package.json").exists():
            types.append("npm")
        if (self.directory / "requirements.txt").exists():
            types.append("pip")
        if (self.directory / "pyproject.toml").exists():
            types.append("python")
        if (self.directory / "Cargo.toml").exists():
            types.append("rust")
        if (self.directory / "go.mod").exists():
            types.append("go")
        if (self.directory / "Gemfile").exists():
            types.append("ruby")
        if (self.directory / "composer.json").exists():
            types.append("php")
        
        return types
    
    def scan_npm(self) -> Dict:
        """Scan npm packages for vulnerabilities."""
        try:
            # Run npm audit
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            
            try:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get("vulnerabilities", {})
                
                summary = {
                    "total": len(vulnerabilities),
                    "critical": 0,
                    "high": 0,
                    "moderate": 0,
                    "low": 0,
                    "issues": []
                }
                
                for pkg, info in vulnerabilities.items():
                    severity = info.get("severity", "unknown")
                    if severity == "critical":
                        summary["critical"] += 1
                    elif severity == "high":
                        summary["high"] += 1
                    elif severity == "moderate":
                        summary["moderate"] += 1
                    else:
                        summary["low"] += 1
                    
                    summary["issues"].append({
                        "package": pkg,
                        "severity": severity,
                        "title": info.get("via", [{}])[0].get("title", "") if isinstance(info.get("via"), list) else ""
                    })
                
                return summary
            except json.JSONDecodeError:
                return {"error": "Failed to parse npm audit output"}
                
        except FileNotFoundError:
            return {"error": "npm not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_npm_outdated(self) -> List[Dict]:
        """Check for outdated npm packages."""
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            
            try:
                outdated = json.loads(result.stdout) if result.stdout else {}
                packages = []
                
                for pkg, info in outdated.items():
                    packages.append({
                        "package": pkg,
                        "current": info.get("current", "?"),
                        "wanted": info.get("wanted", "?"),
                        "latest": info.get("latest", "?")
                    })
                
                return packages
            except json.JSONDecodeError:
                return []
                
        except:
            return []
    
    def scan_pip(self) -> Dict:
        """Scan pip packages for vulnerabilities using pip-audit."""
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            
            try:
                vulnerabilities = json.loads(result.stdout) if result.stdout else []
                
                summary = {
                    "total": len(vulnerabilities),
                    "critical": 0,
                    "high": 0,
                    "issues": []
                }
                
                for vuln in vulnerabilities:
                    summary["issues"].append({
                        "package": vuln.get("name", "?"),
                        "version": vuln.get("version", "?"),
                        "vulnerability": vuln.get("id", "?"),
                        "fix_version": vuln.get("fix_versions", ["?"])[0] if vuln.get("fix_versions") else "?"
                    })
                
                return summary
            except json.JSONDecodeError:
                return {"error": "Failed to parse pip-audit output", "note": "Install with: pip install pip-audit"}
                
        except FileNotFoundError:
            return {"error": "pip-audit not found", "note": "Install with: pip install pip-audit"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_pip_outdated(self) -> List[Dict]:
        """Check for outdated pip packages."""
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            try:
                return json.loads(result.stdout) if result.stdout else []
            except:
                return []
        except:
            return []
    
    def full_scan(self) -> Dict:
        """Run a full dependency scan."""
        project_types = self.detect_project_type()
        results = {
            "project_types": project_types,
            "scans": {}
        }
        
        if "npm" in project_types:
            results["scans"]["npm"] = {
                "vulnerabilities": self.scan_npm(),
                "outdated": self.check_npm_outdated()
            }
        
        if "pip" in project_types or "python" in project_types:
            results["scans"]["pip"] = {
                "vulnerabilities": self.scan_pip(),
                "outdated": self.check_pip_outdated()
            }
        
        return results
