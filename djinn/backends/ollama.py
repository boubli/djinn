"""
Ollama Backend - Local LLM via Ollama.
"""
import requests
from typing import Optional


class OllamaBackend:
    """Ollama API backend for local LLM inference."""
    
    DEFAULT_URL = "http://localhost:11434/api/generate"
    DEFAULT_MODEL = "llama3.2-vision:latest"
    
    def __init__(self, url: Optional[str] = None, model: Optional[str] = None):
        self.url = url or self.DEFAULT_URL
        self.model = model or self.DEFAULT_MODEL
    
    def generate(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generate a response from Ollama."""
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower for more consistent commands
                        "num_predict": 200,  # Commands should be short
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._clean_response(result.get("response", ""))
            else:
                return None
                
        except requests.exceptions.ConnectionError:
            return None
        except Exception:
            return None
    
    def _clean_response(self, text: str) -> str:
        """Clean up the LLM response."""
        text = text.strip()
        
        # Remove markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```bash or similar) and last line (```)
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()
        
        # Remove backticks around the whole command
        if text.startswith("`") and text.endswith("`"):
            text = text[1:-1]
        
        return text
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """List available models."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except:
            pass
        return []
