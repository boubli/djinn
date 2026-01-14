"""
System Monitor Plugin for DJINN
Advanced system monitoring (CPU, RAM, Disk, Network).
"""
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
import psutil

console = Console()

# Plugin Metadata
PLUGIN_NAME = "system-monitor"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Advanced system monitoring tool."
PLUGIN_CATEGORY = "devops"


def get_size(bytes_value):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024


@click.group()
def monitor():
    """System monitoring commands."""
    pass


@monitor.command()
def cpu():
    """Show CPU usage."""
    console.print("\n[bold cyan]🖥️  CPU Information[/bold cyan]\n")
    
    # CPU info
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq()
    
    table = Table()
    table.add_column("Core", style="cyan")
    table.add_column("Usage", style="green")
    table.add_column("Bar")
    
    for i, percent in enumerate(cpu_percent):
        bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
        color = "green" if percent < 50 else "yellow" if percent < 80 else "red"
        table.add_row(f"Core {i}", f"[{color}]{percent}%[/{color}]", f"[{color}]{bar}[/{color}]")
    
    console.print(table)
    
    if cpu_freq:
        console.print(f"\n[muted]Frequency: {cpu_freq.current:.0f} MHz[/muted]")


@monitor.command()
def memory():
    """Show memory usage."""
    console.print("\n[bold cyan]💾 Memory Information[/bold cyan]\n")
    
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # RAM
    ram_percent = mem.percent
    ram_bar = "█" * int(ram_percent / 5) + "░" * (20 - int(ram_percent / 5))
    color = "green" if ram_percent < 50 else "yellow" if ram_percent < 80 else "red"
    
    console.print(f"[bold]RAM:[/bold] {get_size(mem.used)} / {get_size(mem.total)}")
    console.print(f"[{color}]{ram_bar} {ram_percent}%[/{color}]")
    
    # Swap
    console.print(f"\n[bold]Swap:[/bold] {get_size(swap.used)} / {get_size(swap.total)}")
    swap_bar = "█" * int(swap.percent / 5) + "░" * (20 - int(swap.percent / 5))
    console.print(f"[muted]{swap_bar} {swap.percent}%[/muted]")


@monitor.command()
def disk():
    """Show disk usage."""
    console.print("\n[bold cyan]💿 Disk Information[/bold cyan]\n")
    
    table = Table()
    table.add_column("Mount", style="cyan")
    table.add_column("Total")
    table.add_column("Used")
    table.add_column("Free")
    table.add_column("Usage")
    
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            percent = usage.percent
            color = "green" if percent < 50 else "yellow" if percent < 80 else "red"
            
            table.add_row(
                partition.mountpoint,
                get_size(usage.total),
                get_size(usage.used),
                get_size(usage.free),
                f"[{color}]{percent}%[/{color}]"
            )
        except:
            pass
    
    console.print(table)


@monitor.command()
def network():
    """Show network statistics."""
    console.print("\n[bold cyan]🌐 Network Information[/bold cyan]\n")
    
    net_io = psutil.net_io_counters()
    
    console.print(f"[bold]Sent:[/bold] {get_size(net_io.bytes_sent)}")
    console.print(f"[bold]Received:[/bold] {get_size(net_io.bytes_recv)}")
    console.print(f"\n[muted]Packets: ↑{net_io.packets_sent} ↓{net_io.packets_recv}[/muted]")


@monitor.command()
def all():
    """Show all system information."""
    cpu()
    memory()
    disk()
    network()


# Export the main command
main = monitor

if __name__ == "__main__":
    monitor()
