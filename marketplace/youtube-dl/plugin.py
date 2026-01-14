"""
YouTube Downloader Plugin for DJINN
Download videos from YouTube.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from pathlib import Path

console = Console()

PLUGIN_NAME = "youtube-dl"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Download videos from YouTube and other sites."


def get_yt_dlp():
    """Get yt-dlp module."""
    try:
        import yt_dlp
        return yt_dlp
    except ImportError:
        console.print("[error]yt-dlp not installed. Run: pip install yt-dlp[/error]")
        return None


@click.group()
def ytdl():
    """YouTube download commands."""
    pass


@ytdl.command(name="download")
@click.argument("url")
@click.option("--output", "-o", help="Output directory")
@click.option("--format", "-f", "fmt", default="best", help="Video format")
@click.option("--audio", "-a", is_flag=True, help="Audio only")
@click.option("--playlist", "-p", is_flag=True, help="Download entire playlist")
def download_video(url, output, fmt, audio, playlist):
    """Download video from URL."""
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        return
    
    output_dir = Path(output) if output else Path.home() / "Videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    options = {
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "format": fmt,
        "noplaylist": not playlist,
        "progress_hooks": [_progress_hook],
    }
    
    if audio:
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
        options["outtmpl"] = str(output_dir / "%(title)s.%(ext)s")
    
    console.print(f"\n[bold cyan]📥 Downloading...[/bold cyan]\n")
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        
        console.print(f"\n[success]✓ Download complete![/success]")
        console.print(f"[muted]Saved to: {output_dir}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


def _progress_hook(d):
    """Progress callback."""
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%")
        speed = d.get("_speed_str", "0 B/s")
        eta = d.get("_eta_str", "?")
        print(f"\r{percent} | {speed} | ETA: {eta}", end="", flush=True)
    elif d["status"] == "finished":
        print("\n[Processing...]", end="", flush=True)


@ytdl.command(name="info")
@click.argument("url")
def video_info(url):
    """Get video information."""
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        return
    
    options = {
        "quiet": True,
        "no_warnings": True
    }
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        
        console.print(f"\n[bold cyan]📹 {info.get('title', 'Unknown')}[/bold cyan]\n")
        
        console.print(f"[muted]Channel:[/muted] {info.get('uploader', '-')}")
        console.print(f"[muted]Duration:[/muted] {_format_duration(info.get('duration', 0))}")
        console.print(f"[muted]Views:[/muted] {info.get('view_count', 0):,}")
        console.print(f"[muted]Likes:[/muted] {info.get('like_count', 0):,}")
        console.print(f"[muted]Upload Date:[/muted] {info.get('upload_date', '-')}")
        
        if info.get("description"):
            console.print(f"\n[bold]Description:[/bold]")
            console.print(info["description"][:300] + "...")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ytdl.command(name="formats")
@click.argument("url")
def list_formats(url):
    """List available formats."""
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        return
    
    options = {
        "quiet": True,
        "no_warnings": True
    }
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        
        console.print(f"\n[bold cyan]📋 Available Formats[/bold cyan]\n")
        
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Ext")
        table.add_column("Resolution")
        table.add_column("Size")
        table.add_column("Note")
        
        for fmt in info.get("formats", [])[-20:]:
            resolution = fmt.get("resolution", "-")
            if resolution == "audio only":
                resolution = "🔊 audio"
            
            size = fmt.get("filesize") or fmt.get("filesize_approx", 0)
            size_str = f"{size / (1024**2):.1f} MB" if size else "-"
            
            table.add_row(
                fmt.get("format_id", "-"),
                fmt.get("ext", "-"),
                resolution,
                size_str,
                fmt.get("format_note", "-")[:20]
            )
        
        console.print(table)
        console.print("\n[muted]Use: djinn ytdl download URL -f FORMAT_ID[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ytdl.command(name="playlist")
@click.argument("url")
def playlist_info(url):
    """List playlist videos."""
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        return
    
    options = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True
    }
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        
        console.print(f"\n[bold cyan]📋 {info.get('title', 'Playlist')}[/bold cyan]\n")
        
        entries = info.get("entries", [])
        
        table = Table()
        table.add_column("#")
        table.add_column("Title")
        table.add_column("Duration")
        
        for i, entry in enumerate(entries[:30], 1):
            duration = _format_duration(entry.get("duration", 0))
            table.add_row(str(i), entry.get("title", "-")[:50], duration)
        
        console.print(table)
        
        if len(entries) > 30:
            console.print(f"\n[muted]... and {len(entries) - 30} more[/muted]")
        
        console.print(f"\n[muted]Total: {len(entries)} videos[/muted]")
        console.print("[muted]Use: djinn ytdl download URL --playlist[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ytdl.command(name="thumbnail")
@click.argument("url")
@click.option("--output", "-o", help="Output path")
def download_thumbnail(url, output):
    """Download video thumbnail."""
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        return
    
    try:
        import requests
        
        options = {"quiet": True}
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        
        thumbnail_url = info.get("thumbnail")
        if not thumbnail_url:
            console.print("[error]No thumbnail found[/error]")
            return
        
        # Download thumbnail
        resp = requests.get(thumbnail_url)
        
        output_path = Path(output) if output else Path.home() / "Pictures" / f"{info['id']}_thumbnail.jpg"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        
        console.print(f"[success]✓ Thumbnail saved: {output_path}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ytdl.command(name="subtitles")
@click.argument("url")
@click.option("--lang", default="en", help="Language code")
@click.option("--output", "-o", help="Output directory")
def download_subtitles(url, lang, output):
    """Download video subtitles."""
    yt_dlp = get_yt_dlp()
    if not yt_dlp:
        return
    
    output_dir = Path(output) if output else Path.cwd()
    
    options = {
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "writesubtitles": True,
        "subtitleslangs": [lang],
        "skip_download": True
    }
    
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        
        console.print(f"[success]✓ Subtitles downloaded ({lang})[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


def _format_duration(seconds):
    """Format seconds to HH:MM:SS."""
    if not seconds:
        return "-"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


main = ytdl

if __name__ == "__main__":
    ytdl()
