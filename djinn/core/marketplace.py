"""
Plugin Marketplace - Install and manage community plugins.
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import requests


class PluginMarketplace:
    """Manages community plugins for DJINN."""
    
    # Built-in plugin registry (could be fetched from GitHub in the future)
    REGISTRY_URL = "https://raw.githubusercontent.com/boubli/djinn-plugins/main/registry.json"
    
    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            plugins_dir = str(djinn_dir / "plugins")
        
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.installed_file = self.plugins_dir / "installed.json"
        self.installed = self._load_installed()
    
    def _load_installed(self) -> Dict:
        """Load list of installed plugins."""
        if self.installed_file.exists():
            try:
                with open(self.installed_file) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_installed(self):
        """Save installed plugins list."""
        with open(self.installed_file, "w") as f:
            json.dump(self.installed, f, indent=2)
    
    def list_available(self) -> List[Dict]:
        """Fetch available plugins from registry."""
        # For now, return a static list. In production, fetch from URL.
        return [
            {"name": "aws-extended", "description": "Extended AWS commands", "author": "community", "version": "1.0.0"},
            {"name": "terraform-pro", "description": "Advanced Terraform workflows", "author": "community", "version": "1.0.0"},
            {"name": "ci-cd", "description": "CI/CD pipeline commands (GitHub Actions, GitLab)", "author": "community", "version": "1.0.0"},
            {"name": "kubernetes-extras", "description": "Extra K8s utilities", "author": "community", "version": "1.0.0"},
            {"name": "database-tools", "description": "Database migration and backup tools", "author": "community", "version": "1.0.0"},
        ]
    
    def list_installed(self) -> Dict:
        """List installed plugins."""
        return self.installed
    
    def install(self, plugin_name: str) -> bool:
        """Install a plugin by name."""
        available = {p["name"]: p for p in self.list_available()}
        
        if plugin_name not in available:
            return False
        
        plugin_info = available[plugin_name]
        
        # In production, download from URL. For now, just mark as installed.
        self.installed[plugin_name] = {
            "version": plugin_info["version"],
            "description": plugin_info["description"]
        }
        self._save_installed()
        return True
    
    def uninstall(self, plugin_name: str) -> bool:
        """Uninstall a plugin."""
        if plugin_name in self.installed:
            del self.installed[plugin_name]
            self._save_installed()
            # Remove plugin files if they exist
            plugin_path = self.plugins_dir / plugin_name
            if plugin_path.exists():
                shutil.rmtree(plugin_path)
            return True
        return False
