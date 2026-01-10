"""
Security and Networking Plugins - firewall, ssl, network diagnostics.
"""
from typing import Optional


class FirewallPlugin:
    """Firewall (iptables/ufw) command generator."""
    
    SYSTEM_PROMPT = """You are a firewall expert. Generate iptables or ufw commands.

Rules:
- Output ONLY the firewall command
- Use ufw for simplicity when possible
- Be security-conscious

Examples:
- "allow ssh" -> ufw allow ssh
- "block ip" -> ufw deny from 1.2.3.4
- "allow port 80" -> ufw allow 80/tcp
- "show rules" -> ufw status verbose"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class SSLPlugin:
    """SSL/TLS certificate command generator."""
    
    SYSTEM_PROMPT = """You are an SSL/TLS expert. Generate openssl or certbot commands.

Rules:
- Output ONLY the ssl command
- Use proper syntax

Examples:
- "generate self-signed" -> openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
- "get letsencrypt" -> certbot --nginx -d example.com
- "check cert expiry" -> openssl s_client -connect example.com:443 | openssl x509 -noout -dates
- "generate csr" -> openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class NetworkPlugin:
    """Network diagnostics command generator."""
    
    SYSTEM_PROMPT = """You are a network diagnostics expert. Generate network troubleshooting commands.

Rules:
- Output ONLY the network command
- Use common tools: ping, traceroute, netstat, ss, dig, nslookup, curl, wget

Examples:
- "check port open" -> netstat -tuln | grep :80
- "trace route" -> traceroute google.com
- "check dns" -> dig example.com
- "test http" -> curl -I https://example.com
- "list connections" -> ss -tuln"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ProcessPlugin:
    """Process management command generator."""
    
    SYSTEM_PROMPT = """You are a process management expert. Generate process commands.

Rules:
- Output ONLY the process command
- Use ps, top, htop, kill, pkill, pgrep

Examples:
- "find process by name" -> pgrep -a nginx
- "kill by pid" -> kill -9 1234
- "list all processes" -> ps aux
- "cpu usage" -> top -bn1 | head -20
- "kill all node" -> pkill -f node"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class DiskPlugin:
    """Disk management command generator."""
    
    SYSTEM_PROMPT = """You are a disk management expert. Generate disk commands.

Rules:
- Output ONLY the disk command
- Use df, du, fdisk, mount, lsblk

Examples:
- "check disk space" -> df -h
- "folder size" -> du -sh /path
- "find large files" -> find / -type f -size +100M 2>/dev/null
- "list partitions" -> lsblk
- "mount drive" -> mount /dev/sdb1 /mnt/disk"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class UserPlugin:
    """User management command generator."""
    
    SYSTEM_PROMPT = """You are a Linux user management expert. Generate user commands.

Rules:
- Output ONLY the user command
- Use useradd, usermod, passwd, groups, chown, chmod

Examples:
- "create user" -> sudo useradd -m -s /bin/bash username
- "add to sudo" -> sudo usermod -aG sudo username
- "change password" -> sudo passwd username
- "list groups" -> groups username"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
