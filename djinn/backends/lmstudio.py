"""
LM Studio Backend - Local LLM via LM Studio's OpenAI-compatible API.
"""
import requests
from typing import Optional


class LMStudioBackend:
    """LM Studio backend using OpenAI-compatible API."""
    
    DEFAULT_URL = "http://localhost:1234/v1/chat/completions"
    DEFAULT_MODEL = "local-model"  # LM Studio uses whatever is loaded
    
    def __init__(self, url: Optional[str] = None, model: Optional[str] = None):
        self.url = url or self.DEFAULT_URL
        self.model = model or self.DEFAULT_MODEL
    
    def generate(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generate a response from LM Studio."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 200,
                    "stream": False,
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return self._clean_response(content)
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
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()
        
        if text.startswith("`") and text.endswith("`"):
            text = text[1:-1]
        
        return text
    
    def is_available(self) -> bool:
        """Check if LM Studio is running."""
        try:
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False
