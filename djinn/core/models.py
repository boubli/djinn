"""
Model Manager - Download and manage local LLM models.
"""
import subprocess
import requests
import json
from typing import List, Dict, Optional
from pathlib import Path


class ModelManager:
    """Manages local LLM model downloads and operations."""
    
    # Popular models with their details
    POPULAR_MODELS = {
        "llama3": {
            "name": "Llama 3",
            "sizes": ["8b", "70b"],
            "description": "Meta's latest Llama model, excellent general-purpose",
            "default_size": "8b"
        },
        "llama3.2": {
            "name": "Llama 3.2",
            "sizes": ["1b", "3b"],
            "description": "Lightweight Llama models for edge devices",
            "default_size": "3b"
        },
        "mistral": {
            "name": "Mistral",
            "sizes": ["7b"],
            "description": "Fast and efficient, great for coding",
            "default_size": "7b"
        },
        "mixtral": {
            "name": "Mixtral",
            "sizes": ["8x7b", "8x22b"],
            "description": "Mixture of experts model, very capable",
            "default_size": "8x7b"
        },
        "codellama": {
            "name": "Code Llama",
            "sizes": ["7b", "13b", "34b"],
            "description": "Specialized for code generation",
            "default_size": "7b"
        },
        "deepseek-coder": {
            "name": "DeepSeek Coder",
            "sizes": ["1.3b", "6.7b", "33b"],
            "description": "Excellent code-focused model",
            "default_size": "6.7b"
        },
        "phi3": {
            "name": "Phi-3",
            "sizes": ["mini", "medium"],
            "description": "Microsoft's compact powerful model",
            "default_size": "mini"
        },
        "gemma2": {
            "name": "Gemma 2",
            "sizes": ["2b", "9b", "27b"],
            "description": "Google's open model, great quality",
            "default_size": "9b"
        },
        "qwen2.5": {
            "name": "Qwen 2.5",
            "sizes": ["0.5b", "1.5b", "3b", "7b", "14b", "32b", "72b"],
            "description": "Alibaba's multilingual model",
            "default_size": "7b"
        },
        "qwen2.5-coder": {
            "name": "Qwen 2.5 Coder",
            "sizes": ["1.5b", "7b", "32b"],
            "description": "Excellent for code, competes with GPT-4",
            "default_size": "7b"
        },
        "starcoder2": {
            "name": "StarCoder 2",
            "sizes": ["3b", "7b", "15b"],
            "description": "Best for multi-language code completion",
            "default_size": "7b"
        },
        "neural-chat": {
            "name": "Neural Chat",
            "sizes": ["7b"],
            "description": "Intel's fine-tuned chat model",
            "default_size": "7b"
        },
    }
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.lmstudio_models_dir = Path.home() / ".cache" / "lm-studio" / "models"
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_installed_ollama(self) -> List[Dict]:
        """List installed Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
        except:
            pass
        return []
    
    def download_ollama(self, model_name: str, callback=None) -> bool:
        """Download a model using Ollama.
        
        Args:
            model_name: Name of model to download (e.g., "llama3", "mistral")
            callback: Optional callback function for progress updates
        
        Returns:
            True if download was initiated successfully
        """
        try:
            # Use subprocess to run `ollama pull` which shows nice progress
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                if callback:
                    callback(line.strip())
                else:
                    print(line.strip())
            
            process.wait()
            return process.returncode == 0
        except FileNotFoundError:
            return False
        except Exception as e:
            if callback:
                callback(f"Error: {e}")
            return False
    
    def delete_ollama(self, model_name: str) -> bool:
        """Delete an Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get info about a model."""
        base_name = model_name.split(":")[0]
        return self.POPULAR_MODELS.get(base_name)
    
    def list_popular(self) -> Dict:
        """List popular models available for download."""
        return self.POPULAR_MODELS
    
    def get_recommended_for_hardware(self, vram_gb: int = 8) -> List[str]:
        """Get recommended models based on available VRAM."""
        if vram_gb >= 24:
            return ["llama3:70b", "mixtral:8x7b", "qwen2.5:32b", "deepseek-coder:33b"]
        elif vram_gb >= 12:
            return ["llama3:8b", "mistral:7b", "qwen2.5-coder:7b", "gemma2:9b"]
        elif vram_gb >= 8:
            return ["llama3:8b", "mistral:7b", "phi3:mini", "qwen2.5:7b"]
        elif vram_gb >= 6:
            return ["phi3:mini", "qwen2.5:3b", "gemma2:2b", "llama3.2:3b"]
        else:
            return ["llama3.2:1b", "qwen2.5:0.5b", "phi3:mini"]
    
    def run_model_interactive(self, model_name: str):
        """Run a model in interactive mode."""
        subprocess.run(["ollama", "run", model_name])
    
    def get_huggingface_gguf_models(self, query: str = "gguf") -> List[Dict]:
        """Search HuggingFace for GGUF models (for LM Studio)."""
        try:
            url = f"https://huggingface.co/api/models?search={query}&filter=gguf&sort=downloads&direction=-1&limit=10"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
