"""
Data & File Management Tools for DJINN v2.2.0
"""
import hashlib
import shutil
from pathlib import Path
from typing import List, Dict
import subprocess


class TeleportManager:
    """Save and jump between directories."""
    
    def __init__(self):
        self.teleport_file = Path.home() / ".djinn" / "teleport.txt"
        self.teleport_file.parent.mkdir(exist_ok=True)
    
    def save_location(self):
        """Save current directory."""
        with open(self.teleport_file, 'w') as f:
            f.write(str(Path.cwd()))
    
    def get_location(self) -> str:
        """Get saved location."""
        if not self.teleport_file.exists():
            return None
        
        with open(self.teleport_file) as f:
            return f.read().strip()


class SmartCopy:
    """Enhanced copy with progress and rsync backend."""
    
    @staticmethod
    def copy_with_progress(src: str, dst: str):
        """Copy with progress bar."""
        from tqdm import tqdm
        
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.is_file():
            # Single file
            size = src_path.stat().st_size
            with tqdm(total=size, unit='B', unit_scale=True) as pbar:
                with open(src_path, 'rb') as fsrc:
                    with open(dst_path, 'wb') as fdst:
                        while True:
                            chunk = fsrc.read(1024*1024)  # 1MB chunks
                            if not chunk:
                                break
                            fdst.write(chunk)
                            pbar.update(len(chunk))
        else:
            # Directory - use rsync if available
            try:
                subprocess.run([
                    'rsync', '-av', '--progress',
                    str(src_path) + '/',
                    str(dst_path) + '/'
                ])
            except FileNotFoundError:
                # Fallback to shutil
                shutil.copytree(src_path, dst_path)


class DuplicateFinder:
    """Find duplicate files by hash."""
    
    @staticmethod
    def find_duplicates(directory: str) -> Dict[str, List[str]]:
        """Find duplicate files in directory."""
        hashes = {}
        
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file():
                try:
                    file_hash = DuplicateFinder._hash_file(file_path)
                    if file_hash in hashes:
                        hashes[file_hash].append(str(file_path))
                    else:
                        hashes[file_hash] = [str(file_path)]
                except:
                    pass
        
        # Return only duplicates
        return {h: files for h, files in hashes.items() if len(files) > 1}
    
    @staticmethod
    def _hash_file(file_path: Path) -> str:
        """Calculate MD5 hash of file."""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()


class DiskUsageVisualizer:
    """Visualize disk usage (like ncdu)."""
    
    @staticmethod
    def analyze_directory(directory: str, max_depth: int = 3) -> Dict:
        """Analyze disk usage."""
        path = Path(directory)
        
        if not path.exists():
            return {}
        
        result = {
            "path": str(path),
            "size": 0,
            "children": []
        }
        
        if path.is_file():
            result["size"] = path.stat().st_size
            return result
        
        total_size = 0
        for item in path.iterdir():
            try:
                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    result["children"].append({
                        "path": str(item),
                        "size": size,
                        "type": "file"
                    })
                elif item.is_dir() and max_depth > 0:
                    child_result = DiskUsageVisualizer.analyze_directory(
                        str(item), max_depth - 1
                    )
                    total_size += child_result["size"]
                    result["children"].append(child_result)
            except (PermissionError, OSError):
                pass
        
        result["size"] = total_size
        # Sort children by size
        result["children"].sort(key=lambda x: x["size"], reverse=True)
        
        return result


class MediaConverter:
    """Convert images and videos."""
    
    @staticmethod
    def convert_image(input_path: str, output_path: str):
        """Convert image format."""
        from PIL import Image
        
        img = Image.open(input_path)
        img.save(output_path)
    
    @staticmethod
    def trim_video(input_path: str, output_path: str, start: str, duration: str):
        """Trim video using ffmpeg."""
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-ss', start,
            '-t', duration,
            '-c', 'copy',
            output_path
        ])


class FileEncryptor:
    """Encrypt/decrypt files with AES."""
    
    @staticmethod
    def encrypt_file(file_path: str, password: str):
        """Encrypt file."""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        import base64
        
        # Derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'djinn_salt',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        
        # Read and encrypt
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = fernet.encrypt(data)
        
        # Save encrypted file
        with open(file_path + '.encrypted', 'wb') as f:
            f.write(encrypted)
    
    @staticmethod
    def decrypt_file(file_path: str, password: str, output_path: str):
        """Decrypt file."""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        import base64
        
        # Derive key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'djinn_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        
        # Read and decrypt
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted = fernet.decrypt(encrypted_data)
        
        # Save decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted)


class QRCodeGenerator:
    """Generate QR codes."""
    
    @staticmethod
    def generate_qr(data: str, output_file: str = None) -> str:
        """Generate QR code."""
        import qrcode
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        if output_file:
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_file)
            return f"QR code saved to {output_file}"
       else:
            # ASCII QR code for terminal
            qr.print_ascii()
            return "QR code printed to terminal"


class SecretsVault:
    """Encrypted key-value store for secrets."""
    
    def __init__(self, master_password: str):
        self.vault_file = Path.home() / ".djinn" / "vault.enc"
        self.vault_file.parent.mkdir(exist_ok=True)
        self.master_password = master_password
        self.secrets = self._load()
    
    def _load(self) -> Dict:
        """Load and decrypt vault."""
        if not self.vault_file.exists():
            return {}
        
        try:
            FileEncryptor.decrypt_file(
                str(self.vault_file),
                self.master_password,
                str(self.vault_file) + '.tmp'
            )
            
            with open(str(self.vault_file) + '.tmp') as f:
                import json
                data = json.load(f)
            
            Path(str(self.vault_file) + '.tmp').unlink()
            return data
        except:
            return {}
    
    def save(self):
        """Encrypt and save vault."""
        import json
        
        # Save as temporary JSON
        tmp_file = str(self.vault_file) + '.tmp'
        with open(tmp_file, 'w') as f:
            json.dump(self.secrets, f)
        
        # Encrypt
        FileEncryptor.encrypt_file(tmp_file, self.master_password)
        
        # Move encrypted file
        Path(tmp_file + '.encrypted').rename(self.vault_file)
        Path(tmp_file).unlink()
    
    def set(self, key: str, value: str):
        """Store a secret."""
        self.secrets[key] = value
        self.save()
    
    def get(self, key: str) -> str:
        """Retrieve a secret."""
        return self.secrets.get(key)
    
    def list_keys(self) -> List[str]:
        """List all secret keys."""
        return list(self.secrets.keys())
