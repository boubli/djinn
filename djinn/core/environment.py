"""
Environment Manager - Smart .env file management.
"""
import os
import json
import shutil
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class EnvManager:
    """Manages .env files and environment variables."""
    
    def __init__(self, directory: str = None):
        self.directory = Path(directory) if directory else Path.cwd()
        self.djinn_dir = Path.home() / ".djinn"
        self.env_backup_dir = self.djinn_dir / "env_backups"
        self.env_backup_dir.mkdir(parents=True, exist_ok=True)
    
    def read_env(self, filename: str = ".env") -> Dict[str, str]:
        """Read an .env file."""
        env_file = self.directory / filename
        env_vars = {}
        
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        value = value.strip().strip('"').strip("'")
                        env_vars[key.strip()] = value
        
        return env_vars
    
    def write_env(self, env_vars: Dict[str, str], filename: str = ".env"):
        """Write an .env file."""
        env_file = self.directory / filename
        
        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                # Quote values with spaces
                if " " in value or "'" in value:
                    value = f'"{value}"'
                f.write(f"{key}={value}\n")
    
    def get(self, key: str, filename: str = ".env") -> Optional[str]:
        """Get a single env variable."""
        env_vars = self.read_env(filename)
        return env_vars.get(key)
    
    def set(self, key: str, value: str, filename: str = ".env"):
        """Set a single env variable."""
        env_vars = self.read_env(filename)
        env_vars[key] = value
        self.write_env(env_vars, filename)
    
    def delete(self, key: str, filename: str = ".env") -> bool:
        """Delete an env variable."""
        env_vars = self.read_env(filename)
        if key in env_vars:
            del env_vars[key]
            self.write_env(env_vars, filename)
            return True
        return False
    
    def list_all(self, filename: str = ".env") -> Dict[str, str]:
        """List all env variables."""
        return self.read_env(filename)
    
    def list_files(self) -> List[str]:
        """List all .env files in directory."""
        return [f.name for f in self.directory.glob(".env*")]
    
    def backup(self, filename: str = ".env") -> str:
        """Backup an .env file."""
        env_file = self.directory / filename
        if not env_file.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filename}_{timestamp}"
        backup_path = self.env_backup_dir / backup_name
        
        shutil.copy(env_file, backup_path)
        return str(backup_path)
    
    def restore(self, backup_name: str, filename: str = ".env") -> bool:
        """Restore from a backup."""
        backup_path = self.env_backup_dir / backup_name
        if backup_path.exists():
            env_file = self.directory / filename
            shutil.copy(backup_path, env_file)
            return True
        return False
    
    def list_backups(self) -> List[str]:
        """List all backups."""
        return [f.name for f in self.env_backup_dir.glob("*")]
    
    def generate_example(self, filename: str = ".env") -> str:
        """Generate a .env.example from .env (with values removed)."""
        env_vars = self.read_env(filename)
        example_lines = []
        
        for key in env_vars:
            example_lines.append(f"{key}=")
        
        example_content = "\n".join(example_lines)
        example_file = self.directory / f"{filename}.example"
        
        with open(example_file, "w") as f:
            f.write(example_content)
        
        return str(example_file)
    
    def diff(self, file1: str = ".env", file2: str = ".env.example") -> Dict:
        """Compare two .env files."""
        env1 = self.read_env(file1)
        env2 = self.read_env(file2)
        
        keys1 = set(env1.keys())
        keys2 = set(env2.keys())
        
        return {
            "only_in_first": list(keys1 - keys2),
            "only_in_second": list(keys2 - keys1),
            "in_both": list(keys1 & keys2),
        }
    
    def validate(self, filename: str = ".env") -> Dict:
        """Validate .env file for common issues."""
        env_file = self.directory / filename
        issues = []
        
        if not env_file.exists():
            return {"valid": False, "issues": ["File not found"]}
        
        with open(env_file) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                if "=" not in line:
                    issues.append(f"Line {i}: Missing '=' separator")
                else:
                    key, value = line.split("=", 1)
                    if not key.strip():
                        issues.append(f"Line {i}: Empty key")
                    if key != key.upper():
                        issues.append(f"Line {i}: Key '{key}' should be uppercase")
        
        return {"valid": len(issues) == 0, "issues": issues}


class DotfilesManager:
    """Manage dotfiles backup and restore."""
    
    COMMON_DOTFILES = [
        ".bashrc", ".zshrc", ".bash_profile", ".profile",
        ".vimrc", ".tmux.conf", ".gitconfig", ".gitignore_global",
        ".ssh/config", ".npmrc", ".pypirc"
    ]
    
    def __init__(self):
        self.home = Path.home()
        self.djinn_dir = self.home / ".djinn"
        self.dotfiles_dir = self.djinn_dir / "dotfiles"
        self.dotfiles_dir.mkdir(parents=True, exist_ok=True)
    
    def backup(self, files: List[str] = None) -> Dict:
        """Backup dotfiles."""
        files = files or self.COMMON_DOTFILES
        backed_up = []
        skipped = []
        
        for dotfile in files:
            src = self.home / dotfile
            if src.exists():
                dst = self.dotfiles_dir / dotfile
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                backed_up.append(dotfile)
            else:
                skipped.append(dotfile)
        
        return {"backed_up": backed_up, "skipped": skipped}
    
    def restore(self, files: List[str] = None) -> Dict:
        """Restore dotfiles."""
        files = files or self.COMMON_DOTFILES
        restored = []
        skipped = []
        
        for dotfile in files:
            src = self.dotfiles_dir / dotfile
            if src.exists():
                dst = self.home / dotfile
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                restored.append(dotfile)
            else:
                skipped.append(dotfile)
        
        return {"restored": restored, "skipped": skipped}
    
    def list_backed_up(self) -> List[str]:
        """List backed up dotfiles."""
        files = []
        for f in self.dotfiles_dir.rglob("*"):
            if f.is_file():
                files.append(str(f.relative_to(self.dotfiles_dir)))
        return files
    
    def export_archive(self, output_path: str = None) -> str:
        """Export dotfiles as tar archive."""
        import tarfile
        
        if output_path is None:
            output_path = str(self.home / "dotfiles-backup.tar.gz")
        
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(self.dotfiles_dir, arcname="dotfiles")
        
        return output_path
