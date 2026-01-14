"""
TUI Components for DJINN v2.2.0
Interactive Terminal User Interfaces using Textual
"""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Button, Input, Tree, Log
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual import events
from textual.binding import Binding
import psutil
import os
from pathlib import Path
from datetime import datetime


class ProcessKillerTUI(App):
    """Interactive process killer with vim-style navigation."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("k", "kill_selected", "Kill Process"),
        ("r", "refresh", "Refresh"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]
    
    CSS = """
    DataTable {
        height: 100%;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("PID", "Name", "CPU%", "Memory%", "Status")
        table.cursor_type = "row"
        self.refresh_processes()
    
    def refresh_processes(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                table.add_row(
                    str(proc.info['pid']),
                    proc.info['name'][:30],
                    f"{proc.info['cpu_percent']:.1f}",
                    f"{proc.info['memory_percent']:.1f}",
                    proc.info['status']
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def action_refresh(self) -> None:
        self.refresh_processes()
    
    def action_kill_selected(self) -> None:
        table = self.query_one(DataTable)
        row_key = table.cursor_row
        if row_key is not None:
            row = table.get_row_at(row_key)
            pid = int(row[0])
            try:
                proc = psutil.Process(pid)
                proc.kill()
                self.refresh_processes()
            except:
                pass


class FileTreeNavigator(App):
    """File tree navigator like ranger/yazi."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("enter", "open_file", "Open"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Tree("Files")
        yield Footer()
    
    def on_mount(self) -> None:
        tree = self.query_one(Tree)
        self.populate_tree(tree.root, Path.cwd())
    
    def populate_tree(self, node, path: Path, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
        
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    branch = node.add(f"📁 {item.name}", data=item)
                    if current_depth < max_depth - 1:
                        self.populate_tree(branch, item, max_depth, current_depth + 1)
                else:
                    node.add(f"📄 {item.name}", data=item)
        except PermissionError:
            pass


class JSONExplorer(App):
    """Collapsible JSON viewer/editor."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    
    def __init__(self, json_data: dict):
        super().__init__()
        self.json_data = json_data
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Tree("JSON Root")
        yield Footer()
    
    def on_mount(self) -> None:
        tree = self.query_one(Tree)
        self.build_json_tree(tree.root, self.json_data)
    
    def build_json_tree(self, node, data, key="root"):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    branch = node.add(f"🔑 {k}", expand=True)
                    self.build_json_tree(branch, v, k)
                else:
                    node.add(f"{k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = node.add(f"[{i}]", expand=True)
                    self.build_json_tree(branch, item, str(i))
                else:
                    node.add(f"[{i}]: {item}")


class LogWatcher(App):
    """Multi-tail log viewer with regex highlighting."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear", "Clear"),
    ]
    
    def __init__(self, log_file: str):
        super().__init__()
        self.log_file = log_file
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Log(auto_scroll=True)
        yield Footer()
    
    def on_mount(self) -> None:
        self.watch_log()
    
    def watch_log(self) -> None:
        log_widget = self.query_one(Log)
        try:
            with open(self.log_file, 'r') as f:
                # Read existing content
                for line in f.readlines()[-50:]:  # Last 50 lines
                    log_widget.write_line(line.rstrip())
        except FileNotFoundError:
            log_widget.write_line(f"Log file not found: {self.log_file}")
    
    def action_clear(self) -> None:
        log_widget = self.query_one(Log)
        log_widget.clear()


class SummonDashboard(App):
    """Main DJINN dashboard with widgets."""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "show_stats", "Stats"),
        ("2", "show_history", "History"),
        ("3", "show_plugins", "Plugins"),
    ]
    
    CSS = """
    .box {
        border: solid green;
        height: 10;
        margin: 1;
        padding: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📊 DJINN Stats", classes="box", id="stats"),
            Static("📜 Recent History", classes="box", id="history"),
            Static("🔌 Active Plugins", classes="box", id="plugins"),
        )
        yield Footer()
    
    def on_mount(self) -> None:
        self.load_stats()
    
    def load_stats(self) -> None:
        from djinn.core import StatsManager, HistoryManager
        
        stats = StatsManager()
        history = HistoryManager()
        
        summary = stats.get_summary()
        recent = history.get_recent(5)
        
        stats_text = f"""
Commands Today: {summary.get('today', 0)}
Total Commands: {summary.get('total', 0)}
Success Rate: {summary.get('success_rate', 0):.1f}%
"""
        
        history_text = "\n".join([
            f"• {entry['prompt'][:30]}..." for entry in recent
        ])
        
        self.query_one("#stats", Static).update(stats_text)
        self.query_one("#history", Static).update(history_text)


def run_process_killer():
    """Launch process killer TUI."""
    app = ProcessKillerTUI()
    app.run()


def run_file_navigator():
    """Launch file navigator TUI."""
    app = FileTreeNavigator()
    app.run()


def run_json_explorer(data: dict):
    """Launch JSON explorer with data."""
    app = JSONExplorer(data)
    app.run()


def run_log_watcher(log_file: str):
    """Launch log watcher for a file."""
    app = LogWatcher(log_file)
    app.run()


def run_dashboard():
    """Launch main DJINN dashboard."""
    app = SummonDashboard()
    app.run()
