"""
Screenshot Plugin for DJINN
Capture screenshots and screen recordings.
"""
import click
from rich.console import Console
from pathlib import Path
from datetime import datetime
import time

console = Console()

PLUGIN_NAME = "screenshot"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Capture screenshots and screen recordings."


def get_output_path(prefix="screenshot", ext="png"):
    """Generate output filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path.home() / "Pictures" / f"{prefix}_{timestamp}.{ext}"


@click.group()
def capture():
    """Screenshot and recording commands."""
    pass


@capture.command(name="screen")
@click.option("--output", "-o", help="Output file path")
@click.option("--delay", default=0, type=int, help="Delay in seconds")
@click.option("--region", is_flag=True, help="Select region")
@click.option("--clipboard", "-c", is_flag=True, help="Copy to clipboard")
def take_screenshot(output, delay, region, clipboard):
    """Take a screenshot."""
    try:
        from PIL import ImageGrab
        import pyautogui
    except ImportError:
        console.print("[error]Required packages not installed.[/error]")
        console.print("[muted]Run: pip install pillow pyautogui[/muted]")
        return
    
    if delay > 0:
        console.print(f"[muted]Capturing in {delay} seconds...[/muted]")
        time.sleep(delay)
    
    try:
        if region:
            console.print("[muted]Click and drag to select region...[/muted]")
            # Simple region capture using pyautogui
            screenshot = pyautogui.screenshot()
        else:
            screenshot = ImageGrab.grab()
        
        output_path = Path(output) if output else get_output_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        screenshot.save(str(output_path))
        
        console.print(f"[success]✓ Screenshot saved: {output_path}[/success]")
        
        if clipboard:
            try:
                import io
                import win32clipboard
                from PIL import Image
                
                output_buffer = io.BytesIO()
                screenshot.convert("RGB").save(output_buffer, "BMP")
                data = output_buffer.getvalue()[14:]  # Remove BMP header
                
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                
                console.print("[success]✓ Copied to clipboard[/success]")
            except:
                console.print("[muted]Could not copy to clipboard[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@capture.command(name="window")
@click.argument("window_title", required=False)
@click.option("--output", "-o", help="Output file path")
def capture_window(window_title, output):
    """Capture a specific window."""
    try:
        import pyautogui
        import pygetwindow as gw
    except ImportError:
        console.print("[error]Required packages not installed.[/error]")
        console.print("[muted]Run: pip install pyautogui pygetwindow[/muted]")
        return
    
    try:
        if window_title:
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                console.print(f"[error]Window '{window_title}' not found[/error]")
                return
            
            window = windows[0]
            window.activate()
            time.sleep(0.5)
            
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        else:
            # List windows
            console.print("\n[bold cyan]📋 Open Windows[/bold cyan]\n")
            
            for win in gw.getAllWindows():
                if win.title:
                    console.print(f"• {win.title}")
            
            console.print("\n[muted]Use: djinn capture window \"Window Title\"[/muted]")
            return
        
        output_path = Path(output) if output else get_output_path("window")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        screenshot.save(str(output_path))
        
        console.print(f"[success]✓ Window captured: {output_path}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@capture.command(name="record")
@click.option("--output", "-o", help="Output file path")
@click.option("--duration", "-d", type=int, help="Duration in seconds")
@click.option("--fps", default=15, type=int, help="Frames per second")
def record_screen(output, duration, fps):
    """Record screen video."""
    try:
        import cv2
        import numpy as np
        from PIL import ImageGrab
    except ImportError:
        console.print("[error]Required packages not installed.[/error]")
        console.print("[muted]Run: pip install opencv-python numpy pillow[/muted]")
        return
    
    output_path = Path(output) if output else get_output_path("recording", "mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get screen size
    screen = ImageGrab.grab()
    width, height = screen.size
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    console.print(f"[bold cyan]🎥 Recording started[/bold cyan]")
    console.print(f"[muted]Resolution: {width}x{height} @ {fps}fps[/muted]")
    
    if duration:
        console.print(f"[muted]Duration: {duration} seconds[/muted]")
    else:
        console.print("[muted]Press Ctrl+C to stop[/muted]")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # Capture frame
            img = ImageGrab.grab()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            out.write(frame)
            frame_count += 1
            
            # Check duration
            elapsed = time.time() - start_time
            if duration and elapsed >= duration:
                break
            
            # Control frame rate
            time.sleep(1.0 / fps)
    except KeyboardInterrupt:
        pass
    finally:
        out.release()
        elapsed = time.time() - start_time
        
        console.print(f"\n[success]✓ Recording saved: {output_path}[/success]")
        console.print(f"[muted]Duration: {elapsed:.1f}s, Frames: {frame_count}[/muted]")


@capture.command(name="gif")
@click.option("--output", "-o", help="Output file path")
@click.option("--duration", "-d", default=5, type=int, help="Duration in seconds")
@click.option("--fps", default=10, type=int, help="Frames per second")
def record_gif(output, duration, fps):
    """Record screen as GIF."""
    try:
        from PIL import ImageGrab, Image
    except ImportError:
        console.print("[error]pillow not installed. Run: pip install pillow[/error]")
        return
    
    output_path = Path(output) if output else get_output_path("recording", "gif")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[bold cyan]🎬 Recording GIF ({duration}s)...[/bold cyan]")
    
    frames = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            frame = ImageGrab.grab()
            # Resize for smaller file size
            frame = frame.resize((frame.width // 2, frame.height // 2), Image.Resampling.LANCZOS)
            frames.append(frame)
            
            time.sleep(1.0 / fps)
    except KeyboardInterrupt:
        pass
    
    if frames:
        console.print(f"[muted]Saving {len(frames)} frames...[/muted]")
        
        frames[0].save(
            str(output_path),
            save_all=True,
            append_images=frames[1:],
            duration=int(1000 / fps),
            loop=0
        )
        
        console.print(f"[success]✓ GIF saved: {output_path}[/success]")
    else:
        console.print("[error]No frames captured[/error]")


@capture.command(name="ocr")
@click.argument("image_path", required=False)
@click.option("--clipboard", "-c", is_flag=True, help="Copy text to clipboard")
def extract_text(image_path, clipboard):
    """Extract text from screenshot using OCR."""
    try:
        import pytesseract
        from PIL import Image, ImageGrab
    except ImportError:
        console.print("[error]Required packages not installed.[/error]")
        console.print("[muted]Run: pip install pytesseract pillow[/muted]")
        console.print("[muted]Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract[/muted]")
        return
    
    try:
        if image_path:
            img = Image.open(image_path)
        else:
            console.print("[muted]Capturing screen...[/muted]")
            img = ImageGrab.grab()
        
        text = pytesseract.image_to_string(img)
        
        if text.strip():
            console.print("\n[bold cyan]📝 Extracted Text[/bold cyan]\n")
            console.print(text)
            
            if clipboard:
                try:
                    import pyperclip
                    pyperclip.copy(text)
                    console.print("\n[success]✓ Copied to clipboard[/success]")
                except:
                    pass
        else:
            console.print("[muted]No text found in image[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = capture

if __name__ == "__main__":
    capture()
