"""
DJINN Plugins Package - All specialized plugins.
"""

from .security import *
from .database import *
from .networking import *
from .cloud import *
from .sysadmin import *
from .containers import *
from .development import *
from .git_advanced import *
from .files import *
from .api import *
from .monitoring import *
from .misc import *

__all__ = [
    # Security
    'SecretsScanner', 'HardeningPlugin', 'EncryptionPlugin', 'AuditPlugin',
    'FirewallPlugin', 'SSLPlugin', 'PasswordPlugin', 'SSHPlugin', 'VPNPlugin', 'MalwarePlugin',
    
    # Database
    'MySQLPlugin', 'PostgresPlugin', 'MongoDBPlugin', 'RedisPlugin',
    'SQLitePlugin', 'ElasticsearchPlugin', 'CassandraPlugin', 'InfluxDBPlugin',
    
    # Networking
    'PingPlugin', 'DNSPlugin', 'PortPlugin', 'CurlPlugin', 'WgetPlugin',
    'InterfacePlugin', 'BandwidthPlugin', 'TCPDumpPlugin', 'NetcatPlugin', 'ArpPlugin',
    
    # Cloud
    'AWSPlugin', 'GCPPlugin', 'AzurePlugin', 'DigitalOceanPlugin',
    'HerokuPlugin', 'VercelPlugin', 'NetlifyPlugin',
    
    # System Admin
    'ProcessPlugin', 'ServicePlugin', 'DiskPlugin', 'MemoryPlugin',
    'UserPlugin', 'PermissionPlugin', 'CronPlugin', 'SystemInfoPlugin',
    'PackagePlugin', 'LogPlugin', 'BackupPlugin',
    
    # Containers
    'DockerPlugin', 'DockerComposePlugin', 'KubernetesPlugin', 'HelmPlugin', 'PodmanPlugin',
    
    # Development
    'NodePlugin', 'PythonPlugin', 'GoPlugin', 'RustPlugin',
    'JavaPlugin', 'DotNetPlugin', 'RubyPlugin', 'PHPPlugin',
    'FlutterPlugin', 'TerraformPlugin', 'AnsiblePlugin',
    
    # Git
    'GitPlugin', 'GitHubPlugin', 'GitLabPlugin',
    
    # Files
    'FindPlugin', 'GrepPlugin', 'SedPlugin', 'AwkPlugin',
    'TextPlugin', 'FilePlugin', 'ArchivePlugin', 'DiffPlugin',
    'EncodingPlugin', 'JqPlugin', 'YqPlugin',
    
    # API
    'HttpiePlugin', 'CurlAdvancedPlugin', 'PostmanPlugin', 'GrpcPlugin',
    'WebsocketPlugin', 'OpenAPIPlugin', 'WebServerPlugin', 'LighthousePlugin',
    'ScrapingPlugin', 'SSLCheckPlugin', 'DnsToolsPlugin',
    
    # Monitoring
    'SarPlugin', 'TopPlugin', 'DstatPlugin', 'BenchmarkPlugin',
    'ProfilingPlugin', 'NetworkMonitorPlugin', 'LogMonitorPlugin',
    'PrometheusPlugin', 'DockerStatsPlugin', 'KubeMonitorPlugin',
    
    # Misc
    'TmuxPlugin', 'ScreenPlugin', 'MediaPlugin', 'YouTubePlugin',
    'PDFPlugin', 'DateTimePlugin', 'CalculatorPlugin', 'RandomPlugin',
    'WatchPlugin', 'ClipboardPlugin', 'QRPlugin', 'SpeedPlugin',
    'WeatherPlugin', 'ASCIIPlugin',
]
