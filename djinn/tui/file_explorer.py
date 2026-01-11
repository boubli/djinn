"""
File Explorer - Interactive terminal file manager.
"""
import os
import shutil
import stat
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box


class FileExplorer:
    """Interactive file explorer."""
    
    def __init__(self, start_path: str = None):
        self.console = Console()
        self.current_path = Path(start_path) if start_path else Path.cwd()
        self.clipboard = None
        self.clipboard_action = None  # "copy" or "cut"
        self.history = [self.current_path]
    
    def cd(self, path: str) -> bool:
        """Change directory."""
        if path == "..":
            new_path = self.current_path.parent
        elif path == "~":
            new_path = Path.home()
        elif path == "-":
            if len(self.history) > 1:
                new_path = self.history[-2]
            else:
                return False
        else:
            new_path = self.current_path / path if not Path(path).is_absolute() else Path(path)
        
        if new_path.exists() and new_path.is_dir():
            self.history.append(new_path)
            self.current_path = new_path
            return True
        return False
    
    def ls(self, show_hidden: bool = False, sort_by: str = "name") -> List[Dict]:
        """List directory contents."""
        items = []
        
        try:
            for entry in self.current_path.iterdir():
                if not show_hidden and entry.name.startswith("."):
                    continue
                
                try:
                    stat_info = entry.stat()
                    items.append({
                        "name": entry.name,
                        "is_dir": entry.is_dir(),
                        "size": stat_info.st_size,
                        "modified": datetime.fromtimestamp(stat_info.st_mtime),
                        "permissions": stat.filemode(stat_info.st_mode),
                    })
                except:
                    items.append({
                        "name": entry.name,
                        "is_dir": entry.is_dir(),
                        "size": 0,
                        "modified": None,
                        "permissions": "?????????",
                    })
        except PermissionError:
            pass
        
        # Sort
        if sort_by == "name":
            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        elif sort_by == "size":
            items.sort(key=lambda x: (not x["is_dir"], -x["size"]))
        elif sort_by == "modified":
            items.sort(key=lambda x: (not x["is_dir"], x["modified"] or datetime.min), reverse=True)
        
        return items
    
    def render_ls(self, show_hidden: bool = False) -> None:
        """Render directory listing."""
        items = self.ls(show_hidden)
        
        table = Table(
            title=f"📁 {self.current_path}",
            box=box.ROUNDED,
            show_header=True
        )
        table.add_column("Name", style="cyan")
        table.add_column("Size", justify="right")
        table.add_column("Modified")
        table.add_column("Permissions")
        
        for item in items:
            icon = "📁" if item["is_dir"] else "📄"
            name = f"{icon} {item['name']}"
            
            if item["is_dir"]:
                size = "-"
            elif item["size"] < 1024:
                size = f"{item['size']} B"
            elif item["size"] < 1024 * 1024:
                size = f"{item['size']/1024:.1f} KB"
            else:
                size = f"{item['size']/(1024*1024):.1f} MB"
            
            modified = item["modified"].strftime("%Y-%m-%d %H:%M") if item["modified"] else "?"
            
            table.add_row(name, size, modified, item["permissions"])
        
        self.console.print(table)
    
    def tree(self, max_depth: int = 3) -> Tree:
        """Generate a directory tree."""
        tree = Tree(f"📁 {self.current_path.name}")
        self._build_tree(tree, self.current_path, 0, max_depth)
        return tree
    
    def _build_tree(self, tree: Tree, path: Path, depth: int, max_depth: int):
        """Recursively build tree."""
        if depth >= max_depth:
            return
        
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for entry in entries[:20]:  # Limit entries
                if entry.name.startswith("."):
                    continue
                
                if entry.is_dir():
                    branch = tree.add(f"📁 {entry.name}")
                    self._build_tree(branch, entry, depth + 1, max_depth)
                else:
                    tree.add(f"📄 {entry.name}")
        except PermissionError:
            pass
    
    def mkdir(self, name: str) -> bool:
        """Create a directory."""
        try:
            (self.current_path / name).mkdir(parents=True)
            return True
        except:
            return False
    
    def touch(self, name: str) -> bool:
        """Create a file."""
        try:
            (self.current_path / name).touch()
            return True
        except:
            return False
    
    def rm(self, name: str, recursive: bool = False) -> bool:
        """Remove a file or directory."""
        path = self.current_path / name
        try:
            if path.is_dir():
                if recursive:
                    shutil.rmtree(path)
                else:
                    path.rmdir()
            else:
                path.unlink()
            return True
        except:
            return False
    
    def copy(self, name: str):
        """Copy a file/directory to clipboard."""
        self.clipboard = self.current_path / name
        self.clipboard_action = "copy"
    
    def cut(self, name: str):
        """Cut a file/directory to clipboard."""
        self.clipboard = self.current_path / name
        self.clipboard_action = "cut"
    
    def paste(self) -> bool:
        """Paste from clipboard."""
        if not self.clipboard or not self.clipboard.exists():
            return False
        
        dest = self.current_path / self.clipboard.name
        
        try:
            if self.clipboard.is_dir():
                if self.clipboard_action == "copy":
                    shutil.copytree(self.clipboard, dest)
                else:
                    shutil.move(self.clipboard, dest)
            else:
                if self.clipboard_action == "copy":
                    shutil.copy2(self.clipboard, dest)
                else:
                    shutil.move(self.clipboard, dest)
            
            if self.clipboard_action == "cut":
                self.clipboard = None
            
            return True
        except:
            return False
    
    def rename(self, old_name: str, new_name: str) -> bool:
        """Rename a file or directory."""
        try:
            (self.current_path / old_name).rename(self.current_path / new_name)
            return True
        except:
            return False
    
    def read_file(self, name: str, max_lines: int = 100) -> Optional[str]:
        """Read file contents."""
        path = self.current_path / name
        try:
            with open(path) as f:
                lines = f.readlines()[:max_lines]
                return "".join(lines)
        except:
            return None
    
    def get_info(self, name: str) -> Dict:
        """Get detailed info about a file."""
        path = self.current_path / name
        if not path.exists():
            return {"error": "Not found"}
        
        stat_info = path.stat()
        
        return {
            "name": name,
            "path": str(path.absolute()),
            "is_dir": path.is_dir(),
            "size": stat_info.st_size,
            "created": datetime.fromtimestamp(stat_info.st_ctime),
            "modified": datetime.fromtimestamp(stat_info.st_mtime),
            "permissions": stat.filemode(stat_info.st_mode),
        }
    
    def search(self, pattern: str, recursive: bool = True) -> List[str]:
        """Search for files matching pattern."""
        results = []
        search_func = self.current_path.rglob if recursive else self.current_path.glob
        
        for path in search_func(pattern):
            results.append(str(path.relative_to(self.current_path)))
            if len(results) >= 50:
                break
        
        return results
