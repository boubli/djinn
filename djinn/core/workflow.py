"""
Workflow Engine - Create and run multi-step automated workflows.
"""
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class WorkflowEngine:
    """Create and execute multi-step workflows."""
    
    def __init__(self):
        self.djinn_dir = Path.home() / ".djinn"
        self.workflows_dir = self.djinn_dir / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
    
    def create(self, name: str, steps: List[Dict]) -> bool:
        """Create a new workflow.
        
        Steps format: [
            {"name": "Build", "command": "npm run build", "continue_on_error": False},
            {"name": "Test", "command": "npm test", "continue_on_error": False},
            {"name": "Deploy", "command": "npm run deploy", "continue_on_error": False},
        ]
        """
        workflow = {
            "name": name,
            "created": datetime.now().isoformat(),
            "steps": steps,
        }
        
        filepath = self.workflows_dir / f"{name}.json"
        with open(filepath, "w") as f:
            json.dump(workflow, f, indent=2)
        
        return True
    
    def get(self, name: str) -> Optional[Dict]:
        """Get a workflow by name."""
        filepath = self.workflows_dir / f"{name}.json"
        if filepath.exists():
            with open(filepath) as f:
                return json.load(f)
        return None
    
    def list_all(self) -> List[str]:
        """List all workflows."""
        return [f.stem for f in self.workflows_dir.glob("*.json")]
    
    def delete(self, name: str) -> bool:
        """Delete a workflow."""
        filepath = self.workflows_dir / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def run(self, name: str, dry_run: bool = False) -> Dict:
        """Run a workflow and return results."""
        workflow = self.get(name)
        if not workflow:
            return {"success": False, "error": "Workflow not found"}
        
        results = {
            "workflow": name,
            "started": datetime.now().isoformat(),
            "steps": [],
            "success": True,
        }
        
        for i, step in enumerate(workflow["steps"]):
            step_result = {
                "name": step["name"],
                "command": step["command"],
                "status": "pending",
            }
            
            if dry_run:
                step_result["status"] = "dry-run"
                results["steps"].append(step_result)
                continue
            
            try:
                result = subprocess.run(
                    step["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per step
                )
                
                step_result["status"] = "success" if result.returncode == 0 else "failed"
                step_result["returncode"] = result.returncode
                step_result["stdout"] = result.stdout[-500:] if result.stdout else ""
                step_result["stderr"] = result.stderr[-500:] if result.stderr else ""
                
                if result.returncode != 0:
                    results["success"] = False
                    if not step.get("continue_on_error", False):
                        step_result["status"] = "failed-stopped"
                        results["steps"].append(step_result)
                        break
                        
            except subprocess.TimeoutExpired:
                step_result["status"] = "timeout"
                results["success"] = False
                results["steps"].append(step_result)
                break
            except Exception as e:
                step_result["status"] = "error"
                step_result["error"] = str(e)
                results["success"] = False
                results["steps"].append(step_result)
                break
            
            results["steps"].append(step_result)
        
        results["completed"] = datetime.now().isoformat()
        return results
    
    def create_from_commands(self, name: str, commands: List[str]) -> bool:
        """Create a workflow from a list of commands."""
        steps = [
            {"name": f"Step {i+1}", "command": cmd, "continue_on_error": False}
            for i, cmd in enumerate(commands)
        ]
        return self.create(name, steps)


# Pre-built workflow templates
WORKFLOW_TEMPLATES = {
    "node-ci": [
        {"name": "Install", "command": "npm install", "continue_on_error": False},
        {"name": "Lint", "command": "npm run lint", "continue_on_error": True},
        {"name": "Test", "command": "npm test", "continue_on_error": False},
        {"name": "Build", "command": "npm run build", "continue_on_error": False},
    ],
    "python-ci": [
        {"name": "Install", "command": "pip install -r requirements.txt", "continue_on_error": False},
        {"name": "Lint", "command": "ruff check .", "continue_on_error": True},
        {"name": "Test", "command": "pytest", "continue_on_error": False},
    ],
    "docker-deploy": [
        {"name": "Build", "command": "docker build -t app .", "continue_on_error": False},
        {"name": "Tag", "command": "docker tag app:latest registry/app:latest", "continue_on_error": False},
        {"name": "Push", "command": "docker push registry/app:latest", "continue_on_error": False},
    ],
    "git-release": [
        {"name": "Pull", "command": "git pull origin main", "continue_on_error": False},
        {"name": "Tag", "command": "git tag -a v$(date +%Y%m%d) -m 'Release'", "continue_on_error": False},
        {"name": "Push", "command": "git push origin --tags", "continue_on_error": False},
    ],
}
