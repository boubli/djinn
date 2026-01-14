"""
Slack CLI Plugin for DJINN
Send messages, read channels, manage Slack from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "slack-cli"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Send Slack messages and manage channels."


def get_slack_client():
    """Get Slack client."""
    try:
        from slack_sdk import WebClient
        
        token = os.environ.get("SLACK_BOT_TOKEN")
        if not token:
            config_file = Path.home() / ".djinn" / "slack.json"
            if config_file.exists():
                with open(config_file) as f:
                    token = json.load(f).get("token")
        
        if not token:
            console.print("[error]SLACK_BOT_TOKEN not set[/error]")
            console.print("[muted]Set with: djinn slack auth YOUR_BOT_TOKEN[/muted]")
            return None
        
        return WebClient(token=token)
    except ImportError:
        console.print("[error]slack_sdk not installed. Run: pip install slack_sdk[/error]")
        return None


@click.group()
def slack():
    """Slack commands."""
    pass


@slack.command(name="auth")
@click.argument("token")
def set_auth(token):
    """Save Slack bot token."""
    config_file = Path.home() / ".djinn" / "slack.json"
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump({"token": token}, f)
    
    console.print("[success]✓ Slack token saved![/success]")


@slack.command(name="send")
@click.argument("channel")
@click.argument("message")
@click.option("--thread", help="Thread timestamp for replies")
def send_message(channel, message, thread):
    """Send message to a channel."""
    client = get_slack_client()
    if not client:
        return
    
    try:
        # Ensure channel starts with #
        if not channel.startswith("#") and not channel.startswith("C"):
            channel = f"#{channel}"
        
        params = {
            "channel": channel,
            "text": message
        }
        
        if thread:
            params["thread_ts"] = thread
        
        response = client.chat_postMessage(**params)
        
        console.print(f"[success]✓ Message sent to {channel}[/success]")
        console.print(f"[muted]Timestamp: {response['ts']}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@slack.command(name="channels")
@click.option("--limit", default=20)
def list_channels(limit):
    """List Slack channels."""
    client = get_slack_client()
    if not client:
        return
    
    console.print("\n[bold cyan]📋 Channels[/bold cyan]\n")
    
    try:
        response = client.conversations_list(limit=limit, types="public_channel,private_channel")
        
        table = Table()
        table.add_column("Channel", style="cyan")
        table.add_column("Members")
        table.add_column("ID")
        
        for channel in response["channels"]:
            name = f"#{channel['name']}"
            if channel.get("is_private"):
                name = f"🔒 {name}"
            
            table.add_row(name, str(channel.get("num_members", "-")), channel["id"])
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@slack.command(name="read")
@click.argument("channel")
@click.option("--limit", default=10)
def read_channel(channel, limit):
    """Read recent messages from a channel."""
    client = get_slack_client()
    if not client:
        return
    
    console.print(f"\n[bold cyan]💬 Messages in {channel}[/bold cyan]\n")
    
    try:
        response = client.conversations_history(channel=channel, limit=limit)
        
        for msg in reversed(response["messages"]):
            user = msg.get("user", "bot")
            text = msg.get("text", "")
            
            console.print(f"[bold]{user}[/bold]: {text}")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@slack.command(name="dm")
@click.argument("user_id")
@click.argument("message")
def send_dm(user_id, message):
    """Send direct message to a user."""
    client = get_slack_client()
    if not client:
        return
    
    try:
        # Open DM channel
        response = client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]
        
        # Send message
        client.chat_postMessage(channel=channel_id, text=message)
        
        console.print(f"[success]✓ DM sent to {user_id}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@slack.command(name="users")
@click.option("--limit", default=50)
def list_users(limit):
    """List workspace users."""
    client = get_slack_client()
    if not client:
        return
    
    console.print("\n[bold cyan]👥 Users[/bold cyan]\n")
    
    try:
        response = client.users_list(limit=limit)
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Display Name")
        table.add_column("ID")
        
        for user in response["members"]:
            if not user.get("deleted") and not user.get("is_bot"):
                table.add_row(
                    user.get("name", ""),
                    user.get("profile", {}).get("display_name", ""),
                    user["id"]
                )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@slack.command(name="status")
@click.argument("text")
@click.option("--emoji", default=":speech_balloon:")
def set_status(text, emoji):
    """Set your Slack status."""
    client = get_slack_client()
    if not client:
        return
    
    try:
        client.users_profile_set(
            profile={
                "status_text": text,
                "status_emoji": emoji
            }
        )
        
        console.print(f"[success]✓ Status set: {emoji} {text}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = slack

if __name__ == "__main__":
    slack()
