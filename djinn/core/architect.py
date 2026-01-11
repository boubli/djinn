"""
Project Architect - Generate complex project structures.
"""
import subprocess
from typing import Dict, List, Optional
from pathlib import Path


class ProjectArchitect:
    """Generate complex project structures with AI."""
    
    ARCHITECTURES = {
        "fullstack-react-node": {
            "name": "Full Stack React + Node.js",
            "description": "React frontend with Node.js/Express backend",
            "structure": {
                "client/": ["package.json", "src/App.jsx", "src/index.js", "public/index.html"],
                "server/": ["package.json", "index.js", "routes/", "models/"],
                "": [".gitignore", "README.md", "docker-compose.yml"],
            },
            "commands": [
                "cd client && npm init -y && npm install react react-dom",
                "cd server && npm init -y && npm install express cors dotenv",
            ]
        },
        "django-react": {
            "name": "Django + React",
            "description": "Django backend with React frontend",
            "structure": {
                "backend/": ["manage.py", "requirements.txt", "config/"],
                "frontend/": ["package.json", "src/"],
                "": [".gitignore", "README.md", "docker-compose.yml"],
            },
            "commands": [
                "cd backend && python -m venv venv && pip install django djangorestframework",
                "cd frontend && npx create-react-app .",
            ]
        },
        "fastapi-vue": {
            "name": "FastAPI + Vue.js",
            "description": "FastAPI backend with Vue.js frontend",
            "structure": {
                "api/": ["main.py", "requirements.txt", "routes/", "models/"],
                "web/": ["package.json", "src/", "public/"],
                "": [".gitignore", "README.md", "docker-compose.yml"],
            },
        },
        "microservices": {
            "name": "Microservices Architecture",
            "description": "Multiple services with API gateway",
            "structure": {
                "gateway/": ["Dockerfile", "index.js"],
                "services/auth/": ["Dockerfile", "main.py"],
                "services/users/": ["Dockerfile", "main.py"],
                "services/products/": ["Dockerfile", "main.py"],
                "": ["docker-compose.yml", "README.md", ".gitignore"],
            },
        },
        "monorepo-npm": {
            "name": "NPM Monorepo",
            "description": "Monorepo with npm workspaces",
            "structure": {
                "packages/common/": ["package.json", "src/index.js"],
                "packages/api/": ["package.json", "src/index.js"],
                "packages/web/": ["package.json", "src/index.js"],
                "": ["package.json", ".gitignore", "README.md"],
            },
        },
        "cli-python": {
            "name": "Python CLI Tool",
            "description": "Command-line tool with Click",
            "structure": {
                "src/": ["__init__.py", "cli.py", "commands/"],
                "tests/": ["__init__.py", "test_cli.py"],
                "": ["pyproject.toml", "README.md", ".gitignore", "LICENSE"],
            },
        },
    }
    
    DOCKER_COMPOSE_TEMPLATE = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
    environment:
      - NODE_ENV=development
"""
    
    GITIGNORE_TEMPLATE = """# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# Build
dist/
build/
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
"""
    
    README_TEMPLATE = """# {name}

{description}

## Getting Started

### Prerequisites
- Node.js 18+ or Python 3.10+
- Docker (optional)

### Installation
```bash
# Install dependencies
npm install  # or pip install -r requirements.txt
```

### Development
```bash
# Start development server
npm run dev  # or python manage.py runserver
```

## Project Structure
```
{structure}
```

## License
MIT
"""
    
    def __init__(self, engine=None):
        self.engine = engine
    
    @classmethod
    def list_architectures(cls) -> List[Dict]:
        """List available architectures."""
        return [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in cls.ARCHITECTURES.items()
        ]
    
    @classmethod
    def get_architecture(cls, arch_id: str) -> Optional[Dict]:
        """Get architecture by ID."""
        return cls.ARCHITECTURES.get(arch_id)
    
    def create_project(self, arch_id: str, project_name: str, 
                       directory: str = None) -> bool:
        """Create a project from architecture template."""
        arch = self.ARCHITECTURES.get(arch_id)
        if not arch:
            return False
        
        base_dir = Path(directory) if directory else Path.cwd()
        project_dir = base_dir / project_name
        
        try:
            # Create directories and files
            for dir_path, files in arch["structure"].items():
                full_dir = project_dir / dir_path
                full_dir.mkdir(parents=True, exist_ok=True)
                
                for file in files:
                    if file.endswith("/"):
                        (full_dir / file).mkdir(exist_ok=True)
                    else:
                        (full_dir / file).touch()
            
            # Create common files
            (project_dir / ".gitignore").write_text(self.GITIGNORE_TEMPLATE)
            
            readme = self.README_TEMPLATE.format(
                name=project_name,
                description=arch["description"],
                structure=self._format_structure(arch["structure"])
            )
            (project_dir / "README.md").write_text(readme)
            
            # Create docker-compose if needed
            if "docker-compose.yml" in arch["structure"].get("", []):
                (project_dir / "docker-compose.yml").write_text(self.DOCKER_COMPOSE_TEMPLATE)
            
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def _format_structure(self, structure: Dict) -> str:
        """Format structure for README."""
        lines = []
        for dir_path, files in sorted(structure.items()):
            if dir_path:
                lines.append(f"├── {dir_path}")
            for file in files:
                prefix = "│   " if dir_path else ""
                lines.append(f"{prefix}├── {file}")
        return "\n".join(lines)
    
    def generate_custom(self, description: str) -> Optional[Dict]:
        """Generate a custom architecture from description using AI."""
        if not self.engine:
            return None
        
        prompt = f"""Based on this project description, generate a project structure:

"{description}"

Return a JSON object with:
- name: Project name
- description: Brief description
- structure: Dictionary of directories to files
- commands: List of setup commands

Return only valid JSON."""
        
        try:
            import json
            response = self.engine.backend.generate(prompt, "You are a software architect.")
            return json.loads(response)
        except:
            return None


class StackGenerator:
    """Generate boilerplate for specific tech stacks."""
    
    STACKS = {
        "nextjs": {
            "command": "npx create-next-app@latest . --typescript --tailwind --eslint",
            "name": "Next.js with TypeScript & Tailwind"
        },
        "vite-react": {
            "command": "npm create vite@latest . -- --template react-ts",
            "name": "Vite + React + TypeScript"
        },
        "vite-vue": {
            "command": "npm create vite@latest . -- --template vue-ts",
            "name": "Vite + Vue + TypeScript"
        },
        "fastapi": {
            "files": {
                "main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/health")
def health_check():
    return {"healthy": True}
''',
                "requirements.txt": "fastapi\nuvicorn[standard]\npydantic\n",
            },
            "name": "FastAPI Starter"
        },
        "express": {
            "files": {
                "index.js": '''const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
    res.json({ status: 'ok' });
});

app.get('/health', (req, res) => {
    res.json({ healthy: true });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
''',
                "package.json": '''{
  "name": "api",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3"
  }
}
''',
            },
            "name": "Express.js Starter"
        },
    }
    
    @classmethod
    def list_stacks(cls) -> List[Dict]:
        """List available stacks."""
        return [{"id": k, "name": v["name"]} for k, v in cls.STACKS.items()]
    
    @classmethod
    def create_stack(cls, stack_id: str, directory: str = None) -> bool:
        """Create a stack."""
        stack = cls.STACKS.get(stack_id)
        if not stack:
            return False
        
        target_dir = Path(directory) if directory else Path.cwd()
        target_dir.mkdir(parents=True, exist_ok=True)
        
        if "command" in stack:
            subprocess.run(stack["command"], shell=True, cwd=str(target_dir))
        
        if "files" in stack:
            for filename, content in stack["files"].items():
                (target_dir / filename).write_text(content)
        
        return True
