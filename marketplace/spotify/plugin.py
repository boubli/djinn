"""
Spotify Plugin for DJINN
Control Spotify from terminal.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
from pathlib import Path
import webbrowser

console = Console()

PLUGIN_NAME = "spotify"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Control Spotify playback from terminal."

CONFIG_FILE = Path.home() / ".djinn" / "spotify.json"


def get_spotify_client():
    """Get Spotify client."""
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
                    client_id = config.get("client_id")
                    client_secret = config.get("client_secret")
        
        if not client_id or not client_secret:
            console.print("[error]Spotify credentials not set[/error]")
            console.print("[muted]Run: djinn spotify auth CLIENT_ID CLIENT_SECRET[/muted]")
            return None
        
        scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing,playlist-read-private"
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8888/callback",
            scope=scope,
            cache_path=str(Path.home() / ".djinn" / ".spotify_cache")
        ))
        
        return sp
    except ImportError:
        console.print("[error]spotipy not installed. Run: pip install spotipy[/error]")
        return None


@click.group()
def spotify():
    """Spotify commands."""
    pass


@spotify.command(name="auth")
@click.argument("client_id")
@click.argument("client_secret")
def set_auth(client_id, client_secret):
    """Save Spotify credentials."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            "client_id": client_id,
            "client_secret": client_secret
        }, f)
    
    console.print("[success]✓ Spotify credentials saved![/success]")
    console.print("[muted]On first use, you'll be redirected to login.[/muted]")


@spotify.command(name="now")
def now_playing():
    """Show currently playing track."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        current = sp.current_playback()
        
        if not current or not current.get("is_playing"):
            console.print("[muted]Nothing playing[/muted]")
            return
        
        track = current["item"]
        
        console.print("\n[bold cyan]🎵 Now Playing[/bold cyan]\n")
        console.print(f"[bold]{track['name']}[/bold]")
        console.print(f"by {', '.join(a['name'] for a in track['artists'])}")
        console.print(f"on {track['album']['name']}")
        
        # Progress bar
        progress = current["progress_ms"]
        duration = track["duration_ms"]
        percent = int((progress / duration) * 30)
        bar = "█" * percent + "░" * (30 - percent)
        
        progress_min = progress // 60000
        progress_sec = (progress % 60000) // 1000
        duration_min = duration // 60000
        duration_sec = (duration % 60000) // 1000
        
        console.print(f"\n[muted]{bar} {progress_min}:{progress_sec:02d}/{duration_min}:{duration_sec:02d}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="play")
@click.argument("query", nargs=-1, required=False)
def play(query):
    """Play/resume or search and play."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        if query:
            # Search and play
            search_query = " ".join(query)
            results = sp.search(q=search_query, type="track", limit=1)
            
            if results["tracks"]["items"]:
                track = results["tracks"]["items"][0]
                sp.start_playback(uris=[track["uri"]])
                console.print(f"[success]▶ Playing: {track['name']} by {track['artists'][0]['name']}[/success]")
            else:
                console.print("[muted]No tracks found[/muted]")
        else:
            # Resume playback
            sp.start_playback()
            console.print("[success]▶ Resumed playback[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="pause")
def pause():
    """Pause playback."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        sp.pause_playback()
        console.print("[success]⏸ Paused[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="next")
def next_track():
    """Skip to next track."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        sp.next_track()
        console.print("[success]⏭ Skipped to next track[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="prev")
def previous_track():
    """Go to previous track."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        sp.previous_track()
        console.print("[success]⏮ Previous track[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="vol")
@click.argument("level", type=int)
def volume(level):
    """Set volume (0-100)."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        level = max(0, min(100, level))
        sp.volume(level)
        console.print(f"[success]🔊 Volume: {level}%[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="shuffle")
@click.argument("state", type=click.Choice(["on", "off"]))
def shuffle(state):
    """Toggle shuffle."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        sp.shuffle(state == "on")
        console.print(f"[success]🔀 Shuffle: {state}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="playlists")
@click.option("--limit", default=20)
def list_playlists(limit):
    """List your playlists."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        playlists = sp.current_user_playlists(limit=limit)
        
        console.print("\n[bold cyan]📋 Your Playlists[/bold cyan]\n")
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Tracks")
        table.add_column("URI")
        
        for playlist in playlists["items"]:
            table.add_row(
                playlist["name"],
                str(playlist["tracks"]["total"]),
                playlist["uri"]
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="devices")
def list_devices():
    """List available devices."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        devices = sp.devices()
        
        console.print("\n[bold cyan]🔌 Devices[/bold cyan]\n")
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("Active")
        table.add_column("ID")
        
        for device in devices["devices"]:
            active = "▶" if device["is_active"] else ""
            table.add_row(
                device["name"],
                device["type"],
                active,
                device["id"][:12] + "..."
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@spotify.command(name="transfer")
@click.argument("device_id")
def transfer_playback(device_id):
    """Transfer playback to a device."""
    sp = get_spotify_client()
    if not sp:
        return
    
    try:
        sp.transfer_playback(device_id)
        console.print(f"[success]✓ Playback transferred[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = spotify

if __name__ == "__main__":
    spotify()
