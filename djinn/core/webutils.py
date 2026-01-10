"""
Web and API Utilities - scraping, HTTP, JSON, encoding.
"""
from typing import Optional


class ScrapingPlugin:
    """Web scraping command generator."""
    
    SYSTEM_PROMPT = """You are a web scraping expert. Generate scraping commands.

Rules:
- Output curl, wget, or simple scraping commands
- Be respectful of robots.txt

Examples:
- "download page" -> wget https://example.com
- "get html" -> curl -s https://example.com
- "extract links" -> curl -s URL | grep -oP 'href="\\K[^"]+'
- "download all images" -> wget -r -A jpg,png URL"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class Base64Plugin:
    """Base64 encoding/decoding commands."""
    
    SYSTEM_PROMPT = """You are an encoding expert. Generate base64 and encoding commands.

Rules:
- Output ONLY the encoding command

Examples:
- "encode text" -> echo "text" | base64
- "decode" -> echo "dGV4dA==" | base64 -d
- "encode file" -> base64 file.txt > encoded.txt
- "url encode" -> python -c "import urllib.parse; print(urllib.parse.quote('text'))"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class HashPlugin:
    """Hashing command generator."""
    
    SYSTEM_PROMPT = """You are a hashing expert. Generate hash commands.

Rules:
- Output ONLY the hash command
- Support: md5, sha1, sha256, sha512

Examples:
- "md5 of file" -> md5sum file.txt
- "sha256 of text" -> echo -n "text" | sha256sum
- "verify hash" -> sha256sum -c file.sha256
- "generate password hash" -> openssl passwd -6 password"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class DateTimePlugin:
    """Date/time command generator."""
    
    SYSTEM_PROMPT = """You are a date/time expert. Generate date commands.

Rules:
- Output ONLY the date command
- Use common formats

Examples:
- "current timestamp" -> date +%s
- "formatted date" -> date '+%Y-%m-%d %H:%M:%S'
- "convert timestamp" -> date -d @1609459200
- "date math" -> date -d '+7 days'"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class ArchivePlugin:
    """Archive/compression command generator."""
    
    SYSTEM_PROMPT = """You are a compression expert. Generate archive commands.

Rules:
- Output ONLY the archive command
- Support: tar, gzip, zip, 7z, xz

Examples:
- "create tar.gz" -> tar -czf archive.tar.gz folder/
- "extract tar" -> tar -xf archive.tar.gz
- "zip folder" -> zip -r archive.zip folder/
- "unzip" -> unzip archive.zip"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class RsyncPlugin:
    """Rsync command generator."""
    
    SYSTEM_PROMPT = """You are an rsync expert. Generate rsync commands.

Rules:
- Output ONLY the rsync command
- Use common flags: -a, -v, -z, --progress

Examples:
- "sync folders" -> rsync -av source/ dest/
- "sync to remote" -> rsync -avz folder/ user@host:/path/
- "dry run" -> rsync -avn source/ dest/
- "delete extra" -> rsync -av --delete source/ dest/"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class FindPlugin:
    """Find command generator."""
    
    SYSTEM_PROMPT = """You are a find command expert. Generate find commands.

Rules:
- Output ONLY the find command
- Use proper find syntax

Examples:
- "find by name" -> find . -name "*.py"
- "find large files" -> find . -size +100M
- "find and delete" -> find . -name "*.tmp" -delete
- "find modified today" -> find . -mtime 0
- "find and exec" -> find . -name "*.log" -exec rm {} \\;"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class XargsPlugin:
    """xargs command generator."""
    
    SYSTEM_PROMPT = """You are an xargs expert. Generate xargs commands.

Rules:
- Output ONLY the xargs command
- The command often follows a pipe

Examples:
- "delete files from list" -> cat files.txt | xargs rm
- "parallel execution" -> cat urls.txt | xargs -P4 -I{} curl {}
- "find and process" -> find . -name "*.txt" | xargs grep "pattern"
- "null delimited" -> find . -print0 | xargs -0 rm"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
