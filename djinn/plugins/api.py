"""
API and Web Plugins - API testing and web tool commands.
"""


class HttpiePlugin:
    """HTTPie API testing commands."""
    
    TEMPLATES = {
        "get": "http GET {url}",
        "post": "http POST {url} {key}={value}",
        "post_json": "http POST {url} Content-Type:application/json < {file}.json",
        "put": "http PUT {url} {key}={value}",
        "delete": "http DELETE {url}",
        "headers": "http --headers GET {url}",
        "auth": "http -a {user}:{password} GET {url}",
        "bearer": "http GET {url} 'Authorization:Bearer {token}'",
        "download": "http --download GET {url}",
        "form": "http --form POST {url} {key}={value}",
    }


class CurlAdvancedPlugin:
    """Advanced curl commands."""
    
    TEMPLATES = {
        "graphql": "curl -X POST -H 'Content-Type: application/json' -d '{{\"query\": \"{query}\"}}' {url}",
        "multipart": "curl -X POST -F 'file=@{file}' {url}",
        "cookies": "curl -b {cookie_file} {url}",
        "save_cookies": "curl -c {cookie_file} {url}",
        "proxy": "curl -x {proxy} {url}",
        "retry": "curl --retry {count} {url}",
        "compressed": "curl --compressed {url}",
        "user_agent": "curl -A '{user_agent}' {url}",
        "referer": "curl -e '{referer}' {url}",
        "insecure": "curl -k {url}",
        "trace": "curl --trace-ascii - {url}",
    }


class PostmanPlugin:
    """Postman/Newman commands."""
    
    TEMPLATES = {
        "run_collection": "newman run {collection}.json",
        "run_environment": "newman run {collection}.json -e {environment}.json",
        "run_reporters": "newman run {collection}.json -r cli,json",
        "run_iteration": "newman run {collection}.json -n {count}",
    }


class GrpcPlugin:
    """gRPC commands."""
    
    TEMPLATES = {
        "list_services": "grpcurl -plaintext {host}:{port} list",
        "describe": "grpcurl -plaintext {host}:{port} describe {service}",
        "call": "grpcurl -plaintext -d '{{}}' {host}:{port} {service}/{method}",
    }


class WebsocketPlugin:
    """WebSocket commands."""
    
    TEMPLATES = {
        "connect": "websocat {url}",
        "send": "echo '{message}' | websocat {url}",
        "listen": "websocat -t {url}",
    }


class OpenAPIPlugin:
    """OpenAPI/Swagger commands."""
    
    TEMPLATES = {
        "validate": "swagger-cli validate {spec}.yaml",
        "bundle": "swagger-cli bundle {spec}.yaml -o {output}.yaml",
        "generate_client": "openapi-generator generate -i {spec}.yaml -g {language} -o {output}",
    }


class WebServerPlugin:
    """Quick web server commands."""
    
    TEMPLATES = {
        "python_server": "python -m http.server {port}",
        "python_server3": "python3 -m http.server {port}",
        "node_server": "npx serve -p {port}",
        "php_server": "php -S localhost:{port}",
        "ruby_server": "ruby -run -e httpd . -p {port}",
        "caddy": "caddy file-server --browse --listen :{port}",
    }


class LighthousePlugin:
    """Lighthouse performance testing."""
    
    TEMPLATES = {
        "run": "lighthouse {url} --output html --output-path ./report.html",
        "mobile": "lighthouse {url} --emulated-form-factor=mobile",
        "desktop": "lighthouse {url} --emulated-form-factor=desktop",
        "json": "lighthouse {url} --output json --output-path ./report.json",
    }


class ScrapingPlugin:
    """Web scraping commands."""
    
    TEMPLATES = {
        "wget_site": "wget --mirror --convert-links --adjust-extension --page-requisites --no-parent {url}",
        "html_to_text": "curl -s {url} | html2text",
        "links_extract": "curl -s {url} | grep -oP 'href=\"\\K[^\"]+' | sort -u",
    }


class SSLCheckPlugin:
    """SSL certificate checking."""
    
    TEMPLATES = {
        "check_cert": "echo | openssl s_client -connect {host}:443 -servername {host} 2>/dev/null | openssl x509 -noout -dates",
        "full_chain": "echo | openssl s_client -connect {host}:443 -showcerts 2>/dev/null",
        "cipher_test": "nmap --script ssl-enum-ciphers -p 443 {host}",
        "testssl": "testssl.sh {host}",
    }


class DnsToolsPlugin:
    """Advanced DNS tools."""
    
    TEMPLATES = {
        "dnsrecon": "dnsrecon -d {domain}",
        "subfinder": "subfinder -d {domain}",
        "amass": "amass enum -d {domain}",
        "fierce": "fierce --domain {domain}",
    }
