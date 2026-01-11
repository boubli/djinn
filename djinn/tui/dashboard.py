"""
TUI Dashboard - Full-screen system monitoring dashboard.
Uses rich.live for real-time updates.
"""
import psutil
import time
from datetime import datetime
from typing import Dict, List, Optional
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.console import Console, Group
from rich import box


class SystemDashboard:
    """Interactive system monitoring dashboard."""
    
    def __init__(self):
        self.console = Console()
    
    def get_cpu_info(self) -> Dict:
        """Get CPU information."""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "per_cpu": cpu_percent,
            "cores": psutil.cpu_count(),
            "freq": cpu_freq.current if cpu_freq else 0,
        }
    
    def get_memory_info(self) -> Dict:
        """Get memory information."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "total": mem.total / (1024**3),
            "used": mem.used / (1024**3),
            "percent": mem.percent,
            "swap_total": swap.total / (1024**3),
            "swap_used": swap.used / (1024**3),
            "swap_percent": swap.percent,
        }
    
    def get_disk_info(self) -> List[Dict]:
        """Get disk information."""
        disks = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "total": usage.total / (1024**3),
                    "used": usage.used / (1024**3),
                    "percent": usage.percent,
                })
            except:
                pass
        return disks
    
    def get_network_info(self) -> Dict:
        """Get network information."""
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent / (1024**2),
            "bytes_recv": net.bytes_recv / (1024**2),
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
        }
    
    def get_top_processes(self, n: int = 8) -> List[Dict]:
        """Get top processes by CPU usage."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'][:20],
                    "cpu": info['cpu_percent'] or 0,
                    "mem": info['memory_percent'] or 0,
                })
            except:
                pass
        
        return sorted(processes, key=lambda x: x['cpu'], reverse=True)[:n]
    
    def create_cpu_panel(self, cpu_info: Dict) -> Panel:
        """Create CPU panel."""
        bars = []
        for i, percent in enumerate(cpu_info['per_cpu'][:8]):
            bar_len = int(percent / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            bars.append(f"Core {i}: [{bar}] {percent:5.1f}%")
        
        content = "\n".join(bars)
        content += f"\n\nTotal: {cpu_info['percent']:.1f}% | Freq: {cpu_info['freq']:.0f}MHz"
        
        return Panel(content, title="🔥 CPU", border_style="cyan", box=box.ROUNDED)
    
    def create_memory_panel(self, mem_info: Dict) -> Panel:
        """Create memory panel."""
        ram_bar_len = int(mem_info['percent'] / 5)
        ram_bar = "█" * ram_bar_len + "░" * (20 - ram_bar_len)
        
        swap_bar_len = int(mem_info['swap_percent'] / 5) if mem_info['swap_total'] > 0 else 0
        swap_bar = "█" * swap_bar_len + "░" * (20 - swap_bar_len)
        
        content = f"RAM:  [{ram_bar}] {mem_info['percent']:5.1f}%\n"
        content += f"      {mem_info['used']:.1f}GB / {mem_info['total']:.1f}GB\n\n"
        content += f"Swap: [{swap_bar}] {mem_info['swap_percent']:5.1f}%\n"
        content += f"      {mem_info['swap_used']:.1f}GB / {mem_info['swap_total']:.1f}GB"
        
        return Panel(content, title="💾 Memory", border_style="green", box=box.ROUNDED)
    
    def create_disk_panel(self, disks: List[Dict]) -> Panel:
        """Create disk panel."""
        lines = []
        for disk in disks[:4]:
            bar_len = int(disk['percent'] / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"{disk['mountpoint'][:10]:10} [{bar}] {disk['percent']:5.1f}%")
        
        return Panel("\n".join(lines), title="💿 Disks", border_style="yellow", box=box.ROUNDED)
    
    def create_network_panel(self, net_info: Dict) -> Panel:
        """Create network panel."""
        content = f"↑ Sent:     {net_info['bytes_sent']:,.1f} MB\n"
        content += f"↓ Received: {net_info['bytes_recv']:,.1f} MB\n\n"
        content += f"📤 Packets: {net_info['packets_sent']:,}\n"
        content += f"📥 Packets: {net_info['packets_recv']:,}"
        
        return Panel(content, title="🌐 Network", border_style="magenta", box=box.ROUNDED)
    
    def create_process_panel(self, processes: List[Dict]) -> Panel:
        """Create process panel."""
        table = Table(box=None, show_header=True, header_style="bold")
        table.add_column("PID", width=8)
        table.add_column("Name", width=20)
        table.add_column("CPU%", width=8)
        table.add_column("MEM%", width=8)
        
        for proc in processes:
            table.add_row(
                str(proc['pid']),
                proc['name'],
                f"{proc['cpu']:.1f}",
                f"{proc['mem']:.1f}"
            )
        
        return Panel(table, title="⚡ Top Processes", border_style="red", box=box.ROUNDED)
    
    def create_header(self) -> Panel:
        """Create header panel."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = time.time() - psutil.boot_time()
        uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"
        
        text = Text()
        text.append("🔮 DJINN Dashboard", style="bold cyan")
        text.append(f"  |  {now}  |  Uptime: {uptime_str}", style="dim")
        text.append("  |  Press Ctrl+C to exit", style="dim italic")
        
        return Panel(text, box=box.MINIMAL)
    
    def generate_layout(self) -> Layout:
        """Generate the dashboard layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=8),
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        
        layout["left"].split_column(
            Layout(name="cpu"),
            Layout(name="memory"),
        )
        
        layout["right"].split_column(
            Layout(name="disk"),
            Layout(name="network"),
        )
        
        return layout
    
    def update_layout(self, layout: Layout):
        """Update layout with current data."""
        cpu_info = self.get_cpu_info()
        mem_info = self.get_memory_info()
        disks = self.get_disk_info()
        net_info = self.get_network_info()
        processes = self.get_top_processes()
        
        layout["header"].update(self.create_header())
        layout["cpu"].update(self.create_cpu_panel(cpu_info))
        layout["memory"].update(self.create_memory_panel(mem_info))
        layout["disk"].update(self.create_disk_panel(disks))
        layout["network"].update(self.create_network_panel(net_info))
        layout["footer"].update(self.create_process_panel(processes))
    
    def run(self, refresh_rate: float = 1.0):
        """Run the dashboard."""
        layout = self.generate_layout()
        
        with Live(layout, console=self.console, refresh_per_second=4, screen=True) as live:
            try:
                while True:
                    self.update_layout(layout)
                    time.sleep(refresh_rate)
            except KeyboardInterrupt:
                pass


class ProcessManager:
    """Interactive process manager."""
    
    def __init__(self):
        self.console = Console()
    
    def list_processes(self, sort_by: str = "cpu", n: int = 20) -> List[Dict]:
        """List processes sorted by criteria."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                processes.append({
                    "pid": info['pid'],
                    "name": info['name'][:25],
                    "user": (info['username'] or "system")[:10],
                    "cpu": info['cpu_percent'] or 0,
                    "mem": info['memory_percent'] or 0,
                    "status": info['status'][:10],
                })
            except:
                pass
        
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        elif sort_by == "mem":
            processes.sort(key=lambda x: x['mem'], reverse=True)
        elif sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower())
        
        return processes[:n]
    
    def kill_process(self, pid: int) -> bool:
        """Kill a process by PID."""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except:
            return False
    
    def get_process_details(self, pid: int) -> Optional[Dict]:
        """Get detailed info about a process."""
        try:
            proc = psutil.Process(pid)
            return {
                "pid": proc.pid,
                "name": proc.name(),
                "exe": proc.exe(),
                "cwd": proc.cwd(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent(),
                "threads": proc.num_threads(),
                "connections": len(proc.connections()),
                "open_files": len(proc.open_files()),
            }
        except:
            return None
