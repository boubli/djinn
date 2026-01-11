"""
Release Manager - Automate Git releases and versioning.
"""
import subprocess
import re
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime


class ReleaseManager:
    """Manages Git releases and versioning."""
    
    def __init__(self, directory: str = None):
        self.directory = Path(directory) if directory else Path.cwd()
    
    def get_current_version(self) -> Optional[str]:
        """Get current version from various sources."""
        # Try package.json
        pkg_json = self.directory / "package.json"
        if pkg_json.exists():
            import json
            try:
                with open(pkg_json) as f:
                    return json.load(f).get("version")
            except:
                pass
        
        # Try pyproject.toml
        pyproject = self.directory / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        return match.group(1)
            except:
                pass
        
        # Try git tags
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            if result.returncode == 0:
                return result.stdout.strip().lstrip("v")
        except:
            pass
        
        return None
    
    def bump_version(self, bump_type: str = "patch") -> Tuple[str, str]:
        """Bump version (patch, minor, major)."""
        current = self.get_current_version() or "0.0.0"
        parts = current.split(".")
        
        try:
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2].split("-")[0]) if len(parts) > 2 else 0
        except ValueError:
            major, minor, patch = 0, 0, 0
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"{major}.{minor}.{patch}"
        return current, new_version
    
    def get_commits_since_tag(self, tag: str = None) -> list:
        """Get commits since last tag."""
        try:
            if tag:
                cmd = ["git", "log", f"{tag}..HEAD", "--oneline"]
            else:
                cmd = ["git", "log", "--oneline", "-20"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.strip().split("\n") if line]
        except:
            pass
        
        return []
    
    def generate_changelog_entry(self, version: str, commits: list) -> str:
        """Generate a changelog entry."""
        date = datetime.now().strftime("%Y-%m-%d")
        
        # Categorize commits
        features = []
        fixes = []
        other = []
        
        for commit in commits:
            commit_lower = commit.lower()
            if any(word in commit_lower for word in ["feat", "add", "new", "implement"]):
                features.append(commit)
            elif any(word in commit_lower for word in ["fix", "bug", "patch", "resolve"]):
                fixes.append(commit)
            else:
                other.append(commit)
        
        entry = f"## [{version}] - {date}\n\n"
        
        if features:
            entry += "### Added\n"
            for f in features:
                entry += f"- {f}\n"
            entry += "\n"
        
        if fixes:
            entry += "### Fixed\n"
            for f in fixes:
                entry += f"- {f}\n"
            entry += "\n"
        
        if other:
            entry += "### Changed\n"
            for o in other:
                entry += f"- {o}\n"
            entry += "\n"
        
        return entry
    
    def create_tag(self, version: str, message: str = None) -> bool:
        """Create a git tag."""
        tag_name = f"v{version}"
        msg = message or f"Release {version}"
        
        try:
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", msg],
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            return result.returncode == 0
        except:
            return False
    
    def push_tag(self, version: str) -> bool:
        """Push a tag to remote."""
        tag_name = f"v{version}"
        
        try:
            result = subprocess.run(
                ["git", "push", "origin", tag_name],
                capture_output=True,
                text=True,
                cwd=str(self.directory)
            )
            return result.returncode == 0
        except:
            return False
    
    def update_version_files(self, new_version: str) -> list:
        """Update version in project files."""
        updated = []
        
        # Update package.json
        pkg_json = self.directory / "package.json"
        if pkg_json.exists():
            try:
                import json
                with open(pkg_json) as f:
                    data = json.load(f)
                data["version"] = new_version
                with open(pkg_json, "w") as f:
                    json.dump(data, f, indent=2)
                updated.append("package.json")
            except:
                pass
        
        # Update pyproject.toml
        pyproject = self.directory / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject) as f:
                    content = f.read()
                new_content = re.sub(
                    r'(version\s*=\s*["\'])[^"\']+(["\'])',
                    f'\\g<1>{new_version}\\g<2>',
                    content
                )
                with open(pyproject, "w") as f:
                    f.write(new_content)
                updated.append("pyproject.toml")
            except:
                pass
        
        return updated
