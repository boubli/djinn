"""
AI Utilities - Conversation mode, translate, summarize, code generation.
"""
from typing import Optional, List


class ConversationPlugin:
    """AI conversation/chat mode."""
    
    SYSTEM_PROMPT = """You are a helpful terminal assistant. Have a conversation with the user to help them with their tasks.

Rules:
- Be concise and helpful
- If they need a command, provide it
- Answer questions about the terminal, Linux, DevOps, etc.
- Stay focused on technical topics"""

    def __init__(self, engine):
        self.engine = engine
        self.history = []
    
    def chat(self, message: str) -> Optional[str]:
        """Have a conversation turn."""
        self.history.append({"role": "user", "content": message})
        
        # Build context from history
        context = "\n".join([f"{h['role']}: {h['content']}" for h in self.history[-10:]])
        full_prompt = f"{context}\nassistant:"
        
        response = self.engine.backend.generate(full_prompt, self.SYSTEM_PROMPT)
        if response:
            self.history.append({"role": "assistant", "content": response})
        return response
    
    def clear(self):
        """Clear conversation history."""
        self.history = []


class TranslatePlugin:
    """Translate command between shells."""
    
    SYSTEM_PROMPT = """You are a shell command translator. Translate commands between different shells/systems.

Examples:
- Bash to PowerShell: "ls -la" -> "Get-ChildItem -Force"
- PowerShell to Bash: "Get-Process" -> "ps aux"
- Linux to macOS: adjust paths and tools
- Windows to Linux: convert paths and commands

Output ONLY the translated command."""

    def __init__(self, engine):
        self.engine = engine
    
    def translate(self, command: str, from_shell: str, to_shell: str) -> Optional[str]:
        prompt = f"Translate from {from_shell} to {to_shell}: {command}"
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class CodeGenPlugin:
    """Generate code snippets."""
    
    SYSTEM_PROMPT = """You are a code generator. Generate code snippets in the requested language.

Rules:
- Output ONLY the code, no explanations
- Include necessary imports
- Be concise but complete
- Follow language best practices"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str, language: str = "python") -> Optional[str]:
        full_prompt = f"Generate {language} code: {prompt}"
        return self.engine.backend.generate(full_prompt, self.SYSTEM_PROMPT)


class OneLinersPlugin:
    """Generate useful one-liners."""
    
    SYSTEM_PROMPT = """You are a one-liner expert. Generate powerful shell one-liners.

Rules:
- Output ONLY the one-liner command
- Make it as efficient as possible
- Use pipes and common tools
- Be clever but readable"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ScriptPlugin:
    """Generate shell scripts."""
    
    SYSTEM_PROMPT = """You are a shell script expert. Generate complete shell scripts.

Rules:
- Include shebang (#!/bin/bash)
- Add error handling (set -e)
- Include useful comments
- Make it production-ready"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
