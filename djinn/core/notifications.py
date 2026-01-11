"""
Notifications - Desktop notifications for DJINN.
"""
import subprocess
import sys
from typing import Optional


class NotificationManager:
    """Manages desktop notifications."""
    
    @staticmethod
    def notify(title: str, message: str, sound: bool = False) -> bool:
        """Send a desktop notification."""
        try:
            if sys.platform == "win32":
                return NotificationManager._notify_windows(title, message, sound)
            elif sys.platform == "darwin":
                return NotificationManager._notify_macos(title, message, sound)
            else:
                return NotificationManager._notify_linux(title, message, sound)
        except:
            return False
    
    @staticmethod
    def _notify_windows(title: str, message: str, sound: bool = False) -> bool:
        """Windows notification using PowerShell."""
        try:
            # Use PowerShell toast notification
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("DJINN").Show($toast)
            '''
            
            # Simpler fallback using msg command or BurntToast if available
            try:
                # Try simpler PowerShell approach
                simple_script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $balloon = New-Object System.Windows.Forms.NotifyIcon
                $balloon.Icon = [System.Drawing.SystemIcons]::Information
                $balloon.BalloonTipTitle = "{title}"
                $balloon.BalloonTipText = "{message}"
                $balloon.Visible = $true
                $balloon.ShowBalloonTip(5000)
                '''
                subprocess.run(
                    ["powershell", "-Command", simple_script],
                    capture_output=True,
                    timeout=5
                )
                return True
            except:
                pass
            
            if sound:
                NotificationManager.beep()
            
            return True
        except:
            return False
    
    @staticmethod
    def _notify_macos(title: str, message: str, sound: bool = False) -> bool:
        """macOS notification using osascript."""
        try:
            sound_str = 'sound name "Glass"' if sound else ""
            script = f'display notification "{message}" with title "{title}" {sound_str}'
            subprocess.run(["osascript", "-e", script], capture_output=True)
            return True
        except:
            return False
    
    @staticmethod
    def _notify_linux(title: str, message: str, sound: bool = False) -> bool:
        """Linux notification using notify-send."""
        try:
            subprocess.run(["notify-send", title, message], capture_output=True)
            if sound:
                NotificationManager.beep()
            return True
        except:
            return False
    
    @staticmethod
    def beep():
        """Play a simple beep sound."""
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(800, 200)  # 800Hz for 200ms
            else:
                # Try to play a beep using printf
                print("\a", end="", flush=True)
        except:
            pass
    
    @staticmethod
    def success_sound():
        """Play a success sound."""
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(523, 100)  # C5
                winsound.Beep(659, 100)  # E5
                winsound.Beep(784, 150)  # G5
        except:
            NotificationManager.beep()
    
    @staticmethod
    def error_sound():
        """Play an error sound."""
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(300, 300)
        except:
            NotificationManager.beep()
