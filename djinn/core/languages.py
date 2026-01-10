"""
Language-specific Plugins - Python, JavaScript, Rust, Go, etc.
"""
from typing import Optional


class PythonPlugin:
    """Python development command generator."""
    
    SYSTEM_PROMPT = """You are a Python expert. Generate Python commands.

Examples:
- "create venv" -> python -m venv venv
- "run script" -> python script.py
- "install dev deps" -> pip install -e ".[dev]"
- "create package" -> python -m build"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class NodePlugin:
    """Node.js development command generator."""
    
    SYSTEM_PROMPT = """You are a Node.js expert. Generate Node.js commands.

Examples:
- "run server" -> node server.js
- "debug mode" -> node --inspect server.js
- "run ts" -> npx ts-node script.ts
- "init project" -> npm init -y"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class RustPlugin:
    """Rust development command generator."""
    
    SYSTEM_PROMPT = """You are a Rust expert. Generate Rust/cargo commands.

Examples:
- "build release" -> cargo build --release
- "run tests" -> cargo test
- "new project" -> cargo new project_name
- "add dependency" -> cargo add package_name"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class GoPlugin:
    """Go development command generator."""
    
    SYSTEM_PROMPT = """You are a Go expert. Generate Go commands.

Examples:
- "build" -> go build
- "run" -> go run main.go
- "get package" -> go get package
- "test" -> go test ./..."""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class JavaPlugin:
    """Java development command generator."""
    
    SYSTEM_PROMPT = """You are a Java expert. Generate Java/Maven/Gradle commands.

Examples:
- "compile" -> javac Main.java
- "run" -> java Main
- "maven build" -> mvn clean install
- "gradle build" -> ./gradlew build"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class CppPlugin:
    """C++ development command generator."""
    
    SYSTEM_PROMPT = """You are a C++ expert. Generate C++ compilation commands.

Examples:
- "compile" -> g++ -o program main.cpp
- "with debug" -> g++ -g -o program main.cpp
- "optimize" -> g++ -O3 -o program main.cpp
- "cmake build" -> mkdir build && cd build && cmake .. && make"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
