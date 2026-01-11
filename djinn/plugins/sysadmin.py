"""
System Administration Plugins - System admin commands.
"""


class ProcessPlugin:
    """Process management commands."""
    
    TEMPLATES = {
        "list": "ps aux",
        "top": "top",
        "htop": "htop",
        "find": "ps aux | grep {process}",
        "kill": "kill {pid}",
        "kill_force": "kill -9 {pid}",
        "killall": "killall {name}",
        "pkill": "pkill -f {pattern}",
        "nice": "nice -n {priority} {command}",
        "renice": "renice {priority} -p {pid}",
        "nohup": "nohup {command} &",
        "bg": "bg %{job}",
        "fg": "fg %{job}",
        "jobs": "jobs",
    }


class ServicePlugin:
    """Service management commands."""
    
    TEMPLATES = {
        "list": "systemctl list-units --type=service",
        "status": "systemctl status {service}",
        "start": "systemctl start {service}",
        "stop": "systemctl stop {service}",
        "restart": "systemctl restart {service}",
        "enable": "systemctl enable {service}",
        "disable": "systemctl disable {service}",
        "logs": "journalctl -u {service} -f",
        "reload": "systemctl daemon-reload",
    }


class DiskPlugin:
    """Disk management commands."""
    
    TEMPLATES = {
        "usage": "df -h",
        "du": "du -sh *",
        "du_sort": "du -sh * | sort -hr | head -20",
        "lsblk": "lsblk",
        "fdisk": "fdisk -l",
        "mount": "mount {device} {mountpoint}",
        "umount": "umount {mountpoint}",
        "mkfs": "mkfs.ext4 {device}",
        "fsck": "fsck {device}",
        "iostat": "iostat",
        "iotop": "iotop",
    }


class MemoryPlugin:
    """Memory management commands."""
    
    TEMPLATES = {
        "free": "free -h",
        "available": "cat /proc/meminfo | grep MemAvailable",
        "top_memory": "ps aux --sort=-%mem | head -10",
        "cache_clear": "sync && echo 3 > /proc/sys/vm/drop_caches",
        "swap": "swapon --show",
        "vmstat": "vmstat 1 5",
    }


class UserPlugin:
    """User management commands."""
    
    TEMPLATES = {
        "list": "cat /etc/passwd",
        "add": "useradd -m -s /bin/bash {username}",
        "del": "userdel -r {username}",
        "passwd": "passwd {username}",
        "groups": "groups {username}",
        "add_group": "usermod -aG {group} {username}",
        "sudo_add": "usermod -aG sudo {username}",
        "lock": "usermod -L {username}",
        "unlock": "usermod -U {username}",
        "whoami": "whoami",
        "id": "id {username}",
        "last": "last",
        "w": "w",
    }


class PermissionPlugin:
    """File permission commands."""
    
    TEMPLATES = {
        "chmod": "chmod {mode} {file}",
        "chmod_r": "chmod -R {mode} {directory}",
        "chown": "chown {user}:{group} {file}",
        "chown_r": "chown -R {user}:{group} {directory}",
        "readable": "chmod +r {file}",
        "writable": "chmod +w {file}",
        "executable": "chmod +x {file}",
        "700": "chmod 700 {file}",
        "755": "chmod 755 {file}",
        "644": "chmod 644 {file}",
    }


class CronPlugin:
    """Cron job commands."""
    
    TEMPLATES = {
        "list": "crontab -l",
        "edit": "crontab -e",
        "remove": "crontab -r",
        "hourly": "echo '0 * * * * {command}' | crontab -",
        "daily": "echo '0 0 * * * {command}' | crontab -",
        "weekly": "echo '0 0 * * 0 {command}' | crontab -",
        "monthly": "echo '0 0 1 * * {command}' | crontab -",
    }


class SystemInfoPlugin:
    """System information commands."""
    
    TEMPLATES = {
        "uname": "uname -a",
        "hostname": "hostname",
        "uptime": "uptime",
        "date": "date",
        "cal": "cal",
        "lscpu": "lscpu",
        "lsmem": "lsmem",
        "lspci": "lspci",
        "lsusb": "lsusb",
        "dmesg": "dmesg | tail -50",
        "env": "env",
        "arch": "arch",
    }


class PackagePlugin:
    """Package management commands."""
    
    TEMPLATES = {
        # APT (Debian/Ubuntu)
        "apt_update": "apt update",
        "apt_upgrade": "apt upgrade -y",
        "apt_install": "apt install -y {package}",
        "apt_remove": "apt remove {package}",
        "apt_search": "apt search {package}",
        "apt_autoremove": "apt autoremove -y",
        
        # YUM/DNF (RHEL/CentOS/Fedora)
        "dnf_install": "dnf install -y {package}",
        "dnf_remove": "dnf remove {package}",
        "dnf_update": "dnf update -y",
        
        # Pacman (Arch)
        "pacman_install": "pacman -S {package}",
        "pacman_remove": "pacman -R {package}",
        "pacman_update": "pacman -Syu",
        
        # Homebrew (macOS)
        "brew_install": "brew install {package}",
        "brew_remove": "brew uninstall {package}",
        "brew_update": "brew update && brew upgrade",
        
        # Snap
        "snap_install": "snap install {package}",
        "snap_remove": "snap remove {package}",
        "snap_list": "snap list",
    }


class LogPlugin:
    """Log viewing commands."""
    
    TEMPLATES = {
        "syslog": "tail -f /var/log/syslog",
        "auth": "tail -f /var/log/auth.log",
        "kernel": "dmesg | tail -50",
        "journalctl": "journalctl -xe",
        "journalctl_boot": "journalctl -b",
        "journalctl_service": "journalctl -u {service}",
        "last": "last",
        "lastb": "lastb",
    }


class BackupPlugin:
    """Backup commands."""
    
    TEMPLATES = {
        "tar_create": "tar -czvf {archive}.tar.gz {directory}",
        "tar_extract": "tar -xzvf {archive}.tar.gz",
        "rsync": "rsync -avz {source} {destination}",
        "rsync_ssh": "rsync -avz -e ssh {source} {user}@{host}:{destination}",
        "dd": "dd if={input} of={output} bs=4M status=progress",
        "zip": "zip -r {archive}.zip {directory}",
        "unzip": "unzip {archive}.zip",
    }
