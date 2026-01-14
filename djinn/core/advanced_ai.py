"""
Remaining AI Features for DJINN v2.2.0
"""
import os
import json
from pathlib import Path
from typing import List, Dict


class PersonaMorphing:
    """Change AI persona/tone dynamically."""
    
    PERSONAS = {
        "strict_senior": {
            "system_prompt": "You are a strict senior engineer. Be critical, point out potential issues, and suggest best practices. Keep responses concise and technical.",
            "style": "Professional and demanding"
        },
        "helpful_junior": {
            "system_prompt": "You are a helpful junior developer eager to learn and assist. Be friendly, ask clarifying questions, and explain your reasoning. Use simple language.",
            "style": "Friendly and educational"
        },
        "sarcastic_dev": {
            "system_prompt": "You are a sarcastic but knowledgeable developer. Make witty remarks while providing accurate information. Keep it fun.",
            "style": "Sarcastic and humorous"
        },
        "minimal": {
            "system_prompt": "Provide only the essential information. No explanations unless asked. Be extremely concise.",
            "style": "Minimal and direct"
        },
        "enthusiastic": {
            "system_prompt": "You are an enthusiastic developer who loves coding! Be positive, energetic, and encouraging. Use emojis and exclamation marks!",
            "style": "Energetic and positive"
        }
    }
    
    def __init__(self):
        self.config_file = Path.home() / ".djinn" / "persona.json"
        self.current_persona = self.load_persona()
    
    def load_persona(self) -> str:
        """Load current persona."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f).get("persona", "helpful_junior")
        return "helpful_junior"
    
    def set_persona(self, persona: str):
        """Set current persona."""
        if persona not in self.PERSONAS:
            raise ValueError(f"Unknown persona. Available: {', '.join(self.PERSONAS.keys())}")
        
        self.current_persona = persona
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({"persona": persona}, f)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for current persona."""
        return self.PERSONAS[self.current_persona]["system_prompt"]
    
    def list_personas(self) -> Dict:
        """List all available personas."""
        return self.PERSONAS


class PredictiveNextStep:
    """Predict and suggest next command based on history."""
    
    def __init__(self):
        self.history_file = Path.home() / ".djinn" / "command_history.json"
    
    def record_command(self, command: str):
        """Record executed command."""
        history = self._load_history()
        history.append({
            "command": command,
            "timestamp": str(Path.cwd()),
            "directory": str(Path.cwd())
        })
        
        # Keep last 1000 commands
        history = history[-1000:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f)
    
    def _load_history(self) -> List[Dict]:
        """Load command history."""
        if not self.history_file.exists():
            return []
        
        with open(self.history_file) as f:
            return json.load(f)
    
    def predict_next(self, current_command: str = None) -> List[str]:
        """Predict next likely commands."""
        history = self._load_history()
        
        if not history or len(history) < 2:
            return []
        
        # Find patterns: what commonly follows the last command
        last_cmd = history[-1]["command"] if not current_command else current_command
        
        following_commands = []
        for i in range(len(history) - 1):
            if history[i]["command"] == last_cmd:
                following_commands.append(history[i + 1]["command"])
        
        # Count frequencies
        from collections import Counter
        counter = Counter(following_commands)
        
        # Return top 3 most common
        return [cmd for cmd, count in counter.most_common(3)]


class VoiceMode:
    """Voice interaction with DJINN."""
    
    def __init__(self, engine):
        self.engine = engine
        self.conversation_history = []
    
    def listen(self) -> str:
        """Listen to user voice input and convert to text."""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("🎤 Listening...")
                audio = recognizer.listen(source, timeout=5)
                
                text = recognizer.recognize_google(audio)
                return text
        except ImportError:
            return "Error: speech_recognition not installed. Run: pip install SpeechRecognition pyaudio"
        except Exception as e:
            return f"Error: {e}"
    
    def speak(self, text: str):
        """Convert text to speech."""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except ImportError:
            print("Error: pyttsx3 not installed. Run: pip install pyttsx3")
        except Exception as e:
            print(f"Error: {e}")
    
    def interactive_session(self):
        """Run interactive voice session."""
        from rich.console import Console
        console = Console()
        
        console.print("[bold green]🎤 Voice Mode Activated[/bold green]")
        console.print("[muted]Say 'exit' or 'quit' to stop[/muted]\n")
        
        while True:
            # Listen
            user_input = self.listen()
            
            if not user_input or "error" in user_input.lower():
                console.print(f"[error]{user_input}[/error]")
                continue
            
            console.print(f"[prompt]You:[/prompt] {user_input}")
            
            # Check for exit
            if user_input.lower() in ["exit", "quit", "stop"]:
                self.speak("Goodbye!")
                break
            
            # Generate response
            self.conversation_history.append({"role": "user", "content": user_input})
            
            response = self.engine.generate(user_input)
            self.conversation_history.append({"role": "assistant", "content": response})
            
            console.print(f"[success]DJINN:[/success] {response}\n")
            
            # Speak response
            self.speak(response)
