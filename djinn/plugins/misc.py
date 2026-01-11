"""
Miscellaneous Power Tools - Various utility commands.
"""


class TmuxPlugin:
    """Tmux terminal multiplexer commands."""
    
    TEMPLATES = {
        "new_session": "tmux new -s {name}",
        "attach": "tmux attach -t {name}",
        "list_sessions": "tmux ls",
        "kill_session": "tmux kill-session -t {name}",
        "new_window": "tmux new-window -n {name}",
        "split_h": "tmux split-window -h",
        "split_v": "tmux split-window -v",
        "detach": "tmux detach",
    }


class ScreenPlugin:
    """GNU Screen commands."""
    
    TEMPLATES = {
        "new": "screen -S {name}",
        "attach": "screen -r {name}",
        "list": "screen -ls",
        "detach": "screen -d",
        "kill": "screen -X -S {name} quit",
    }


class MediaPlugin:
    """Media processing commands."""
    
    TEMPLATES = {
        # FFmpeg
        "ffmpeg_convert": "ffmpeg -i {input} {output}",
        "ffmpeg_compress": "ffmpeg -i {input} -vcodec libx265 -crf 28 {output}",
        "ffmpeg_extract_audio": "ffmpeg -i {input} -vn -acodec copy {output}",
        "ffmpeg_gif": "ffmpeg -i {input} -vf 'fps=10,scale=320:-1' {output}.gif",
        "ffmpeg_resize": "ffmpeg -i {input} -vf scale={width}:{height} {output}",
        "ffmpeg_trim": "ffmpeg -i {input} -ss {start} -t {duration} -c copy {output}",
        "ffmpeg_concat": "ffmpeg -f concat -i filelist.txt -c copy {output}",
        "ffmpeg_thumbnail": "ffmpeg -i {input} -ss {time} -vframes 1 {output}.jpg",
        
        # ImageMagick
        "convert": "convert {input} {output}",
        "resize": "convert {input} -resize {size} {output}",
        "crop": "convert {input} -crop {geometry} {output}",
        "rotate": "convert {input} -rotate {degrees} {output}",
        "compress_jpg": "convert {input} -quality {quality} {output}",
        "strip_metadata": "convert {input} -strip {output}",
        "pdf_to_png": "convert -density 300 {input}.pdf {output}.png",
        "montage": "montage *.jpg -geometry +2+2 {output}",
    }


class YouTubePlugin:
    """YouTube download commands."""
    
    TEMPLATES = {
        "download": "yt-dlp {url}",
        "download_audio": "yt-dlp -x --audio-format mp3 {url}",
        "download_best": "yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' {url}",
        "download_720p": "yt-dlp -f 'bestvideo[height<=720]+bestaudio/best[height<=720]' {url}",
        "download_playlist": "yt-dlp -o '%(playlist_index)s-%(title)s.%(ext)s' {url}",
        "list_formats": "yt-dlp -F {url}",
        "subtitles": "yt-dlp --write-subs --sub-lang en {url}",
    }


class PDFPlugin:
    """PDF manipulation commands."""
    
    TEMPLATES = {
        "merge": "pdfunite {files} {output}",
        "split": "pdfseparate {input} {output}_%d.pdf",
        "extract_pages": "pdftk {input} cat {pages} output {output}",
        "compress": "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile={output} {input}",
        "to_text": "pdftotext {input} {output}",
        "to_html": "pdftohtml {input} {output}",
        "info": "pdfinfo {input}",
        "rotate": "pdftk {input} cat 1-endeast output {output}",
    }


class DateTimePlugin:
    """Date and time commands."""
    
    TEMPLATES = {
        "now": "date",
        "utc": "date -u",
        "iso": "date -Iseconds",
        "epoch": "date +%s",
        "from_epoch": "date -d @{timestamp}",
        "format": "date '+{format}'",
        "calendar": "cal",
        "calendar_year": "cal {year}",
        "timezone": "timedatectl",
        "set_timezone": "timedatectl set-timezone {timezone}",
    }


class CalculatorPlugin:
    """Calculator commands."""
    
    TEMPLATES = {
        "bc": "echo '{expression}' | bc -l",
        "python_calc": "python3 -c 'print({expression})'",
        "expr": "expr {expression}",
        "dc": "echo '{expression}' | dc",
    }


class RandomPlugin:
    """Random generation commands."""
    
    TEMPLATES = {
        "uuid": "uuidgen",
        "random_hex": "openssl rand -hex {bytes}",
        "random_base64": "openssl rand -base64 {bytes}",
        "random_string": "cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w {length} | head -n 1",
        "random_number": "shuf -i {min}-{max} -n 1",
        "random_mac": "openssl rand -hex 6 | sed 's/\\(..\\)/\\1:/g; s/:$//'",
    }


class WatchPlugin:
    """Watch command variants."""
    
    TEMPLATES = {
        "watch": "watch -n {seconds} '{command}'",
        "watch_diff": "watch -d '{command}'",
        "watch_color": "watch --color '{command}'",
        "viddy": "viddy '{command}'",
    }


class ClipboardPlugin:
    """Clipboard commands."""
    
    TEMPLATES = {
        "copy_linux": "xclip -selection clipboard",
        "paste_linux": "xclip -selection clipboard -o",
        "copy_macos": "pbcopy",
        "paste_macos": "pbpaste",
        "copy_wayland": "wl-copy",
        "paste_wayland": "wl-paste",
    }


class QRPlugin:
    """QR code commands."""
    
    TEMPLATES = {
        "generate": "qrencode -o {output}.png '{text}'",
        "generate_terminal": "qrencode -t ansiutf8 '{text}'",
        "scan": "zbarimg {image}",
    }


class SpeedPlugin:
    """Speed testing commands."""
    
    TEMPLATES = {
        "speedtest": "speedtest-cli",
        "speedtest_json": "speedtest-cli --json",
        "fast": "fast",
    }


class WeatherPlugin:
    """Weather commands."""
    
    TEMPLATES = {
        "weather": "curl wttr.in/{city}",
        "weather_short": "curl 'wttr.in/{city}?format=3'",
        "weather_moon": "curl wttr.in/Moon",
    }


class ASCIIPlugin:
    """ASCII art commands."""
    
    TEMPLATES = {
        "figlet": "figlet '{text}'",
        "toilet": "toilet '{text}'",
        "cowsay": "cowsay '{text}'",
        "fortune": "fortune",
        "lolcat": "echo '{text}' | lolcat",
        "neofetch": "neofetch",
        "screenfetch": "screenfetch",
        "fastfetch": "fastfetch",
    }
