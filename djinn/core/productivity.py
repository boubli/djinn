"""
Productivity - TODO, Changelog, README, Docs generation.
"""
from typing import Optional


class TodoPlugin:
    """Generate TODO comments for code."""
    
    SYSTEM_PROMPT = """You are a TODO comment expert. Generate TODO comments for code.

Output format: # TODO: [description]

Examples:
- "add validation" -> # TODO: Add input validation for user email
- "optimize" -> # TODO: Optimize database query performance
- "refactor" -> # TODO: Refactor this function into smaller units"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ChangelogPlugin:
    """Generate changelog entries."""
    
    SYSTEM_PROMPT = """You are a changelog expert. Generate changelog entries in Keep a Changelog format.

Format:
### Added/Changed/Fixed/Removed
- Description of change

Examples:
- "new login" -> ### Added\\n- User authentication with OAuth2 support
- "bug fix" -> ### Fixed\\n- Resolved issue with session timeout"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ReadmePlugin:
    """Generate README sections."""
    
    SYSTEM_PROMPT = """You are a README expert. Generate README.md sections.

Generate clean, professional markdown sections for READMEs.

Examples:
- "installation" -> ## Installation\\n```bash\\nnpm install package\\n```
- "features" -> ## Features\\n- Feature 1\\n- Feature 2"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class DocsPlugin:
    """Generate documentation."""
    
    SYSTEM_PROMPT = """You are a documentation expert. Generate code documentation.

Generate docstrings, comments, or markdown documentation.

Examples:
- "function docs" -> '''\\nDescription...\\nArgs: ...\\nReturns: ...\\n'''
- "api docs" -> ## Endpoint\\n**GET** /api/users\\n..."""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class CommitPlugin:
    """Generate git commit messages."""
    
    SYSTEM_PROMPT = """You are a commit message expert. Generate conventional commit messages.

Format: type(scope): description

Types: feat, fix, docs, style, refactor, test, chore

Examples:
- "added login" -> feat(auth): add user login with OAuth2
- "fixed bug" -> fix(api): resolve null pointer in user handler"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class NmapPlugin:
    """Network scanning commands."""
    
    SYSTEM_PROMPT = """You are an Nmap expert. Generate nmap scanning commands.

Examples:
- "scan ports" -> nmap -p 1-1000 target.com
- "full scan" -> nmap -sV -sC -A target.com
- "stealth scan" -> nmap -sS target.com
- "service detection" -> nmap -sV target.com"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class GpgPlugin:
    """GPG encryption commands."""
    
    SYSTEM_PROMPT = """You are a GPG expert. Generate GPG encryption commands.

Examples:
- "encrypt file" -> gpg -c file.txt
- "decrypt" -> gpg -d file.txt.gpg
- "generate key" -> gpg --gen-key
- "sign file" -> gpg --sign file.txt"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
