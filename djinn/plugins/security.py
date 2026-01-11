"""
Security Plugins - Security-focused command generators.
"""


class SecretsScanner:
    """Scan for leaked secrets in code."""
    
    SYSTEM_PROMPT = """You are a security expert. Generate commands to scan for leaked secrets.
Output only the command, no explanations."""
    
    PATTERNS = [
        "API_KEY", "SECRET_KEY", "PASSWORD", "TOKEN", "PRIVATE_KEY",
        "AWS_ACCESS_KEY", "AWS_SECRET", "GITHUB_TOKEN", "DATABASE_URL"
    ]


class HardeningPlugin:
    """System hardening suggestions."""
    
    SYSTEM_PROMPT = """You are a security hardening expert. Generate commands to improve security.
Focus on practical, actionable commands. Output only commands."""


class EncryptionPlugin:
    """File encryption commands."""
    
    SYSTEM_PROMPT = """You are an encryption expert. Generate OpenSSL/GPG encryption commands.
Output only the command."""
    
    TEMPLATES = {
        "encrypt_file": "openssl enc -aes-256-cbc -salt -pbkdf2 -in {input} -out {output}.enc",
        "decrypt_file": "openssl enc -aes-256-cbc -d -pbkdf2 -in {input} -out {output}",
        "encrypt_gpg": "gpg -c --cipher-algo AES256 {file}",
        "decrypt_gpg": "gpg -d {file}.gpg > {file}",
        "generate_key": "openssl rand -base64 32",
        "hash_file": "sha256sum {file}",
        "sign_file": "gpg --sign {file}",
        "verify_sig": "gpg --verify {file}.sig",
    }


class AuditPlugin:
    """Security audit commands."""
    
    SYSTEM_PROMPT = """You are a security auditor. Generate commands for security auditing.
Include file permissions, open ports, running services checks."""
    
    AUDIT_COMMANDS = {
        "linux": [
            "find / -perm -4000 2>/dev/null",  # SUID files
            "netstat -tulpn",  # Open ports
            "last -10",  # Recent logins
            "cat /etc/passwd | grep -v nologin",  # Users with shell
            "ss -tulpn",  # Socket stats
            "systemctl list-units --type=service --state=running",  # Running services
        ],
        "windows": [
            "netstat -an | findstr LISTENING",
            "net user",
            "Get-LocalUser | Select Name,Enabled",
            "Get-Service | Where-Object {$_.Status -eq 'Running'}",
        ]
    }


class FirewallPlugin:
    """Firewall command generator."""
    
    SYSTEM_PROMPT = """You are a firewall expert. Generate iptables/ufw/firewalld commands.
Output practical, safe firewall rules."""
    
    TEMPLATES = {
        "ufw_allow": "ufw allow {port}/{protocol}",
        "ufw_deny": "ufw deny {port}",
        "ufw_status": "ufw status verbose",
        "iptables_allow": "iptables -A INPUT -p {protocol} --dport {port} -j ACCEPT",
        "iptables_list": "iptables -L -n -v",
    }


class SSLPlugin:
    """SSL/TLS certificate commands."""
    
    SYSTEM_PROMPT = """You are an SSL/TLS expert. Generate certificate commands.
Include OpenSSL, Let's Encrypt, and certificate checking."""
    
    TEMPLATES = {
        "generate_self_signed": "openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes",
        "generate_csr": "openssl req -new -newkey rsa:2048 -nodes -keyout {domain}.key -out {domain}.csr",
        "check_cert": "openssl s_client -connect {domain}:443 -servername {domain} 2>/dev/null | openssl x509 -noout -dates",
        "check_cert_local": "openssl x509 -in {file} -text -noout",
        "certbot_get": "certbot certonly --standalone -d {domain}",
        "certbot_renew": "certbot renew --dry-run",
    }


class PasswordPlugin:
    """Password generation commands."""
    
    TEMPLATES = {
        "generate_strong": "openssl rand -base64 32",
        "generate_hex": "openssl rand -hex 16",
        "generate_alphanumeric": "cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1",
        "hash_password": "echo -n '{password}' | sha256sum",
        "bcrypt_hash": "python3 -c \"import bcrypt; print(bcrypt.hashpw(b'{password}', bcrypt.gensalt()).decode())\"",
    }


class SSHPlugin:
    """SSH security commands."""
    
    SYSTEM_PROMPT = """You are an SSH expert. Generate SSH commands and configurations.
Focus on security best practices."""
    
    TEMPLATES = {
        "generate_key": "ssh-keygen -t ed25519 -C '{email}'",
        "copy_key": "ssh-copy-id -i ~/.ssh/id_ed25519.pub {user}@{host}",
        "tunnel": "ssh -L {local_port}:localhost:{remote_port} {user}@{host}",
        "socks_proxy": "ssh -D {port} -N {user}@{host}",
        "port_forward": "ssh -R {remote_port}:localhost:{local_port} {user}@{host}",
        "check_fingerprint": "ssh-keygen -lf {key_file}",
    }


class VPNPlugin:
    """VPN configuration commands."""
    
    TEMPLATES = {
        "wireguard_keygen": "wg genkey | tee privatekey | wg pubkey > publickey",
        "wireguard_up": "wg-quick up {interface}",
        "wireguard_down": "wg-quick down {interface}",
        "openvpn_connect": "openvpn --config {config_file}",
    }


class MalwarePlugin:
    """Malware scanning commands."""
    
    TEMPLATES = {
        "clamav_scan": "clamscan -r {directory}",
        "clamav_update": "freshclam",
        "rkhunter": "rkhunter --check",
        "chkrootkit": "chkrootkit",
    }
