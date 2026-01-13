"""
Compose Generator - Generate Docker Compose files from natural language.
"""
from typing import Optional


class ComposeGenerator:
    """Generate Docker Compose files from descriptions."""
    
    SYSTEM_PROMPT = """You are a Docker Compose expert. Generate complete, production-ready docker-compose.yml files.

Rules:
- Use version "3.8" or higher
- Include proper networking
- Add health checks where appropriate
- Use environment variables for secrets
- Add volume mounts for persistence
- Include restart policies
- Output ONLY valid YAML, no explanations

Common stacks you know well:
- LAMP/LEMP (Linux, Apache/Nginx, MySQL, PHP)
- MERN (MongoDB, Express, React, Node)
- Django + PostgreSQL + Redis
- WordPress + MySQL
- Node.js + MongoDB + Redis
- Python FastAPI + PostgreSQL
- Grafana + Prometheus + Node Exporter
"""

    TEMPLATES = {
        "nginx": """
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
    restart: unless-stopped
""",
        "postgres": r"""
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: \${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-secret}
      POSTGRES_DB: \${POSTGRES_DB:-app}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
""",
        "redis": """
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

volumes:
  redis_data:
""",
        "mongodb": r"""
services:
  mongo:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: \${MONGO_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: \${MONGO_PASSWORD:-secret}
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped

volumes:
  mongo_data:
""",
        "wordpress": r"""
services:
  wordpress:
    image: wordpress:latest
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: \${DB_PASSWORD:-secret}
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress_data:/var/www/html
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: \${DB_ROOT_PASSWORD:-rootsecret}
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: \${DB_PASSWORD:-secret}
    volumes:
      - db_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  wordpress_data:
  db_data:
""",
        "mern": """
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/app
      - NODE_ENV=development
    depends_on:
      - mongo

  mongo:
    image: mongo:7
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo_data:
""",
        "monitoring": r"""
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
""",
    }
    
    def __init__(self, engine=None):
        self.engine = engine
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a pre-built template."""
        return self.TEMPLATES.get(name.lower())
    
    def list_templates(self) -> list:
        """List available templates."""
        return list(self.TEMPLATES.keys())
    
    def generate(self, description: str) -> Optional[str]:
        """Generate compose file from description using AI."""
        if not self.engine:
            return None
        
        prompt = f"Generate a docker-compose.yml for: {description}"
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
    
    def combine_templates(self, templates: list) -> str:
        """Combine multiple templates into one compose file."""
        services = []
        volumes = []
        
        header = "version: '3.8'\n\nservices:"
        
        for tmpl_name in templates:
            tmpl = self.TEMPLATES.get(tmpl_name.lower())
            if tmpl:
                # Extract services and volumes (simple parsing)
                services.append(tmpl.strip())
        
        return header + "\n" + "\n".join(services)
