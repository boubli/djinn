"""
Advanced AI features for DJINN v2.2.0

Includes:
- Git Commit Message Generator
- PR Reviewer  
- Regex Explainer
- SQL Generator
- Model Switcher
"""
from typing import Dict, List
import subprocess
import re


class GitCommitWizard:
    """Generate conventional commit messages from staged changes."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def generate_commit_message(self) -> str:
        """Generate commit message based on git staged changes."""
        try:
            # Get staged diff
            result = subprocess.run(
                ["git", "diff", "--staged"],
                capture_output=True,
                text=True
            )
            diff = result.stdout
            
            if not diff:
                return "No staged changes found. Run 'git add' first."
            
            # Limit diff size
            if len(diff) > 3000:
                diff = diff[:3000] + "\n... (truncated)"
            
            prompt = f"""Generate a conventional commit message for these changes:

{diff}

Use format: type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Keep description under 50 chars.
Add a body if needed explaining WHY (not what).

Commit message:"""
            
            message = self.engine.backend.generate(
                prompt,
                system_prompt="You are a git expert. Write clear, conventional commit messages."
            )
            
            return message.strip()
        except:
            return "Error: Is this a git repository?"


class PRReviewer:
    """Generate PR reviews comparing branches."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def review_pr(self, base_branch: str = "main") -> str:
        """Generate PR review comparing current branch to base."""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            
            if not current_branch:
                return "Not on a git branch"
            
            # Get diff
            result = subprocess.run(
                ["git", "diff", f"{base_branch}...{current_branch}"],
                capture_output=True,
                text=True
            )
            diff = result.stdout
            
            if not diff:
                return f"No changes between {current_branch} and {base_branch}"
            
            # Limit diff size
            if len(diff) > 4000:
                diff = diff[:4000] + "\n... (truncated)"
            
            prompt = f"""Review this Pull Request comparing {current_branch} to {base_branch}:

{diff}

Provide a markdown review covering:
1. Summary of changes
2. Potential issues or bugs
3. Code quality suggestions
4. Security concerns (if any)

Be constructive and specific.

Review:"""
            
            review = self.engine.backend.generate(
                prompt,
                system_prompt="You are a senior code reviewer. Be thorough but constructive."
            )
            
            return review
        except Exception as e:
            return f"Error generating review: {e}"


class RegexExplainer:
    """Explain regular expressions in plain English."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def explain(self, regex_pattern: str) -> str:
        """Explain what a regex pattern does."""
        prompt = f"""Explain this regular expression pattern in simple terms:

Pattern: {regex_pattern}

Break down each part and explain:
1. What it matches
2. Key components (groups, quantifiers, etc.)
3. Example matches
4. Common use cases

Explanation:"""
        
        explanation = self.engine.backend.generate(
            prompt,
            system_prompt="You are a regex expert. Explain patterns clearly with examples."
        )
        
        return explanation


class SQLGenerator:
    """Generate SQL queries from natural language."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, description: str, schema_hint: str = None) -> str:
        """Generate SQL query from description."""
        schema_context = ""
        if schema_hint:
            schema_context = f"\nDatabase schema hint: {schema_hint}\n"
        
        prompt = f"""Generate a SQL query for this request:

{description}{schema_context}

Provide ONLY the SQL query, no explanations.

Query:"""
        
        query = self.engine.backend.generate(
            prompt,
            system_prompt="You are a SQL expert. Generate clean, efficient queries."
        )
        
        return query.strip()
    
    def explain_query(self, sql_query: str) -> str:
        """Explain what a SQL query does."""
        prompt = f"""Explain this SQL query in simple terms:

{sql_query}

Cover:
1. What data it retrieves/modifies
2. How it works (joins, filters, etc.)
3. Performance considerations

Explanation:"""
        
        explanation = self.engine.backend.generate(
            prompt,
            system_prompt="You are a SQL expert. Explain queries clearly."
        )
        
        return explanation


class ModelSwitcher:
    """Switch between LLM backends/models on the fly."""
    
    def __init__(self):
        pass
    
    def list_available_backends(self) -> Dict[str, bool]:
        """Check which backends are available."""
        import requests
        
        backends = {
            "ollama": False,
            "lmstudio": False,
            "openai": False
        }
        
        # Check Ollama
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=1)
            if r.status_code == 200:
                backends["ollama"] = True
        except:
            pass
        
        # Check LM Studio
        try:
            r = requests.get("http://localhost:1234/v1/models", timeout=1)
            if r.status_code == 200:
                backends["lmstudio"] = True
        except:
            pass
        
        # Check OpenAI (just check if API key exists)
        import os
        if os.environ.get("OPENAI_API_KEY") or Path.home() / ".djinn" / "config.json"):
            backends["openai"] = True
        
        return backends
    
    def switch_backend(self, backend: str, model: str = None) -> Dict:
        """Switch to a different backend."""
        from pathlib import Path
        import json
        
        config_path = Path.home() / ".djinn" / "config.json"
        
        # Load current config
        config = {}
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        
        # Update backend
        config["backend"] = backend
        if model:
            config["model"] = model
        
        # Save  
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        return config


from pathlib import Path
