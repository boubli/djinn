"""
Codebase Chat - Interactive chatbot aware of all files in current directory.

Example:
    djinn chat
"""
import os
from pathlib import Path
from typing import List, Dict


class CodebaseContext:
    """Manages codebase context for chat sessions."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.file_index = {}
        self.indexed = False
    
    def index_codebase(self, max_files: int = 100):
        """Index all files in the code base."""
        self.file_index = {}
        count = 0
        
        for root, dirs, files in os.walk(self.root_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build']]
            
            for file in files:
                if count >= max_files:
                    break
                
                file_path = Path(root) / file
                try:
                    rel_path = file_path.relative_to(self.root_path)
                    
                    # Only index text files
                    if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go', '.rs', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.xml']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            self.file_index[str(rel_path)] = {
                                "path": str(file_path),
                                "content": content[:2000],  # First 2000 chars
                                "size": len(content),
                                "lines": content.count('\n')
                            }
                            count += 1
                except:
                    continue
        
        self.indexed = True
        return count
    
    def get_file_list(self) -> str:
        """Get summary of indexed files."""
        if not self.indexed:
            self.index_codebase()
        
        file_list = []
        for rel_path, info in self.file_index.items():
            file_list.append(f"- {rel_path} ({info['lines']} lines)")
        
        return "\n".join(file_list[:50])  # Limit to 50 files for context
    
    def get_file_content(self, file_path: str) -> str:
        """Get content of a specific file."""
        if file_path in self.file_index:
            full_path = self.file_index[file_path]["path"]
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except:
                pass
        return None
    
    def search_files(self, query: str) -> List[str]:
        """Search for files matching query."""
        results = []
        query_lower = query.lower()
        
        for rel_path in self.file_index.keys():
            if query_lower in rel_path.lower():
                results.append(rel_path)
        
        return results


class CodebaseChat:
    """Interactive codebase-aware chat."""
    
    def __init__(self, engine, root_path: str = "."):
        self.engine = engine
        self.context = CodebaseContext(root_path)
        self.chat_history = []
    
    def start(self):
        """Start the codebase chat session."""
        # Index codebase first
        num_files = self.context.index_codebase()
        return num_files
    
    def get_context_prompt(self) -> str:
        """Build context prompt for the LLM."""
        file_list = self.context.get_file_list()
        
        context = f"""You are chatting about a codebase.

Files in this project:
{file_list}

Answer questions about the code, suggest improvements, or help debug issues.
Be concise and practical."""
        
        return context
    
    def ask(self, question: str) -> str:
        """Ask a question about the codebase."""
        # Build prompt with context
        system_prompt = self.get_context_prompt()
        
        # Add chat history
        history_text = ""
        for msg in self.chat_history[-5:]:  # Last 5 messages
            history_text += f"\nUser: {msg['question']}\nAssistant: {msg['answer']}\n"
        
        full_prompt = f"""{history_text}
User: {question}
Assistant:"""
        
        answer = self.engine.backend.generate(
            full_prompt,
            system_prompt=system_prompt
        )
        
        # Save to history
        self.chat_history.append({
            "question": question,
            "answer": answer
        })
        
        return answer
    
    def show_file(self, file_path: str) -> str:
        """Show contents of a specific file."""
        content = self.context.get_file_content(file_path)
        if content:
            return content
        else:
            # Try searching
            matches = self.context.search_files(file_path)
            if matches:
                return f"Did you mean one of these?\n" + "\n".join(matches)
            return f"File not found: {file_path}"
