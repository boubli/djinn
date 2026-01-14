"""
Password Manager Plugin for DJINN
1Password and Bitwarden integration.
"""
import click
from rich.console import Console
from rich.table import Table
import subprocess
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "password-manager"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "1Password and Bitwarden CLI integration."


def run_op(args):
    """Run 1Password CLI."""
    try:
        result = subprocess.run(["op"] + args, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "1Password CLI not installed"


def run_bw(args):
    """Run Bitwarden CLI."""
    try:
        result = subprocess.run(["bw"] + args, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "Bitwarden CLI not installed"


@click.group()
def pw():
    """Password manager commands."""
    pass


# ==================== 1PASSWORD ====================

@pw.group(name="1p")
def onepassword():
    """1Password commands."""
    pass


@onepassword.command(name="login")
def op_login():
    """Login to 1Password."""
    console.print("[bold cyan]🔐 1Password Login[/bold cyan]\n")
    subprocess.run(["op", "signin"])


@onepassword.command(name="list")
@click.option("--vault", help="Vault name")
def op_list(vault):
    """List items in 1Password."""
    args = ["item", "list", "--format=json"]
    if vault:
        args.extend(["--vault", vault])
    
    success, stdout, stderr = run_op(args)
    
    if not success:
        console.print(f"[error]{stderr}[/error]")
        return
    
    try:
        items = json.loads(stdout)
        
        console.print("\n[bold cyan]🔑 1Password Items[/bold cyan]\n")
        
        table = Table()
        table.add_column("Title", style="cyan")
        table.add_column("Category")
        table.add_column("Vault")
        
        for item in items[:30]:
            table.add_row(
                item.get("title", ""),
                item.get("category", ""),
                item.get("vault", {}).get("name", "")
            )
        
        console.print(table)
    except:
        console.print(stdout)


@onepassword.command(name="get")
@click.argument("item_name")
@click.option("--field", default="password")
def op_get(item_name, field):
    """Get item field from 1Password."""
    args = ["item", "get", item_name, f"--fields={field}"]
    
    success, stdout, stderr = run_op(args)
    
    if success:
        password = stdout.strip()
        
        try:
            import pyperclip
            pyperclip.copy(password)
            console.print(f"[success]✓ {field} copied to clipboard[/success]")
        except:
            console.print(f"[success]{password}[/success]")
    else:
        console.print(f"[error]{stderr}[/error]")


@onepassword.command(name="vaults")
def op_vaults():
    """List 1Password vaults."""
    success, stdout, stderr = run_op(["vault", "list", "--format=json"])
    
    if not success:
        console.print(f"[error]{stderr}[/error]")
        return
    
    try:
        vaults = json.loads(stdout)
        
        console.print("\n[bold cyan]🗄️  Vaults[/bold cyan]\n")
        
        for vault in vaults:
            console.print(f"• {vault.get('name', '')}")
    except:
        console.print(stdout)


# ==================== BITWARDEN ====================

@pw.group(name="bw")
def bitwarden():
    """Bitwarden commands."""
    pass


@bitwarden.command(name="login")
def bw_login():
    """Login to Bitwarden."""
    console.print("[bold cyan]🔐 Bitwarden Login[/bold cyan]\n")
    subprocess.run(["bw", "login"])


@bitwarden.command(name="unlock")
def bw_unlock():
    """Unlock Bitwarden vault."""
    console.print("[bold cyan]🔓 Unlocking Bitwarden[/bold cyan]\n")
    result = subprocess.run(["bw", "unlock"], capture_output=True, text=True)
    
    # Extract session key
    for line in result.stdout.split("\n"):
        if "BW_SESSION" in line:
            console.print("[muted]Run the export command shown above[/muted]")
            break
    
    console.print(result.stdout)


@bitwarden.command(name="list")
@click.option("--folder", help="Folder name")
def bw_list(folder):
    """List items in Bitwarden."""
    args = ["list", "items"]
    if folder:
        args.extend(["--folderid", folder])
    
    success, stdout, stderr = run_bw(args)
    
    if not success:
        if "locked" in stderr.lower():
            console.print("[error]Vault is locked. Run: djinn pw bw unlock[/error]")
        else:
            console.print(f"[error]{stderr}[/error]")
        return
    
    try:
        items = json.loads(stdout)
        
        console.print("\n[bold cyan]🔑 Bitwarden Items[/bold cyan]\n")
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Username")
        table.add_column("Type")
        
        for item in items[:30]:
            item_type = {1: "Login", 2: "Note", 3: "Card", 4: "Identity"}.get(item.get("type"), "")
            username = item.get("login", {}).get("username", "") if item.get("type") == 1 else ""
            
            table.add_row(item.get("name", ""), username, item_type)
        
        console.print(table)
    except:
        console.print(stdout)


@bitwarden.command(name="get")
@click.argument("item_name")
@click.option("--field", default="password")
def bw_get(item_name, field):
    """Get item from Bitwarden."""
    success, stdout, stderr = run_bw(["get", "item", item_name])
    
    if not success:
        console.print(f"[error]{stderr}[/error]")
        return
    
    try:
        item = json.loads(stdout)
        
        if field == "password" and item.get("login"):
            value = item["login"].get("password", "")
        elif field == "username" and item.get("login"):
            value = item["login"].get("username", "")
        elif field == "totp" and item.get("login"):
            value = item["login"].get("totp", "")
        else:
            value = ""
        
        if value:
            try:
                import pyperclip
                pyperclip.copy(value)
                console.print(f"[success]✓ {field} copied to clipboard[/success]")
            except:
                console.print(f"[success]{value}[/success]")
        else:
            console.print(f"[muted]Field '{field}' not found[/muted]")
    except:
        console.print(f"[error]Could not parse item[/error]")


@bitwarden.command(name="generate")
@click.option("--length", default=20, type=int)
@click.option("--uppercase/--no-uppercase", default=True)
@click.option("--lowercase/--no-lowercase", default=True)
@click.option("--numbers/--no-numbers", default=True)
@click.option("--special/--no-special", default=True)
def bw_generate(length, uppercase, lowercase, numbers, special):
    """Generate secure password."""
    args = ["generate", f"--length={length}"]
    
    if uppercase:
        args.append("--uppercase")
    if lowercase:
        args.append("--lowercase")
    if numbers:
        args.append("--number")
    if special:
        args.append("--special")
    
    success, stdout, stderr = run_bw(args)
    
    if success:
        password = stdout.strip()
        
        try:
            import pyperclip
            pyperclip.copy(password)
            console.print(f"[success]Generated password copied to clipboard[/success]")
        except:
            console.print(f"[success]{password}[/success]")
    else:
        console.print(f"[error]{stderr}[/error]")


@bitwarden.command(name="sync")
def bw_sync():
    """Sync Bitwarden vault."""
    success, stdout, stderr = run_bw(["sync"])
    
    if success:
        console.print("[success]✓ Vault synced[/success]")
    else:
        console.print(f"[error]{stderr}[/error]")


main = pw

if __name__ == "__main__":
    pw()
