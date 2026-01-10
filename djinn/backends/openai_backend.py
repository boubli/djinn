"""
OpenAI Backend - Cloud LLM via OpenAI API.
"""
import os
from typing import Optional

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class OpenAIBackend:
    """OpenAI API backend for cloud LLM inference."""
    
    DEFAULT_MODEL = "gpt-4o-mini"
    
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or self.DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            if not HAS_OPENAI:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
            if not self.api_key:
                raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def generate(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Generate a response from OpenAI."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=200,
            )
            
            content = response.choices[0].message.content
            return self._clean_response(content)
            
        except Exception as e:
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
        """Check if OpenAI API is accessible."""
        return bool(self.api_key)
