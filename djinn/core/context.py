"""
Context Analyzer - Analyzes current directory for better command generation.
"""
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional


class ContextAnalyzer:
    """Analyzes the current directory to provide context for command generation."""
    
    # File type categories
    CATEGORIES = {
        "code": [".py", ".js", ".ts", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".cs", ".rb", ".php"],
        "web": [".html", ".css", ".scss", ".less", ".jsx", ".tsx", ".vue", ".svelte"],
        "data": [".json", ".yaml", ".yml", ".xml", ".csv", ".sql", ".db", ".sqlite"],
        "media": [".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".flac", ".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "docs": [".md", ".txt", ".pdf", ".doc", ".docx", ".rst"],
        "config": [".env", ".gitignore", ".dockerignore", "Dockerfile", "docker-compose.yml", "Makefile"],
        "package": ["package.json", "requirements.txt", "Cargo.toml", "go.mod", "pyproject.toml", "setup.py"],
    }
    
    def __init__(self, directory: Optional[str] = None):
        self.directory = Path(directory) if directory else Path.cwd()
        self.system = platform.system()
    
    def analyze(self, max_files: int = 50, max_depth: int = 2) -> Dict:
        """Analyze the directory and return context information."""
        files = []
        dirs = []
        file_types = {}
        categories_found = set()
        
        try:
            for item in self._walk_limited(max_files, max_depth):
                if item.is_file():
                    files.append(item.name)
                    ext = item.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                    
                    # Check categories
                    for cat, extensions in self.CATEGORIES.items():
                        if ext in extensions or item.name in extensions:
                            categories_found.add(cat)
                elif item.is_dir():
                    dirs.append(item.name)
        except PermissionError:
            pass
        
        return {
            "path": str(self.directory),
            "system": self.system,
            "files": files[:20],  # Limit for context
            "dirs": dirs[:10],
            "file_count": len(files),
            "dir_count": len(dirs),
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
            "categories": list(categories_found),
            "is_git": (self.directory / ".git").exists(),
            "has_package_json": (self.directory / "package.json").exists(),
            "has_requirements": (self.directory / "requirements.txt").exists(),
            "has_dockerfile": (self.directory / "Dockerfile").exists(),
        }
    
    def _walk_limited(self, max_files: int, max_depth: int):
        """Walk directory with limits."""
        count = 0
        
        def walk(path: Path, depth: int):
            nonlocal count
            if depth > max_depth or count >= max_files:
                return
            
            try:
                for item in path.iterdir():
                    if count >= max_files:
                        return
                    
                    # Skip hidden and common ignore patterns
                    if item.name.startswith(".") or item.name in ["node_modules", "__pycache__", "venv", ".git"]:
                        continue
                    
                    yield item
                    count += 1
                    
                    if item.is_dir():
                        yield from walk(item, depth + 1)
            except PermissionError:
                pass
        
        yield from walk(self.directory, 0)
    
    def get_context_string(self, max_length: int = 500) -> str:
        """Get a formatted context string for LLM prompts."""
        analysis = self.analyze()
        
        lines = [
            f"OS: {analysis['system']}",
            f"Directory: {analysis['path']}",
            f"Files: {analysis['file_count']}, Dirs: {analysis['dir_count']}",
        ]
        
        if analysis["categories"]:
            lines.append(f"Project type: {', '.join(analysis['categories'])}")
        
        if analysis["is_git"]:
            lines.append("Git repository: Yes")
        
        if analysis["file_types"]:
            top_types = ", ".join(f"{k}({v})" for k, v in list(analysis["file_types"].items())[:5])
            lines.append(f"Top file types: {top_types}")
        
        if analysis["files"]:
            lines.append(f"Sample files: {', '.join(analysis['files'][:10])}")
        
        context = "\n".join(lines)
        return context[:max_length]
    
    def detect_shell(self) -> str:
        """Detect the current shell type."""
        if self.system == "Windows":
            # Check if running in PowerShell or CMD
            if os.environ.get("PSModulePath"):
                return "powershell"
            return "cmd"
        else:
            shell = os.environ.get("SHELL", "")
            if "zsh" in shell:
                return "zsh"
            elif "bash" in shell:
                return "bash"
            elif "fish" in shell:
                return "fish"
            return "sh"
    
    def get_shell_info(self) -> str:
        """Get shell information for LLM context."""
        shell = self.detect_shell()
        shell_info = {
            "powershell": "PowerShell on Windows. Use PowerShell syntax (e.g., Get-ChildItem, Remove-Item).",
            "cmd": "CMD on Windows. Use batch syntax.",
            "bash": "Bash shell. Use bash syntax.",
            "zsh": "Zsh shell. Use zsh/bash syntax.",
            "fish": "Fish shell. Use fish syntax.",
            "sh": "POSIX shell. Use portable sh syntax.",
        }
        return shell_info.get(shell, f"Shell: {shell}")
