"""
Djinn Engine - Orchestrates LLM backends for command generation.
"""
import os
from typing import Optional, Dict, Any
from djinn.backends import OllamaBackend, LMStudioBackend, OpenAIBackend


class DjinnEngine:
    """Main engine that orchestrates LLM backends."""
    
    BACKENDS = {
        "ollama": OllamaBackend,
        "lmstudio": LMStudioBackend,
        "openai": OpenAIBackend,
    }
    
    SYSTEM_PROMPT = """You are Djinn, a powerful terminal command generator. Convert the user's natural language description into a single, executable shell command.

Rules:
- Output ONLY the command, no explanations or markdown
- Use common CLI tools (ffmpeg, docker, git, find, grep, etc.)
- For Windows, prefer PowerShell syntax when appropriate
- If the task requires multiple commands, chain them appropriately
- Be concise and efficient

Context about current directory will be provided when available."""

    def __init__(self, backend: str = "ollama", model: Optional[str] = None, api_key: Optional[str] = None):
        self.backend_name = backend.lower()
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._backend = None
        
    @property
    def backend(self):
        """Lazy-load the backend."""
        if self._backend is None:
            if self.backend_name not in self.BACKENDS:
                raise ValueError(f"Unknown backend: {self.backend_name}. Available: {list(self.BACKENDS.keys())}")
            
            backend_class = self.BACKENDS[self.backend_name]
            
            if self.backend_name == "openai":
                self._backend = backend_class(model=self.model, api_key=self.api_key)
            else:
                self._backend = backend_class(model=self.model)
                
        return self._backend
    
    def get_system_prompt(self) -> str:
        """Get system prompt (always English for best LLM performance)."""
        return self.SYSTEM_PROMPT
    
    def generate(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """Generate a shell command from natural language."""
        system_prompt = self.get_system_prompt()
        
        if context:
            system_prompt += f"\n\nCurrent directory context:\n{context}"
        
        return self.backend.generate(prompt, system_prompt)
    
    def generate_with_explanation(self, prompt: str, context: Optional[str] = None) -> Dict[str, str]:
        """Generate a command with explanation."""
        command = self.generate(prompt, context)
        
        if not command:
            return {"command": None, "explanation": None}
        
        # Get explanation
        explain_prompt = f"Explain this command briefly in one line: {command}"
        explanation = self.backend.generate(explain_prompt, "You are a helpful assistant. Give very brief explanations.")
        
        return {"command": command, "explanation": explanation}
    
    def refine(self, original_prompt: str, original_command: str, feedback: str) -> Optional[str]:
        """Refine a command based on user feedback."""
        refine_prompt = f"""Original request: {original_prompt}
Generated command: {original_command}
User feedback: {feedback}

Generate an improved command based on the feedback. Output ONLY the command."""
        
        return self.backend.generate(refine_prompt, self.SYSTEM_PROMPT)
