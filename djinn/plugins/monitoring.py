"""
Monitoring and Performance Plugins - System monitoring commands.
"""


class SarPlugin:
    """System Activity Reporter commands."""
    
    TEMPLATES = {
        "cpu": "sar -u 1 5",
        "memory": "sar -r 1 5",
        "disk": "sar -d 1 5",
        "network": "sar -n DEV 1 5",
        "load": "sar -q 1 5",
        "all": "sar -A",
    }


class TopPlugin:
    """Top-like monitoring commands."""
    
    TEMPLATES = {
        "top": "top",
        "htop": "htop",
        "btop": "btop",
        "glances": "glances",
        "atop": "atop",
        "nmon": "nmon",
        "vtop": "vtop",
        "gtop": "gtop",
    }


class DstatPlugin:
    """Dstat monitoring commands."""
    
    TEMPLATES = {
        "default": "dstat",
        "cpu_mem": "dstat -c -m",
        "disk": "dstat -d",
        "network": "dstat -n",
        "all": "dstat -a",
    }


class BenchmarkPlugin:
    """Benchmarking commands."""
    
    TEMPLATES = {
        "sysbench_cpu": "sysbench cpu run",
        "sysbench_memory": "sysbench memory run",
        "sysbench_io": "sysbench fileio --file-test-mode=seqwr run",
        "fio_read": "fio --name=read --rw=read --size={size}",
        "fio_write": "fio --name=write --rw=write --size={size}",
        "dd_write": "dd if=/dev/zero of=testfile bs=1G count=1 oflag=direct",
        "dd_read": "dd if=testfile of=/dev/null bs=1G count=1 iflag=direct",
        "stress_cpu": "stress --cpu {cores} --timeout {seconds}s",
        "stress_memory": "stress --vm {workers} --vm-bytes {size} --timeout {seconds}s",
        "hyperfine": "hyperfine '{command}'",
    }


class ProfilingPlugin:
    """Profiling commands."""
    
    TEMPLATES = {
        "perf_record": "perf record -g {command}",
        "perf_report": "perf report",
        "perf_stat": "perf stat {command}",
        "strace": "strace {command}",
        "strace_count": "strace -c {command}",
        "ltrace": "ltrace {command}",
        "time": "time {command}",
        "valgrind": "valgrind --leak-check=full {command}",
    }


class NetworkMonitorPlugin:
    """Network monitoring commands."""
    
    TEMPLATES = {
        "iftop": "iftop -i {interface}",
        "nethogs": "nethogs {interface}",
        "bmon": "bmon",
        "nload": "nload {interface}",
        "vnstat": "vnstat -i {interface}",
        "vnstat_live": "vnstat -l -i {interface}",
        "iptraf": "iptraf-ng",
        "tcptrack": "tcptrack -i {interface}",
    }


class LogMonitorPlugin:
    """Log monitoring commands."""
    
    TEMPLATES = {
        "tail_syslog": "tail -f /var/log/syslog",
        "tail_auth": "tail -f /var/log/auth.log",
        "multitail": "multitail /var/log/syslog /var/log/auth.log",
        "lnav": "lnav /var/log/syslog",
        "goaccess": "goaccess /var/log/nginx/access.log",
        "logwatch": "logwatch --detail high --mailto {email}",
    }


class PrometheusPlugin:
    """Prometheus commands."""
    
    TEMPLATES = {
        "query": "curl 'http://localhost:9090/api/v1/query?query={query}'",
        "query_range": "curl 'http://localhost:9090/api/v1/query_range?query={query}&start={start}&end={end}&step={step}'",
        "targets": "curl http://localhost:9090/api/v1/targets",
        "config_reload": "curl -X POST http://localhost:9090/-/reload",
    }


class DockerStatsPlugin:
    """Docker monitoring commands."""
    
    TEMPLATES = {
        "stats": "docker stats",
        "stats_no_stream": "docker stats --no-stream",
        "ctop": "ctop",
        "lazydocker": "lazydocker",
    }


class KubeMonitorPlugin:
    """Kubernetes monitoring commands."""
    
    TEMPLATES = {
        "k9s": "k9s",
        "top_pods": "kubectl top pods",
        "top_nodes": "kubectl top nodes",
        "events": "kubectl get events --watch",
        "logs_stern": "stern {pattern}",
        "lens": "lens",
    }
