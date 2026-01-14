"""
Semantic File Search - Find files using natural language.

Example:
    djinn find "python script about sorting"
"""
import os
import glob
from pathlib import Path
from typing import List, Dict


class SemanticSearchEngine:
    """Semantic file search using LLM-powered pattern generation."""
    
    def __init__(self, engine):
        self.engine = engine
    
    def search(self, description: str, path: str = ".") -> List[Dict]:
        """
        Search for files matching semantic description.
        
        Args:
            description: Natural language description
            path: Starting directory
            
        Returns:
            List of matching file paths with relevance scores
        """
        # Generate search pattern from description
        pattern_prompt = f"""Given this description: "{description}"

Generate a Python glob pattern or list of keywords to find matching files.
Consider file extensions, common naming patterns, and keywords.

Return only the pattern or keywords, nothing else. Examples:
- "**/*.py" for Python files
- "**/*test*.py" for Python test files
- "**/*sort*.py && **/*algorithm*.py" for sorting algorithm files

Pattern:"""

        pattern = self.engine.backend.generate(
            pattern_prompt,
            system_prompt="You are a file search expert. Generate exact glob patterns or keywords."
        ).strip()
        
        # Execute search
        results = []
        base_path = Path(path).resolve()
        
        # Try glob pattern first
        if "*" in pattern or "**" in pattern:
            try:
                matching_files = list(base_path.glob(pattern))
                for file_path in matching_files[:50]:  # Limit results
                    if file_path.is_file():
                        results.append({
                            "path": str(file_path.relative_to(base_path)),
                            "relevance": 1.0,
                            "size": file_path.stat().st_size
                        })
            except:
                pass
        else:
            # Keyword-based search
            keywords = [k.strip().lower() for k in pattern.split("&&")]
            for root, dirs, files in os.walk(base_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_lower = file.lower()
                    # Check if all keywords match
                    if all(kw in file_lower for kw in keywords):
                        file_path = Path(root) / file
                        try:
                            results.append({
                                "path": str(file_path.relative_to(base_path)),
                                "relevance": 1.0,
                                "size": file_path.stat().st_size
                            })
                        except:
                            pass
                        
                    if len(results) >= 50:
                        break
                if len(results) >= 50:
                    break
        
        return results
    
    def search_content(self, description: str, path: str = ".") -> List[Dict]:
        """
        Search file CONTENTS using semantic understanding.
        More expensive - reads files.
        """
        results = []
        base_path = Path(path).resolve()
        
        # First, get candidate files
        candidates = self.search(description, path)
        
        # For each candidate, check content relevance
        for candidate in candidates[:20]:  # Limit to avoid too many LLM calls
            file_path = base_path / candidate["path"]
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)  # Read first 2000 chars
                
                # Ask LLM if this content matches
                check_prompt = f"""Does this code fulfill the description: "{description}"?

Code snippet:
{content}

Answer with just YES or NO:"""
                
                answer = self.engine.backend.generate(
                    check_prompt,
                    system_prompt="You are a code analyzer. Answer YES or NO only."
                ).strip().upper()
                
                if "YES" in answer:
                    candidate["relevance"] = 2.0  # Higher relevance for content match
                    results.append(candidate)
            except:
                continue
        
        return results if results else candidates


class SmartFileSearch:
    """Wrapper for semantic search functionality."""
    
    def __init__(self, engine):
        self.searcher = SemanticSearchEngine(engine)
    
    def find(self, query: str, search_content: bool = False):
        """Execute semantic file search."""
        if search_content:
            return self.searcher.search_content(query)
        else:
            return self.searcher.search(query)
