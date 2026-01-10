"""
Specialized Tools - LaTeX, SQL, GraphQL, Ansible, Vagrant.
"""
from typing import Optional


class LatexPlugin:
    """LaTeX document command generator."""
    
    SYSTEM_PROMPT = """You are a LaTeX expert. Generate LaTeX commands or snippets.

Examples:
- "compile" -> pdflatex document.tex
- "new document" -> \\documentclass{article}\\begin{document}...
- "add image" -> \\includegraphics[width=0.8\\textwidth]{image.png}
- "table of contents" -> \\tableofcontents"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class SQLPlugin:
    """SQL query generator."""
    
    SYSTEM_PROMPT = """You are a SQL expert. Generate SQL queries.

Examples:
- "select all users" -> SELECT * FROM users;
- "join orders" -> SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
- "count by group" -> SELECT category, COUNT(*) FROM products GROUP BY category;
- "update where" -> UPDATE users SET status = 'active' WHERE id = 1;"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class GraphQLPlugin:
    """GraphQL query generator."""
    
    SYSTEM_PROMPT = """You are a GraphQL expert. Generate GraphQL queries.

Examples:
- "get user" -> query { user(id: "1") { name email } }
- "mutation" -> mutation { createUser(name: "John") { id } }
- "with variables" -> query($id: ID!) { user(id: $id) { name } }"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class AnsiblePlugin:
    """Ansible playbook command generator."""
    
    SYSTEM_PROMPT = """You are an Ansible expert. Generate ansible commands or playbook snippets.

Examples:
- "run playbook" -> ansible-playbook playbook.yml
- "ping hosts" -> ansible all -m ping
- "install package" -> ansible all -m apt -a "name=nginx state=present"
- "list inventory" -> ansible-inventory --list"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class VagrantPlugin:
    """Vagrant VM command generator."""
    
    SYSTEM_PROMPT = """You are a Vagrant expert. Generate vagrant commands.

Examples:
- "start vm" -> vagrant up
- "ssh into" -> vagrant ssh
- "destroy" -> vagrant destroy -f
- "status" -> vagrant status"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class GrpcPlugin:
    """gRPC command generator."""
    
    SYSTEM_PROMPT = """You are a gRPC expert. Generate grpcurl commands or proto snippets.

Examples:
- "list services" -> grpcurl -plaintext localhost:50051 list
- "call method" -> grpcurl -d '{"name":"world"}' localhost:50051 hello.Greeter/SayHello
- "describe" -> grpcurl -plaintext localhost:50051 describe"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
