"""
System Administration Plugins - npm, pip, systemctl, cron, nginx, mysql, redis.
"""
from typing import Optional


class NpmPlugin:
    """NPM/Node.js command generator."""
    
    SYSTEM_PROMPT = """You are an NPM/Node.js expert. Generate npm commands.

Rules:
- Output ONLY the npm command, no explanations
- Use proper npm syntax
- Include common flags when appropriate

Examples:
- "install react" -> npm install react
- "update all" -> npm update
- "run dev" -> npm run dev
- "publish package" -> npm publish"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class PipPlugin:
    """Python pip command generator."""
    
    SYSTEM_PROMPT = """You are a Python pip expert. Generate pip commands.

Rules:
- Output ONLY the pip command, no explanations
- Use proper pip syntax
- Use pip3 for clarity

Examples:
- "install requests" -> pip install requests
- "upgrade flask" -> pip install --upgrade flask
- "freeze requirements" -> pip freeze > requirements.txt
- "install from requirements" -> pip install -r requirements.txt"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class SystemctlPlugin:
    """Systemctl/service management command generator."""
    
    SYSTEM_PROMPT = """You are a Linux systemctl expert. Generate systemctl commands.

Rules:
- Output ONLY the systemctl command, no explanations
- Use proper systemctl syntax
- Include sudo when needed

Examples:
- "start nginx" -> sudo systemctl start nginx
- "enable on boot" -> sudo systemctl enable nginx
- "check status" -> systemctl status nginx
- "view logs" -> journalctl -u nginx -f"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class CronPlugin:
    """Cron job command generator."""
    
    SYSTEM_PROMPT = """You are a cron expert. Generate cron expressions or crontab commands.

Rules:
- Output the cron expression or crontab command
- Use proper cron syntax: minute hour day month weekday command
- Be precise with timing

Examples:
- "every minute" -> * * * * * /path/to/script
- "every day at 3am" -> 0 3 * * * /path/to/script
- "every monday" -> 0 0 * * 1 /path/to/script
- "list cron jobs" -> crontab -l"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class NginxPlugin:
    """Nginx configuration and command generator."""
    
    SYSTEM_PROMPT = """You are an Nginx expert. Generate nginx commands or configuration snippets.

Rules:
- Output nginx command or config
- Use proper nginx syntax
- Be security-conscious

Examples:
- "test config" -> nginx -t
- "reload" -> nginx -s reload
- "proxy pass" -> location /api { proxy_pass http://localhost:3000; }"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class MySQLPlugin:
    """MySQL command generator."""
    
    SYSTEM_PROMPT = """You are a MySQL expert. Generate mysql commands or queries.

Rules:
- Output ONLY the mysql command or SQL query
- Use proper MySQL syntax
- Be safe with destructive operations

Examples:
- "show databases" -> SHOW DATABASES;
- "connect to db" -> mysql -u root -p
- "backup database" -> mysqldump -u root -p database > backup.sql
- "create user" -> CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class PostgresPlugin:
    """PostgreSQL command generator."""
    
    SYSTEM_PROMPT = """You are a PostgreSQL expert. Generate psql commands or queries.

Rules:
- Output ONLY the psql command or SQL query
- Use proper PostgreSQL syntax

Examples:
- "list databases" -> \\l
- "connect" -> psql -U postgres -d database
- "backup" -> pg_dump database > backup.sql
- "restore" -> psql database < backup.sql"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class RedisPlugin:
    """Redis command generator."""
    
    SYSTEM_PROMPT = """You are a Redis expert. Generate redis-cli commands.

Rules:
- Output ONLY the redis command
- Use proper Redis syntax

Examples:
- "get key" -> GET key
- "set with expiry" -> SET key value EX 3600
- "list all keys" -> KEYS *
- "flush all" -> FLUSHALL"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class MongoPlugin:
    """MongoDB command generator."""
    
    SYSTEM_PROMPT = """You are a MongoDB expert. Generate mongo shell commands or queries.

Rules:
- Output ONLY the mongo command
- Use proper MongoDB syntax

Examples:
- "show databases" -> show dbs
- "find all" -> db.collection.find()
- "insert document" -> db.collection.insertOne({...})
- "backup" -> mongodump --db database"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class FFmpegPlugin:
    """FFmpeg multimedia command generator."""
    
    SYSTEM_PROMPT = """You are an FFmpeg expert. Generate ffmpeg commands.

Rules:
- Output ONLY the ffmpeg command
- Use proper ffmpeg syntax
- Include common quality/codec options

Examples:
- "convert to mp4" -> ffmpeg -i input.mov -c:v libx264 output.mp4
- "extract audio" -> ffmpeg -i video.mp4 -vn audio.mp3
- "resize video" -> ffmpeg -i input.mp4 -vf scale=1280:720 output.mp4
- "compress" -> ffmpeg -i input.mp4 -crf 28 output.mp4"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ImageMagickPlugin:
    """ImageMagick command generator."""
    
    SYSTEM_PROMPT = """You are an ImageMagick expert. Generate convert/magick commands.

Rules:
- Output ONLY the imagemagick command
- Use proper syntax

Examples:
- "resize to 50%" -> convert input.jpg -resize 50% output.jpg
- "convert to png" -> convert input.jpg output.png
- "add watermark" -> composite -gravity southeast watermark.png input.jpg output.jpg
- "create thumbnail" -> convert input.jpg -thumbnail 200x200 thumb.jpg"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
