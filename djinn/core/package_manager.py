"""
Universal Package Manager - Smart package management across all ecosystems.
"""
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class UniversalPackageManager:
    """Unified interface for all package managers."""
    
    MANAGERS = {
        "npm": {
            "detect": ["package.json"],
            "install": "npm install {pkg}",
            "install_dev": "npm install -D {pkg}",
            "uninstall": "npm uninstall {pkg}",
            "list": "npm list --depth=0",
            "update": "npm update",
            "outdated": "npm outdated",
            "search": "npm search {query}",
        },
        "yarn": {
            "detect": ["yarn.lock"],
            "install": "yarn add {pkg}",
            "install_dev": "yarn add -D {pkg}",
            "uninstall": "yarn remove {pkg}",
            "list": "yarn list --depth=0",
            "update": "yarn upgrade",
            "outdated": "yarn outdated",
        },
        "pnpm": {
            "detect": ["pnpm-lock.yaml"],
            "install": "pnpm add {pkg}",
            "install_dev": "pnpm add -D {pkg}",
            "uninstall": "pnpm remove {pkg}",
            "list": "pnpm list --depth=0",
            "update": "pnpm update",
        },
        "pip": {
            "detect": ["requirements.txt", "setup.py", "pyproject.toml"],
            "install": "pip install {pkg}",
            "install_dev": "pip install {pkg}",
            "uninstall": "pip uninstall -y {pkg}",
            "list": "pip list",
            "update": "pip install --upgrade {pkg}",
            "outdated": "pip list --outdated",
            "search": "pip index versions {query}",
        },
        "poetry": {
            "detect": ["poetry.lock"],
            "install": "poetry add {pkg}",
            "install_dev": "poetry add -D {pkg}",
            "uninstall": "poetry remove {pkg}",
            "list": "poetry show",
            "update": "poetry update",
        },
        "cargo": {
            "detect": ["Cargo.toml"],
            "install": "cargo add {pkg}",
            "uninstall": "cargo remove {pkg}",
            "list": "cargo tree --depth=1",
            "update": "cargo update",
        },
        "go": {
            "detect": ["go.mod"],
            "install": "go get {pkg}",
            "uninstall": "go mod edit -droprequire {pkg}",
            "list": "go list -m all",
            "update": "go get -u {pkg}",
        },
        "gem": {
            "detect": ["Gemfile"],
            "install": "gem install {pkg}",
            "uninstall": "gem uninstall {pkg}",
            "list": "gem list",
            "update": "gem update {pkg}",
            "outdated": "gem outdated",
        },
        "composer": {
            "detect": ["composer.json"],
            "install": "composer require {pkg}",
            "install_dev": "composer require --dev {pkg}",
            "uninstall": "composer remove {pkg}",
            "list": "composer show",
            "update": "composer update",
        },
        "apt": {
            "detect": [],  # System package manager
            "install": "apt install -y {pkg}",
            "uninstall": "apt remove -y {pkg}",
            "list": "apt list --installed",
            "update": "apt update && apt upgrade -y",
            "search": "apt search {query}",
        },
        "brew": {
            "detect": [],  # System package manager
            "install": "brew install {pkg}",
            "uninstall": "brew uninstall {pkg}",
            "list": "brew list",
            "update": "brew update && brew upgrade",
            "search": "brew search {query}",
            "outdated": "brew outdated",
        },
    }
    
    def __init__(self, directory: str = None):
        self.directory = Path(directory) if directory else Path.cwd()
    
    def detect_manager(self) -> Optional[str]:
        """Detect the package manager for the current project."""
        # Check project-specific managers first
        priority = ["pnpm", "yarn", "npm", "poetry", "pip", "cargo", "go", "gem", "composer"]
        
        for manager in priority:
            config = self.MANAGERS[manager]
            for file in config.get("detect", []):
                if (self.directory / file).exists():
                    return manager
        
        return None
    
    def _run_command(self, cmd: str) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.directory),
                capture_output=True,
                text=True,
                timeout=120
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def install(self, package: str, dev: bool = False, manager: str = None) -> Tuple[bool, str]:
        """Install a package."""
        mgr = manager or self.detect_manager()
        if not mgr:
            return False, "Could not detect package manager"
        
        config = self.MANAGERS[mgr]
        cmd_key = "install_dev" if dev and "install_dev" in config else "install"
        cmd = config[cmd_key].format(pkg=package)
        
        return self._run_command(cmd)
    
    def uninstall(self, package: str, manager: str = None) -> Tuple[bool, str]:
        """Uninstall a package."""
        mgr = manager or self.detect_manager()
        if not mgr:
            return False, "Could not detect package manager"
        
        cmd = self.MANAGERS[mgr]["uninstall"].format(pkg=package)
        return self._run_command(cmd)
    
    def list_packages(self, manager: str = None) -> Tuple[bool, str]:
        """List installed packages."""
        mgr = manager or self.detect_manager()
        if not mgr:
            return False, "Could not detect package manager"
        
        cmd = self.MANAGERS[mgr]["list"]
        return self._run_command(cmd)
    
    def update(self, package: str = None, manager: str = None) -> Tuple[bool, str]:
        """Update packages."""
        mgr = manager or self.detect_manager()
        if not mgr:
            return False, "Could not detect package manager"
        
        cmd = self.MANAGERS[mgr]["update"]
        if package:
            cmd = cmd.format(pkg=package)
        return self._run_command(cmd)
    
    def outdated(self, manager: str = None) -> Tuple[bool, str]:
        """Check for outdated packages."""
        mgr = manager or self.detect_manager()
        if not mgr or "outdated" not in self.MANAGERS[mgr]:
            return False, "Outdated check not available for this manager"
        
        cmd = self.MANAGERS[mgr]["outdated"]
        return self._run_command(cmd)
    
    def search(self, query: str, manager: str = None) -> Tuple[bool, str]:
        """Search for packages."""
        mgr = manager or self.detect_manager() or "npm"
        if "search" not in self.MANAGERS[mgr]:
            return False, "Search not available for this manager"
        
        cmd = self.MANAGERS[mgr]["search"].format(query=query)
        return self._run_command(cmd)
    
    def get_info(self) -> Dict:
        """Get information about the current project's packages."""
        manager = self.detect_manager()
        
        info = {
            "directory": str(self.directory),
            "manager": manager,
            "lockfile": None,
        }
        
        # Check for lockfiles
        lockfiles = {
            "npm": "package-lock.json",
            "yarn": "yarn.lock",
            "pnpm": "pnpm-lock.yaml",
            "pip": "requirements.txt",
            "poetry": "poetry.lock",
            "cargo": "Cargo.lock",
            "go": "go.sum",
            "gem": "Gemfile.lock",
            "composer": "composer.lock",
        }
        
        if manager and manager in lockfiles:
            lockfile = self.directory / lockfiles[manager]
            if lockfile.exists():
                info["lockfile"] = str(lockfile)
        
        return info


class MultiProjectManager:
    """Manage packages across multiple projects in a monorepo."""
    
    def __init__(self, root_directory: str = None):
        self.root = Path(root_directory) if root_directory else Path.cwd()
    
    def find_projects(self) -> List[Dict]:
        """Find all projects in the directory tree."""
        projects = []
        
        # Files that indicate a project root
        project_files = [
            "package.json", "requirements.txt", "Cargo.toml",
            "go.mod", "Gemfile", "composer.json", "pyproject.toml"
        ]
        
        for project_file in project_files:
            for path in self.root.rglob(project_file):
                # Skip node_modules and similar
                if any(skip in str(path) for skip in ["node_modules", ".git", "vendor", "venv"]):
                    continue
                
                projects.append({
                    "path": str(path.parent),
                    "type": project_file,
                    "manager": UniversalPackageManager(str(path.parent)).detect_manager(),
                })
        
        return projects
    
    def install_all(self) -> List[Dict]:
        """Install dependencies for all projects."""
        results = []
        
        for project in self.find_projects():
            mgr = UniversalPackageManager(project["path"])
            success, output = mgr._run_command(
                self.MANAGERS[project["manager"]]["install"].format(pkg="")
                if project["manager"] else "echo 'No manager'"
            )
            results.append({
                "path": project["path"],
                "success": success,
            })
        
        return results
