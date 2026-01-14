"""
Remaining File and System Tools for DJINN v2.2.0
"""
import tempfile
import os
import subprocess
from pathlib import Path
from typing import List
import json


class PDFMerger:
    """Merge multiple PDF files."""
    
    @staticmethod
    def merge_pdfs(input_files: List[str], output_file: str):
        """Merge PDF files."""
        try:
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            for pdf in input_files:
                merger.append(pdf)
            
            merger.write(output_file)
            merger.close()
            
            return f"Merged {len(input_files)} PDFs into {output_file}"
        except ImportError:
            return "Error: PyPDF2 not installed. Run: pip install PyPDF2"
        except Exception as e:
            return f"Error: {e}"


class ClipboardManager:
    """Clipboard history manager."""
    
    def __init__(self):
        self.history_file = Path.home() / ".djinn" / "clipboard_history.json"
        self.history_file.parent.mkdir(exist_ok=True)
        self.max_items = 50
    
    def save_to_clipboard(self, text: str):
        """Save text to clipboard and history."""
        import pyperclip
        
        # Copy to system clipboard
        pyperclip.copy(text)
        
        # Save to history
        history = self.load_history()
        history.insert(0, {
            "text": text[:500],  # Limit size
            "timestamp": str(Path.cwd())
        })
        
        # Keep only last N items
        history = history[:self.max_items]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def load_history(self) -> List[dict]:
        """Load clipboard history."""
        if not self.history_file.exists():
            return []
        
        with open(self.history_file) as f:
            return json.load(f)
    
    def get_from_history(self, index: int) -> str:
        """Get item from history."""
        history = self.load_history()
        if 0 <= index < len(history):
            return history[index]["text"]
        return None
    
    def clear_history(self):
        """Clear clipboard history."""
        if self.history_file.exists():
            self.history_file.unlink()


class TempFileManager:
    """Create and manage temporary files."""
    
    @staticmethod
    def create_temp_file(suffix: str = ".txt", prefix: str = "djinn_", content: str = None) -> str:
        """Create a temporary file and return its path."""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        
        if content:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
        else:
            os.close(fd)
        
        return path
    
    @staticmethod
    def create_and_edit(suffix: str = ".txt", editor: str = None) -> str:
        """Create temp file and open in editor."""
        path = TempFileManager.create_temp_file(suffix=suffix)
        
        # Determine editor
        if not editor:
            editor = os.environ.get("EDITOR", "vim" if os.name == "posix" else "notepad")
        
        # Open editor
        subprocess.run([editor, path])
        
        return path
    
    @staticmethod
    def create_temp_dir(prefix: str = "djinn_") -> str:
        """Create a temporary directory."""
        return tempfile.mkdtemp(prefix=prefix)


class KubernetesLens:
    """Simple Kubernetes pod viewer/log streamer."""
    
    @staticmethod
    def list_pods(namespace: str = "default") -> List[dict]:
        """List pods in namespace."""
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                pods = []
                
                for item in data.get("items", []):
                    pods.append({
                        "name": item["metadata"]["name"],
                        "status": item["status"]["phase"],
                        "restarts": sum(c.get("restartCount", 0) for c in item["status"].get("containerStatuses", [])),
                        "age": item["metadata"].get("creationTimestamp", "")
                    })
                
                return pods
            else:
                return [{"error": result.stderr}]
        except FileNotFoundError:
            return [{"error": "kubectl not found"}]
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def get_logs(pod_name: str, namespace: str = "default", tail: int = 100) -> str:
        """Get pod logs."""
        try:
            result = subprocess.run(
                ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail}"],
                capture_output=True,
                text=True
            )
            
            return result.stdout if result.returncode == 0 else result.stderr
        except:
            return "Error fetching logs"
    
    @staticmethod
    def describe_pod(pod_name: str, namespace: str = "default") -> str:
        """Describe a pod."""
        try:
            result = subprocess.run(
                ["kubectl", "describe", "pod", pod_name, "-n", namespace],
                capture_output=True,
                text=True
            )
            
            return result.stdout if result.returncode == 0 else result.stderr
        except:
            return "Error describing pod"


class MusicPlayer:
    """Simple music player for Spotify."""
    
    @staticmethod
    def spotify_status() -> dict:
        """Get current Spotify status (requires spotipy)."""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
                redirect_uri="http://localhost:8888/callback",
                scope="user-read-playback-state,user-modify-playback-state"
            ))
            
            current = sp.current_playback()
            
            if current and current.get("is_playing"):
                track = current["item"]
                return {
                    "playing": True,
                    "track": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "progress_ms": current["progress_ms"],
                    "duration_ms": track["duration_ms"]
                }
            else:
                return {"playing": False}
        except ImportError:
            return {"error": "spotipy not installed. Run: pip install spotipy"}
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def spotify_control(action: str):
        """Control Spotify playback."""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
                client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
                redirect_uri="http://localhost:8888/callback",
                scope="user-read-playback-state,user-modify-playback-state"
            ))
            
            if action == "play":
                sp.start_playback()
            elif action == "pause":
                sp.pause_playback()
            elif action == "next":
                sp.next_track()
            elif action == "previous":
                sp.previous_track()
            
            return f"{action.title()} successful"
        except:
            return f"Error: Could not {action}"
