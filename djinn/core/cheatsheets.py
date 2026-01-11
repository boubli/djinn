"""
Cheatsheets - Built-in command reference for popular tools.
"""
from typing import Dict, List, Optional


class CheatsheetManager:
    """Provides built-in cheatsheets for popular CLI tools."""
    
    CHEATSHEETS = {
        "git": {
            "title": "Git Cheatsheet",
            "sections": {
                "Basics": [
                    ("git init", "Initialize a new repository"),
                    ("git clone <url>", "Clone a repository"),
                    ("git status", "Check working directory status"),
                    ("git add .", "Stage all changes"),
                    ("git commit -m '<msg>'", "Commit with message"),
                    ("git push", "Push to remote"),
                    ("git pull", "Pull from remote"),
                ],
                "Branches": [
                    ("git branch", "List branches"),
                    ("git branch <name>", "Create branch"),
                    ("git checkout <branch>", "Switch branch"),
                    ("git checkout -b <name>", "Create and switch branch"),
                    ("git merge <branch>", "Merge branch into current"),
                    ("git branch -d <name>", "Delete branch"),
                ],
                "Undo": [
                    ("git reset --soft HEAD~1", "Undo last commit, keep changes"),
                    ("git reset --hard HEAD~1", "Undo last commit, discard changes"),
                    ("git checkout -- <file>", "Discard file changes"),
                    ("git revert <commit>", "Create commit that undoes another"),
                    ("git stash", "Stash changes temporarily"),
                    ("git stash pop", "Apply stashed changes"),
                ],
                "History": [
                    ("git log --oneline", "Compact history"),
                    ("git log --graph", "Visual branch history"),
                    ("git diff", "Show unstaged changes"),
                    ("git diff --staged", "Show staged changes"),
                    ("git blame <file>", "Show who changed each line"),
                ],
            }
        },
        "docker": {
            "title": "Docker Cheatsheet",
            "sections": {
                "Containers": [
                    ("docker ps", "List running containers"),
                    ("docker ps -a", "List all containers"),
                    ("docker run <image>", "Run a container"),
                    ("docker run -d -p 8080:80 <image>", "Run detached with port"),
                    ("docker stop <id>", "Stop container"),
                    ("docker rm <id>", "Remove container"),
                    ("docker exec -it <id> bash", "Shell into container"),
                    ("docker logs <id>", "View container logs"),
                ],
                "Images": [
                    ("docker images", "List images"),
                    ("docker pull <image>", "Pull image from registry"),
                    ("docker build -t <name> .", "Build image from Dockerfile"),
                    ("docker rmi <image>", "Remove image"),
                    ("docker tag <src> <dest>", "Tag an image"),
                    ("docker push <image>", "Push to registry"),
                ],
                "Cleanup": [
                    ("docker system prune", "Remove unused data"),
                    ("docker container prune", "Remove stopped containers"),
                    ("docker image prune", "Remove dangling images"),
                    ("docker volume prune", "Remove unused volumes"),
                ],
                "Compose": [
                    ("docker-compose up", "Start services"),
                    ("docker-compose up -d", "Start in background"),
                    ("docker-compose down", "Stop and remove"),
                    ("docker-compose logs -f", "Follow logs"),
                    ("docker-compose ps", "List services"),
                ],
            }
        },
        "kubernetes": {
            "title": "Kubernetes Cheatsheet",
            "sections": {
                "Basics": [
                    ("kubectl get pods", "List pods"),
                    ("kubectl get pods -A", "List all pods, all namespaces"),
                    ("kubectl get services", "List services"),
                    ("kubectl get deployments", "List deployments"),
                    ("kubectl get nodes", "List nodes"),
                    ("kubectl describe pod <name>", "Pod details"),
                ],
                "Create/Apply": [
                    ("kubectl apply -f <file>.yaml", "Apply configuration"),
                    ("kubectl create deployment <name> --image=<img>", "Create deployment"),
                    ("kubectl expose deployment <name> --port=80", "Expose as service"),
                    ("kubectl delete -f <file>.yaml", "Delete from file"),
                ],
                "Debug": [
                    ("kubectl logs <pod>", "View pod logs"),
                    ("kubectl logs -f <pod>", "Follow logs"),
                    ("kubectl exec -it <pod> -- bash", "Shell into pod"),
                    ("kubectl port-forward <pod> 8080:80", "Port forward"),
                    ("kubectl top pods", "Resource usage"),
                ],
                "Scale": [
                    ("kubectl scale deployment <name> --replicas=3", "Scale replicas"),
                    ("kubectl rollout status deployment/<name>", "Rollout status"),
                    ("kubectl rollout undo deployment/<name>", "Rollback"),
                ],
            }
        },
        "linux": {
            "title": "Linux Cheatsheet",
            "sections": {
                "Files": [
                    ("ls -la", "List all with details"),
                    ("cd <dir>", "Change directory"),
                    ("pwd", "Print working directory"),
                    ("cp <src> <dest>", "Copy file"),
                    ("mv <src> <dest>", "Move/rename"),
                    ("rm <file>", "Remove file"),
                    ("rm -rf <dir>", "Remove directory recursively"),
                    ("mkdir -p <path>", "Create directories"),
                    ("touch <file>", "Create empty file"),
                ],
                "Search": [
                    ("find . -name '*.py'", "Find files by name"),
                    ("find . -size +100M", "Find large files"),
                    ("grep -r 'pattern' .", "Search in files"),
                    ("grep -l 'pattern' .", "List files containing pattern"),
                    ("locate <file>", "Quick file search"),
                ],
                "System": [
                    ("df -h", "Disk usage"),
                    ("du -sh *", "Directory sizes"),
                    ("free -h", "Memory usage"),
                    ("top", "Process monitor"),
                    ("htop", "Better process monitor"),
                    ("ps aux", "List processes"),
                    ("kill <pid>", "Kill process"),
                    ("kill -9 <pid>", "Force kill"),
                ],
                "Network": [
                    ("curl <url>", "HTTP request"),
                    ("wget <url>", "Download file"),
                    ("ping <host>", "Check connectivity"),
                    ("netstat -tulpn", "Open ports"),
                    ("ss -tulpn", "Socket stats"),
                    ("ip addr", "IP addresses"),
                ],
            }
        },
        "npm": {
            "title": "NPM Cheatsheet",
            "sections": {
                "Basics": [
                    ("npm init", "Create package.json"),
                    ("npm install", "Install dependencies"),
                    ("npm install <pkg>", "Install package"),
                    ("npm install -D <pkg>", "Install as dev dependency"),
                    ("npm install -g <pkg>", "Install globally"),
                    ("npm uninstall <pkg>", "Remove package"),
                ],
                "Scripts": [
                    ("npm run <script>", "Run script"),
                    ("npm start", "Run start script"),
                    ("npm test", "Run tests"),
                    ("npm run build", "Run build"),
                ],
                "Info": [
                    ("npm list", "List installed packages"),
                    ("npm outdated", "Check for updates"),
                    ("npm update", "Update packages"),
                    ("npm audit", "Security audit"),
                    ("npm audit fix", "Fix vulnerabilities"),
                ],
                "Publish": [
                    ("npm login", "Login to npm"),
                    ("npm publish", "Publish package"),
                    ("npm version patch", "Bump patch version"),
                    ("npm version minor", "Bump minor version"),
                ],
            }
        },
        "python": {
            "title": "Python Cheatsheet",
            "sections": {
                "Virtual Environments": [
                    ("python -m venv venv", "Create venv"),
                    ("source venv/bin/activate", "Activate (Linux/Mac)"),
                    ("venv\\Scripts\\activate", "Activate (Windows)"),
                    ("deactivate", "Deactivate venv"),
                ],
                "Pip": [
                    ("pip install <pkg>", "Install package"),
                    ("pip install -r requirements.txt", "Install from file"),
                    ("pip freeze > requirements.txt", "Export dependencies"),
                    ("pip list", "List packages"),
                    ("pip show <pkg>", "Package info"),
                    ("pip uninstall <pkg>", "Remove package"),
                ],
                "Run": [
                    ("python <file>.py", "Run script"),
                    ("python -m <module>", "Run module"),
                    ("python -c '<code>'", "Run inline code"),
                    ("python -i <file>.py", "Run then interactive"),
                ],
                "Tools": [
                    ("pytest", "Run tests"),
                    ("black .", "Format code"),
                    ("ruff check .", "Lint code"),
                    ("mypy .", "Type checking"),
                    ("pip-compile", "Lock dependencies"),
                ],
            }
        },
        "aws": {
            "title": "AWS CLI Cheatsheet",
            "sections": {
                "S3": [
                    ("aws s3 ls", "List buckets"),
                    ("aws s3 ls s3://<bucket>", "List bucket contents"),
                    ("aws s3 cp <file> s3://<bucket>/", "Upload file"),
                    ("aws s3 sync . s3://<bucket>/", "Sync directory"),
                    ("aws s3 rm s3://<bucket>/<key>", "Delete object"),
                ],
                "EC2": [
                    ("aws ec2 describe-instances", "List instances"),
                    ("aws ec2 start-instances --instance-ids <id>", "Start instance"),
                    ("aws ec2 stop-instances --instance-ids <id>", "Stop instance"),
                    ("aws ec2 describe-security-groups", "List security groups"),
                ],
                "Lambda": [
                    ("aws lambda list-functions", "List functions"),
                    ("aws lambda invoke --function-name <name> out.json", "Invoke function"),
                    ("aws logs tail /aws/lambda/<fn> --follow", "Tail logs"),
                ],
                "ECS": [
                    ("aws ecs list-clusters", "List clusters"),
                    ("aws ecs list-services --cluster <name>", "List services"),
                    ("aws ecs update-service --cluster <c> --service <s> --force-new-deployment", "Force deploy"),
                ],
            }
        },
        "postgres": {
            "title": "PostgreSQL Cheatsheet",
            "sections": {
                "Connection": [
                    ("psql -U <user> -d <db>", "Connect to database"),
                    ("psql -h <host> -U <user> -d <db>", "Connect to remote"),
                    ("\\q", "Quit psql"),
                    ("\\c <db>", "Switch database"),
                ],
                "Info": [
                    ("\\l", "List databases"),
                    ("\\dt", "List tables"),
                    ("\\d <table>", "Describe table"),
                    ("\\du", "List users"),
                    ("\\dn", "List schemas"),
                ],
                "Queries": [
                    ("SELECT * FROM <table> LIMIT 10;", "Select rows"),
                    ("\\x", "Toggle expanded display"),
                    ("EXPLAIN ANALYZE <query>;", "Query plan"),
                    ("\\timing", "Toggle timing"),
                ],
                "Admin": [
                    ("CREATE DATABASE <name>;", "Create database"),
                    ("DROP DATABASE <name>;", "Drop database"),
                    ("pg_dump <db> > backup.sql", "Backup database"),
                    ("psql <db> < backup.sql", "Restore database"),
                ],
            }
        },
    }
    
    @classmethod
    def list_available(cls) -> List[str]:
        """List available cheatsheets."""
        return list(cls.CHEATSHEETS.keys())
    
    @classmethod
    def get(cls, name: str) -> Optional[Dict]:
        """Get a cheatsheet by name."""
        return cls.CHEATSHEETS.get(name.lower())
    
    @classmethod
    def search(cls, query: str) -> List[tuple]:
        """Search across all cheatsheets."""
        results = []
        query_lower = query.lower()
        
        for sheet_name, sheet in cls.CHEATSHEETS.items():
            for section, commands in sheet["sections"].items():
                for cmd, desc in commands:
                    if query_lower in cmd.lower() or query_lower in desc.lower():
                        results.append((sheet_name, section, cmd, desc))
        
        return results[:20]  # Limit results
