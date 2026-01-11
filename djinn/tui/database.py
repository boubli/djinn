"""
Database Viewer - Interactive database browser for SQL databases.
"""
import sqlite3
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from rich.table import Table
from rich.console import Console


class DatabaseViewer:
    """Interactive database viewer."""
    
    def __init__(self):
        self.console = Console()
        self.connection = None
        self.db_type = None
    
    def connect_sqlite(self, filepath: str) -> bool:
        """Connect to SQLite database."""
        try:
            self.connection = sqlite3.connect(filepath)
            self.db_type = "sqlite"
            return True
        except Exception as e:
            return False
    
    def connect_postgres(self, host: str, port: int, database: str, 
                         user: str, password: str) -> bool:
        """Connect to PostgreSQL database."""
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=host, port=port, database=database,
                user=user, password=password
            )
            self.db_type = "postgres"
            return True
        except:
            return False
    
    def connect_mysql(self, host: str, port: int, database: str,
                      user: str, password: str) -> bool:
        """Connect to MySQL database."""
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(
                host=host, port=port, database=database,
                user=user, password=password
            )
            self.db_type = "mysql"
            return True
        except:
            return False
    
    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        
        if self.db_type == "sqlite":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        elif self.db_type == "postgres":
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        elif self.db_type == "mysql":
            cursor.execute("SHOW TABLES")
        
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        return tables
    
    def get_table_schema(self, table: str) -> List[Dict]:
        """Get schema for a table."""
        if not self.connection:
            return []
        
        cursor = self.connection.cursor()
        
        if self.db_type == "sqlite":
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema = [
                {"name": col[1], "type": col[2], "nullable": not col[3], "pk": bool(col[5])}
                for col in columns
            ]
        elif self.db_type in ["postgres", "mysql"]:
            cursor.execute(f"DESCRIBE {table}" if self.db_type == "mysql" 
                          else f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}'")
            columns = cursor.fetchall()
            schema = [{"name": col[0], "type": col[1]} for col in columns]
        
        cursor.close()
        return schema
    
    def query(self, sql: str, limit: int = 100) -> Tuple[List[str], List[Tuple]]:
        """Execute a query and return results."""
        if not self.connection:
            return [], []
        
        cursor = self.connection.cursor()
        
        # Add limit if not present
        sql_lower = sql.lower().strip()
        if sql_lower.startswith("select") and "limit" not in sql_lower:
            sql = f"{sql} LIMIT {limit}"
        
        cursor.execute(sql)
        
        if sql_lower.startswith("select"):
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
        else:
            self.connection.commit()
            columns = ["affected_rows"]
            rows = [(cursor.rowcount,)]
        
        cursor.close()
        
        return columns, rows
    
    def preview_table(self, table: str, limit: int = 20) -> Tuple[List[str], List[Tuple]]:
        """Preview data from a table."""
        return self.query(f"SELECT * FROM {table} LIMIT {limit}")
    
    def count_rows(self, table: str) -> int:
        """Count rows in a table."""
        _, rows = self.query(f"SELECT COUNT(*) FROM {table}")
        return rows[0][0] if rows else 0
    
    def render_results(self, columns: List[str], rows: List[Tuple]) -> Table:
        """Render query results as a rich table."""
        table = Table(show_header=True, header_style="bold cyan")
        
        for col in columns:
            table.add_column(col)
        
        for row in rows:
            table.add_row(*[str(v)[:50] for v in row])
        
        return table
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        tables = self.list_tables()
        
        stats = {
            "type": self.db_type,
            "tables": len(tables),
            "table_details": []
        }
        
        for table in tables[:10]:  # Limit to 10 tables
            count = self.count_rows(table)
            schema = self.get_table_schema(table)
            stats["table_details"].append({
                "name": table,
                "rows": count,
                "columns": len(schema)
            })
        
        return stats
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


class SQLiteExplorer:
    """Quick SQLite file explorer."""
    
    @staticmethod
    def find_databases(directory: str = None) -> List[str]:
        """Find SQLite databases in a directory."""
        dir_path = Path(directory) if directory else Path.cwd()
        
        databases = []
        for ext in [".db", ".sqlite", ".sqlite3"]:
            databases.extend([str(f) for f in dir_path.rglob(f"*{ext}")])
        
        return databases[:20]  # Limit results
    
    @staticmethod
    def quick_info(filepath: str) -> Dict:
        """Get quick info about a SQLite database."""
        try:
            conn = sqlite3.connect(filepath)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            size = Path(filepath).stat().st_size / 1024  # KB
            
            conn.close()
            
            return {
                "path": filepath,
                "size_kb": size,
                "tables": len(tables),
                "table_names": tables[:10]
            }
        except:
            return {"path": filepath, "error": "Could not read database"}
