"""
History Manager - SQLite-backed command history storage.
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class HistoryManager:
    """Manages command history with SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to user's home directory
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            db_path = str(djinn_dir / "history.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    command TEXT NOT NULL,
                    backend TEXT,
                    model TEXT,
                    language TEXT DEFAULT 'en',
                    context TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    favorite INTEGER DEFAULT 0,
                    tags TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_favorite ON history(favorite)")
            conn.commit()
    
    def add(self, prompt: str, command: str, backend: str = None, model: str = None,
            language: str = "en", context: str = None, tags: List[str] = None) -> int:
        """Add a command to history."""
        tags_str = ",".join(tags) if tags else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO history (prompt, command, backend, model, language, context, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (prompt, command, backend, model, language, context, tags_str))
            conn.commit()
            return cursor.lastrowid
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get recent history entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM history ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_favorites(self) -> List[Dict]:
        """Get favorite commands."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM history WHERE favorite = 1 ORDER BY timestamp DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search history by prompt or command."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM history 
                WHERE prompt LIKE ? OR command LIKE ?
                ORDER BY timestamp DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def toggle_favorite(self, entry_id: int) -> bool:
        """Toggle favorite status of an entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT favorite FROM history WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            if row is None:
                return False
            
            new_status = 0 if row[0] else 1
            conn.execute("UPDATE history SET favorite = ? WHERE id = ?", (new_status, entry_id))
            conn.commit()
            return bool(new_status)
    
    def delete(self, entry_id: int) -> bool:
        """Delete a history entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def clear(self) -> int:
        """Clear all history (except favorites)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM history WHERE favorite = 0")
            conn.commit()
            return cursor.rowcount
    
    def get_stats(self) -> Dict:
        """Get history statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
            favorites = conn.execute("SELECT COUNT(*) FROM history WHERE favorite = 1").fetchone()[0]
            backends = conn.execute("""
                SELECT backend, COUNT(*) FROM history 
                GROUP BY backend ORDER BY COUNT(*) DESC
            """).fetchall()
            
            return {
                "total": total,
                "favorites": favorites,
                "by_backend": dict(backends) if backends else {}
            }
