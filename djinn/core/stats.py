"""
Stats Module - Track and display usage statistics.
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class StatsManager:
    """Manages usage statistics for DJINN."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            home = Path.home()
            djinn_dir = home / ".djinn"
            djinn_dir.mkdir(exist_ok=True)
            db_path = str(djinn_dir / "history.db")
        
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure stats tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_type TEXT,
                    plugin TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    execution_time_ms INTEGER,
                    success INTEGER DEFAULT 1
                )
            """)
            conn.commit()
    
    def log_usage(self, command_type: str, plugin: str = None, 
                  execution_time_ms: int = 0, success: bool = True):
        """Log a command usage."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO usage_stats (command_type, plugin, execution_time_ms, success)
                VALUES (?, ?, ?, ?)
            """, (command_type, plugin, execution_time_ms, 1 if success else 0))
            conn.commit()
    
    def get_summary(self) -> Dict:
        """Get usage summary statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total commands
            total = conn.execute("SELECT COUNT(*) FROM usage_stats").fetchone()[0]
            
            # Success rate
            successes = conn.execute(
                "SELECT COUNT(*) FROM usage_stats WHERE success = 1"
            ).fetchone()[0]
            success_rate = (successes / total * 100) if total > 0 else 0
            
            # Most used plugins
            top_plugins = conn.execute("""
                SELECT plugin, COUNT(*) as cnt FROM usage_stats 
                WHERE plugin IS NOT NULL
                GROUP BY plugin ORDER BY cnt DESC LIMIT 5
            """).fetchall()
            
            # Commands today
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = conn.execute("""
                SELECT COUNT(*) FROM usage_stats 
                WHERE date(timestamp) = ?
            """, (today,)).fetchone()[0]
            
            # Commands this week
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            week_count = conn.execute("""
                SELECT COUNT(*) FROM usage_stats 
                WHERE date(timestamp) >= ?
            """, (week_ago,)).fetchone()[0]
            
            # Time saved estimate (assuming 30 seconds saved per command)
            time_saved_seconds = total * 30
            
            return {
                "total_commands": total,
                "success_rate": round(success_rate, 1),
                "top_plugins": dict(top_plugins) if top_plugins else {},
                "today": today_count,
                "this_week": week_count,
                "time_saved_minutes": time_saved_seconds // 60,
            }
    
    def get_daily_activity(self, days: int = 7) -> List[Dict]:
        """Get daily command counts for the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            results = conn.execute("""
                SELECT date(timestamp) as day, COUNT(*) as cnt
                FROM usage_stats
                WHERE date(timestamp) >= date('now', ?)
                GROUP BY day ORDER BY day
            """, (f"-{days} days",)).fetchall()
            return [{"date": r[0], "count": r[1]} for r in results]
