"""
Sync Manager - Export/Import settings and cloud sync.
"""
import json
import base64
import zipfile
import io
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime


class SyncManager:
    """Manages settings export/import and cloud sync."""
    
    def __init__(self):
        self.djinn_dir = Path.home() / ".djinn"
        self.djinn_dir.mkdir(exist_ok=True)
    
    def export_settings(self, output_path: str = None) -> str:
        """Export all DJINN settings to a file."""
        settings = {
            "exported_at": datetime.now().isoformat(),
            "version": "1.0.2",
            "config": {},
            "aliases": {},
            "snippets": {},
            "templates": {},
            "vault": {},
        }
        
        # Load config
        config_file = self.djinn_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    settings["config"] = json.load(f)
                # Remove sensitive data
                settings["config"].pop("api_key", None)
            except:
                pass
        
        # Load aliases
        aliases_file = self.djinn_dir / "aliases.json"
        if aliases_file.exists():
            try:
                with open(aliases_file) as f:
                    settings["aliases"] = json.load(f)
            except:
                pass
        
        # Load snippets
        snippets_file = self.djinn_dir / "snippets.json"
        if snippets_file.exists():
            try:
                with open(snippets_file) as f:
                    settings["snippets"] = json.load(f)
            except:
                pass
        
        # Load templates
        templates_file = self.djinn_dir / "templates.json"
        if templates_file.exists():
            try:
                with open(templates_file) as f:
                    settings["templates"] = json.load(f)
            except:
                pass
        
        # Save to file
        if output_path is None:
            output_path = str(Path.home() / f"djinn-backup-{datetime.now().strftime('%Y%m%d')}.json")
        
        with open(output_path, "w") as f:
            json.dump(settings, f, indent=2)
        
        return output_path
    
    def import_settings(self, input_path: str, merge: bool = True) -> Dict:
        """Import settings from a file."""
        results = {"imported": [], "errors": []}
        
        try:
            with open(input_path) as f:
                settings = json.load(f)
        except Exception as e:
            results["errors"].append(f"Failed to read file: {e}")
            return results
        
        # Import config (merge or replace)
        if settings.get("config"):
            config_file = self.djinn_dir / "config.json"
            try:
                if merge and config_file.exists():
                    with open(config_file) as f:
                        current = json.load(f)
                    current.update(settings["config"])
                    settings["config"] = current
                
                with open(config_file, "w") as f:
                    json.dump(settings["config"], f, indent=2)
                results["imported"].append("config")
            except Exception as e:
                results["errors"].append(f"config: {e}")
        
        # Import aliases
        if settings.get("aliases"):
            aliases_file = self.djinn_dir / "aliases.json"
            try:
                if merge and aliases_file.exists():
                    with open(aliases_file) as f:
                        current = json.load(f)
                    current.update(settings["aliases"])
                    settings["aliases"] = current
                
                with open(aliases_file, "w") as f:
                    json.dump(settings["aliases"], f, indent=2)
                results["imported"].append("aliases")
            except Exception as e:
                results["errors"].append(f"aliases: {e}")
        
        # Import snippets
        if settings.get("snippets"):
            snippets_file = self.djinn_dir / "snippets.json"
            try:
                if merge and snippets_file.exists():
                    with open(snippets_file) as f:
                        current = json.load(f)
                    current.update(settings["snippets"])
                    settings["snippets"] = current
                
                with open(snippets_file, "w") as f:
                    json.dump(settings["snippets"], f, indent=2)
                results["imported"].append("snippets")
            except Exception as e:
                results["errors"].append(f"snippets: {e}")
        
        # Import templates
        if settings.get("templates"):
            templates_file = self.djinn_dir / "templates.json"
            try:
                if merge and templates_file.exists():
                    with open(templates_file) as f:
                        current = json.load(f)
                    current.update(settings["templates"])
                    settings["templates"] = current
                
                with open(templates_file, "w") as f:
                    json.dump(settings["templates"], f, indent=2)
                results["imported"].append("templates")
            except Exception as e:
                results["errors"].append(f"templates: {e}")
        
        return results
    
    def get_shareable_link(self, settings: Dict) -> str:
        """Generate a shareable base64 link for settings."""
        # Simple encoding - not for sensitive data
        json_str = json.dumps(settings)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return f"djinn://import/{encoded}"
    
    def parse_shareable_link(self, link: str) -> Optional[Dict]:
        """Parse a shareable link."""
        try:
            if link.startswith("djinn://import/"):
                encoded = link.replace("djinn://import/", "")
                json_str = base64.urlsafe_b64decode(encoded.encode()).decode()
                return json.loads(json_str)
        except:
            pass
        return None
