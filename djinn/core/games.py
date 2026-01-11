"""
Terminal Games and Quiz - Fun learning through games.
"""
import random
import time
from typing import Dict, List, Optional


class TypingGame:
    """Typing speed practice with CLI commands."""
    
    COMMANDS = [
        "git status",
        "docker ps",
        "ls -la",
        "kubectl get pods",
        "npm install",
        "python -m venv venv",
        "curl -X GET",
        "ssh user@host",
        "tar -xzvf archive.tar.gz",
        "find . -name '*.py'",
        "grep -r 'pattern' .",
        "chmod +x script.sh",
        "systemctl status nginx",
        "docker-compose up -d",
        "git push origin main",
    ]
    
    def __init__(self):
        self.score = 0
        self.rounds = 0
        self.total_time = 0
    
    def get_challenge(self) -> str:
        """Get a random command to type."""
        return random.choice(self.COMMANDS)
    
    def check_answer(self, challenge: str, answer: str, time_taken: float) -> Dict:
        """Check typing accuracy and speed."""
        self.rounds += 1
        correct = challenge == answer
        
        if correct:
            self.score += 1
            wpm = len(challenge.split()) / (time_taken / 60) if time_taken > 0 else 0
            cpm = len(challenge) / (time_taken / 60) if time_taken > 0 else 0
        else:
            wpm = 0
            cpm = 0
        
        self.total_time += time_taken
        
        return {
            "correct": correct,
            "expected": challenge,
            "got": answer,
            "time_seconds": time_taken,
            "wpm": int(wpm),
            "cpm": int(cpm),
            "score": self.score,
            "rounds": self.rounds,
        }
    
    def get_stats(self) -> Dict:
        """Get game statistics."""
        return {
            "score": self.score,
            "rounds": self.rounds,
            "accuracy": f"{(self.score/self.rounds*100):.1f}%" if self.rounds > 0 else "0%",
            "total_time": f"{self.total_time:.1f}s",
            "avg_time": f"{(self.total_time/self.rounds):.1f}s" if self.rounds > 0 else "0s",
        }


class CLIQuiz:
    """Quiz to learn CLI commands."""
    
    QUESTIONS = [
        {
            "q": "Which command shows disk usage in human-readable format?",
            "options": ["df -h", "du -a", "ls -l", "cat disk"],
            "answer": 0,
            "explanation": "df -h shows disk filesystem usage with -h for human-readable sizes"
        },
        {
            "q": "How do you find files by name recursively?",
            "options": ["ls -R", "find . -name", "grep -r", "locate file"],
            "answer": 1,
            "explanation": "find . -name 'pattern' searches recursively from current directory"
        },
        {
            "q": "What does 'chmod 755' give to a file?",
            "options": ["Read only", "Owner: rwx, Others: rx", "Full access to all", "No access"],
            "answer": 1,
            "explanation": "755 = Owner can read/write/execute, Group and Others can read/execute"
        },
        {
            "q": "How do you kill a process by name?",
            "options": ["kill name", "pkill name", "stop name", "end name"],
            "answer": 1,
            "explanation": "pkill kills processes by name pattern, kill requires PID"
        },
        {
            "q": "Which git command undoes the last commit but keeps changes?",
            "options": ["git revert HEAD", "git reset --soft HEAD~1", "git undo", "git uncommit"],
            "answer": 1,
            "explanation": "git reset --soft HEAD~1 moves HEAD back but keeps changes staged"
        },
        {
            "q": "How do you watch a file for changes?",
            "options": ["cat -f", "tail -f", "watch file", "follow file"],
            "answer": 1,
            "explanation": "tail -f follows/watches a file and shows new content as it's added"
        },
        {
            "q": "What does 'docker ps -a' show?",
            "options": ["All images", "All containers", "Running containers", "Stopped containers"],
            "answer": 1,
            "explanation": "-a shows ALL containers including stopped ones, without -a only running"
        },
        {
            "q": "How do you create a symbolic link?",
            "options": ["ln source target", "ln -s target link", "link source target", "mklink"],
            "answer": 1,
            "explanation": "ln -s creates a symbolic (soft) link, without -s creates hard link"
        },
        {
            "q": "Which command shows environment variables?",
            "options": ["vars", "env", "show env", "list vars"],
            "answer": 1,
            "explanation": "env or printenv shows all environment variables"
        },
        {
            "q": "How do you search command history?",
            "options": ["history | grep", "search history", "find history", "Ctrl+H"],
            "answer": 0,
            "explanation": "history | grep pattern searches through command history"
        },
    ]
    
    def __init__(self):
        self.score = 0
        self.asked = []
    
    def get_question(self) -> Optional[Dict]:
        """Get a random unasked question."""
        available = [i for i in range(len(self.QUESTIONS)) if i not in self.asked]
        if not available:
            return None
        
        idx = random.choice(available)
        self.asked.append(idx)
        q = self.QUESTIONS[idx].copy()
        q["index"] = idx
        return q
    
    def answer(self, question_idx: int, answer_idx: int) -> Dict:
        """Check an answer."""
        q = self.QUESTIONS[question_idx]
        correct = answer_idx == q["answer"]
        
        if correct:
            self.score += 1
        
        return {
            "correct": correct,
            "correct_answer": q["options"][q["answer"]],
            "explanation": q["explanation"],
            "score": self.score,
            "total": len(self.asked),
        }
    
    def get_score(self) -> Dict:
        """Get quiz score."""
        return {
            "score": self.score,
            "total": len(self.asked),
            "percentage": f"{(self.score/len(self.asked)*100):.0f}%" if self.asked else "0%",
            "remaining": len(self.QUESTIONS) - len(self.asked),
        }
    
    def reset(self):
        """Reset the quiz."""
        self.score = 0
        self.asked = []


class CommandMemory:
    """Memory game with commands and their descriptions."""
    
    PAIRS = [
        ("ls", "list directory"),
        ("cd", "change directory"),
        ("pwd", "print working directory"),
        ("cp", "copy files"),
        ("mv", "move files"),
        ("rm", "remove files"),
        ("cat", "display file contents"),
        ("grep", "search text patterns"),
    ]
    
    def __init__(self):
        self.cards = []
        self.revealed = []
        self.matched = []
        self.moves = 0
        self._setup()
    
    def _setup(self):
        """Setup the game board."""
        pairs = random.sample(self.PAIRS, min(6, len(self.PAIRS)))
        self.cards = []
        for cmd, desc in pairs:
            self.cards.append({"type": "cmd", "value": cmd, "pair": desc})
            self.cards.append({"type": "desc", "value": desc, "pair": cmd})
        random.shuffle(self.cards)
        self.revealed = [False] * len(self.cards)
        self.matched = [False] * len(self.cards)
        self.moves = 0
    
    def reveal(self, idx: int) -> str:
        """Reveal a card."""
        if 0 <= idx < len(self.cards) and not self.matched[idx]:
            self.revealed[idx] = True
            return self.cards[idx]["value"]
        return ""
    
    def check_match(self, idx1: int, idx2: int) -> bool:
        """Check if two cards match."""
        self.moves += 1
        card1 = self.cards[idx1]
        card2 = self.cards[idx2]
        
        matched = card1["pair"] == card2["value"]
        if matched:
            self.matched[idx1] = True
            self.matched[idx2] = True
        else:
            self.revealed[idx1] = False
            self.revealed[idx2] = False
        
        return matched
    
    def is_complete(self) -> bool:
        """Check if game is complete."""
        return all(self.matched)
    
    def get_board(self) -> List[str]:
        """Get current board state."""
        return [
            self.cards[i]["value"] if self.revealed[i] or self.matched[i] else "?"
            for i in range(len(self.cards))
        ]
