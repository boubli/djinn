"""
Documentation Generator - Auto-generate docs for scripts and projects.
"""
import os
import re
from typing import Dict, List, Optional
from pathlib import Path


class DocsGenerator:
    """Generate documentation from code and scripts."""
    
    def __init__(self, engine=None):
        self.engine = engine
    
    SYSTEM_PROMPT = """You are a technical documentation expert. Generate clear, comprehensive documentation.
Include: purpose, usage, parameters, examples, and notes.
Use markdown format. Be concise but complete."""
    
    def generate_for_script(self, filepath: str) -> str:
        """Generate documentation for a shell script."""
        path = Path(filepath)
        if not path.exists():
            return "File not found"
        
        content = path.read_text()
        
        if self.engine:
            prompt = f"Generate documentation for this script:\n\n```\n{content[:3000]}\n```"
            return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
        
        # Fallback: extract comments and generate basic docs
        return self._extract_basic_docs(content, path.name)
    
    def _extract_basic_docs(self, content: str, filename: str) -> str:
        """Extract basic documentation from script comments."""
        lines = content.split("\n")
        doc_lines = [f"# {filename}", ""]
        
        # Extract header comments
        in_header = True
        for line in lines:
            if line.startswith("#!"):
                continue
            if line.startswith("#"):
                if in_header:
                    doc_lines.append(line[1:].strip())
            else:
                in_header = False
        
        doc_lines.extend(["", "## Usage", f"```bash\n./{filename}\n```", ""])
        
        # Extract functions
        functions = re.findall(r'^(\w+)\s*\(\)\s*{', content, re.MULTILINE)
        if functions:
            doc_lines.append("## Functions")
            for func in functions:
                doc_lines.append(f"- `{func}()`")
        
        return "\n".join(doc_lines)
    
    def generate_readme(self, directory: str = None) -> str:
        """Generate a README.md for a project."""
        dir_path = Path(directory) if directory else Path.cwd()
        
        project_info = {
            "name": dir_path.name,
            "files": [],
            "has_package_json": (dir_path / "package.json").exists(),
            "has_requirements": (dir_path / "requirements.txt").exists(),
            "has_dockerfile": (dir_path / "Dockerfile").exists(),
        }
        
        # Scan for important files
        for ext in [".py", ".js", ".ts", ".go", ".rs"]:
            files = list(dir_path.glob(f"*{ext}"))
            project_info["files"].extend([f.name for f in files[:10]])
        
        readme = f"""# {project_info['name']}

## Description
[Add project description here]

## Installation

"""
        
        if project_info["has_package_json"]:
            readme += "```bash\nnpm install\n```\n\n"
        if project_info["has_requirements"]:
            readme += "```bash\npip install -r requirements.txt\n```\n\n"
        
        readme += """## Usage
[Add usage instructions here]

## Files
"""
        
        for f in project_info["files"][:10]:
            readme += f"- `{f}`\n"
        
        readme += """
## License
[Add license information here]
"""
        
        return readme
    
    def generate_api_docs(self, filepath: str) -> str:
        """Generate API documentation from Python file."""
        path = Path(filepath)
        if not path.exists() or path.suffix != ".py":
            return "Python file not found"
        
        content = path.read_text()
        
        # Extract classes and functions
        classes = re.findall(r'^class\s+(\w+).*?:', content, re.MULTILINE)
        functions = re.findall(r'^def\s+(\w+)\s*\((.*?)\):', content, re.MULTILINE)
        
        doc = f"# API Documentation: {path.name}\n\n"
        
        if classes:
            doc += "## Classes\n\n"
            for cls in classes:
                doc += f"### `{cls}`\n\n"
        
        if functions:
            doc += "## Functions\n\n"
            for func, params in functions:
                if not func.startswith("_"):
                    doc += f"### `{func}({params})`\n\n"
        
        return doc


class WhyExplainer:
    """Explain WHY commands failed, not just how to fix."""
    
    SYSTEM_PROMPT = """You are an expert debugger. When a command fails, explain:
1. WHAT went wrong (the immediate cause)
2. WHY it went wrong (the root cause)
3. HOW to prevent it in the future
4. The fix

Be educational and thorough. Help the user understand the underlying concepts."""
    
    def __init__(self, engine=None):
        self.engine = engine
    
    COMMON_ERRORS = {
        "permission denied": {
            "what": "The system denied access to the file or resource",
            "why": "Either the file has restrictive permissions, you need sudo, or you don't own the file",
            "prevent": "Check permissions before operations, use sudo when needed, understand file ownership",
        },
        "command not found": {
            "what": "The shell couldn't find the executable",
            "why": "The program isn't installed, not in PATH, or misspelled",
            "prevent": "Install missing tools, verify PATH, use 'which' to check availability",
        },
        "connection refused": {
            "what": "The network connection was rejected",
            "why": "The service isn't running, firewall blocking, or wrong port",
            "prevent": "Verify service is running, check ports, review firewall rules",
        },
        "no such file": {
            "what": "The specified file or directory doesn't exist",
            "why": "Wrong path, typo, file was moved/deleted, or not yet created",
            "prevent": "Use tab completion, verify paths exist before operations",
        },
    }
    
    def explain(self, command: str, error: str) -> str:
        """Explain why a command failed."""
        # Check common errors first
        error_lower = error.lower()
        for pattern, info in self.COMMON_ERRORS.items():
            if pattern in error_lower:
                explanation = f"""## Error Analysis

### What Happened
{info['what']}

### Why It Happened  
{info['why']}

### How to Prevent
{info['prevent']}

### The Failed Command
```
{command}
```

### The Error
```
{error[:500]}
```
"""
                return explanation
        
        # Use AI for unknown errors
        if self.engine:
            prompt = f"""Command: {command}

Error: {error[:500]}

Explain WHY this failed (root cause), not just the symptom."""
            return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
        
        return f"Error occurred: {error[:200]}"
