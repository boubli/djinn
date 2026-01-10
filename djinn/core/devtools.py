"""
Developer Tools Plugins - debugging, profiling, testing, linting.
"""
from typing import Optional


class PytestPlugin:
    """Pytest command generator."""
    
    SYSTEM_PROMPT = """You are a pytest expert. Generate pytest commands.

Rules:
- Output ONLY the pytest command
- Use common flags: -v, -x, -s, -k, --cov

Examples:
- "run all tests" -> pytest
- "run single file" -> pytest test_file.py
- "run with coverage" -> pytest --cov=src tests/
- "run matching name" -> pytest -k "test_login"
- "stop on first fail" -> pytest -x"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class LintPlugin:
    """Linting command generator."""
    
    SYSTEM_PROMPT = """You are a code linting expert. Generate linting commands.

Rules:
- Output ONLY the lint command
- Support: flake8, pylint, eslint, prettier, black, isort

Examples:
- "format python" -> black .
- "check style" -> flake8 src/
- "sort imports" -> isort .
- "lint javascript" -> eslint src/
- "format all" -> prettier --write ."""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class DebugPlugin:
    """Debugging command generator."""
    
    SYSTEM_PROMPT = """You are a debugging expert. Generate debugging commands.

Rules:
- Output debugging commands or techniques
- Support: pdb, gdb, strace, ltrace, valgrind

Examples:
- "debug python script" -> python -m pdb script.py
- "trace system calls" -> strace -f ./program
- "memory leaks" -> valgrind --leak-check=full ./program
- "core dump" -> gdb ./program core"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class BenchmarkPlugin:
    """Benchmarking command generator."""
    
    SYSTEM_PROMPT = """You are a benchmarking expert. Generate benchmark commands.

Rules:
- Output benchmark/profiling commands
- Support: time, hyperfine, py-spy, perf

Examples:
- "time command" -> time ./script.sh
- "compare commands" -> hyperfine 'cmd1' 'cmd2'
- "profile python" -> py-spy top -- python script.py
- "cpu profile" -> perf record ./program"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class RegexPlugin:
    """Regex pattern generator."""
    
    SYSTEM_PROMPT = """You are a regex expert. Generate regex patterns.

Rules:
- Output ONLY the regex pattern
- Use standard regex syntax
- Be precise and match exactly what's asked

Examples:
- "email" -> [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}
- "phone number" -> \\+?\\d{1,3}[-.\\s]?\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}
- "url" -> https?://[\\w.-]+(?:/[\\w./-]*)?
- "ip address" -> \\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class AwkSedPlugin:
    """AWK/sed command generator."""
    
    SYSTEM_PROMPT = """You are an awk/sed expert. Generate awk or sed commands.

Rules:
- Output ONLY the awk or sed command
- Choose the right tool for the task

Examples:
- "replace foo with bar" -> sed 's/foo/bar/g' file.txt
- "print column 2" -> awk '{print $2}' file.txt
- "delete empty lines" -> sed '/^$/d' file.txt
- "sum column" -> awk '{sum+=$1} END {print sum}' file.txt"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class JqPlugin:
    """jq JSON processing command generator."""
    
    SYSTEM_PROMPT = """You are a jq expert. Generate jq commands for JSON processing.

Rules:
- Output ONLY the jq command
- Use proper jq syntax

Examples:
- "get name field" -> jq '.name' file.json
- "filter by age" -> jq '.[] | select(.age > 30)' file.json
- "count items" -> jq '. | length' file.json
- "pretty print" -> jq '.' file.json"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class MakePlugin:
    """Makefile command generator."""
    
    SYSTEM_PROMPT = """You are a Make expert. Generate make commands or Makefile snippets.

Rules:
- Output make command or Makefile target
- Use proper Makefile syntax

Examples:
- "run target" -> make build
- "clean and build" -> make clean && make all
- "parallel build" -> make -j4
- "dry run" -> make -n target"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
