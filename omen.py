#!/usr/bin/env python3
"""
 ██████╗ ███╗   ███╗███████╗███╗   ██╗
██╔═══██╗████╗ ████║██╔════╝████╗  ██║
██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║
██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║
╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║
 ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝

Ghost-Writer for Your Terminal
Converts natural language comments into shell commands.

Developer: Youssef Boubli
Website:   https://boubli.tech
GitHub:    https://github.com/boubli
"""

import os
import sys
import platform
import pyperclip
import requests

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2-vision:latest"  # Or any model you have installed

LOGO = """
\033[95m ██████╗ ███╗   ███╗███████╗███╗   ██╗\033[0m
\033[95m██╔═══██╗████╗ ████║██╔════╝████╗  ██║\033[0m
\033[96m██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║\033[0m
\033[96m██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║\033[0m
\033[94m╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║\033[0m
\033[94m ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝\033[0m
\033[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m
\033[37m  Ghost-Writer for Your Terminal\033[0m
\033[90m  by Youssef Boubli • boubli.tech\033[0m
\033[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m
"""


def get_history_file():
    """Determine the shell history file based on OS and shell."""
    system = platform.system()
    
    if system == "Windows":
        # PowerShell history
        ps_history = os.path.join(
            os.environ.get("APPDATA", ""),
            "Microsoft", "Windows", "PowerShell", "PSReadLine",
            "ConsoleHost_history.txt"
        )
        if os.path.exists(ps_history):
            return ps_history
    else:
        # Unix-like systems
        home = os.path.expanduser("~")
        shell = os.environ.get("SHELL", "")
        
        if "zsh" in shell:
            return os.path.join(home, ".zsh_history")
        elif "bash" in shell:
            return os.path.join(home, ".bash_history")
    
    return None


def get_last_comment(history_file):
    """Read the last line starting with '#' from the history file."""
    if not history_file or not os.path.exists(history_file):
        return None
    
    try:
        with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # Find the last line that looks like a natural language comment
        for line in reversed(lines):
            line = line.strip()
            if line.startswith("#") and len(line) > 2:
                return line[1:].strip()  # Remove the '#' and whitespace
    except Exception as e:
        print(f"\033[91mError reading history: {e}\033[0m")
    
    return None


def query_ollama(prompt):
    """Send the natural language prompt to Ollama and get a shell command."""
    system_prompt = """You are a shell command generator. Convert the user's natural language description into a single, executable shell command.

Rules:
- Output ONLY the command, no explanations
- Use common CLI tools (ffmpeg, docker, git, etc.)
- Prefer cross-platform solutions when possible
- If the task requires multiple commands, chain them with && or use a one-liner

Example:
User: convert all mov to mp4 in this folder
Output: for f in *.mov; do ffmpeg -i "$f" "${f%.mov}.mp4"; done"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"User request: {prompt}",
                "system": system_prompt,
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"\033[91mOllama error: {response.status_code}\033[0m")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\033[91mError: Cannot connect to Ollama. Is it running?\033[0m")
        print("\033[90mStart Ollama with: ollama serve\033[0m")
        return None
    except Exception as e:
        print(f"\033[91mError: {e}\033[0m")
        return None


def main():
    print(LOGO)
    
    # Check for direct input via command line argument
    if len(sys.argv) > 1:
        intent = " ".join(sys.argv[1:])
    else:
        # Read from history
        history_file = get_history_file()
        if not history_file:
            print("\033[91mError: Could not locate shell history file.\033[0m")
            sys.exit(1)
        
        intent = get_last_comment(history_file)
        
    if not intent:
        print("\033[93mNo natural language intent found.\033[0m")
        print("\033[90mUsage: Type a comment like '# convert all mov to mp4' then run omen\033[0m")
        print("\033[90mOr:    omen \"convert all mov to mp4\"\033[0m")
        sys.exit(1)
    
    print(f"\033[96m▶ Intent:\033[0m {intent}")
    print("\033[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print("\033[93m⚡ Generating command...\033[0m\n")
    
    command = query_ollama(intent)
    
    if command:
        print(f"\033[92m✓ Command:\033[0m")
        print(f"\033[97m  {command}\033[0m\n")
        
        # Copy to clipboard
        try:
            pyperclip.copy(command)
            print("\033[92m📋 Copied to clipboard!\033[0m")
            print("\033[90mPaste with Ctrl+V (or Cmd+V on Mac)\033[0m")
        except Exception:
            print("\033[93mCould not copy to clipboard.\033[0m")
    else:
        print("\033[91m✗ Failed to generate command.\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
