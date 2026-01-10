"""
Cloud CLI Plugins - AWS, GCP, Azure, Kubernetes.
"""
from typing import Optional


class AWSPlugin:
    """AWS CLI command generator."""
    
    SYSTEM_PROMPT = """You are an AWS CLI expert. Generate AWS CLI commands.

Rules:
- Output ONLY the aws command, no explanations
- Use proper aws cli syntax
- Include necessary flags like --region when appropriate
- Be security-conscious

Examples:
- "list buckets" -> aws s3 ls
- "deploy lambda" -> aws lambda update-function-code --function-name NAME --zip-file FILE
- "check ec2" -> aws ec2 describe-instances"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class GCPPlugin:
    """GCP gcloud command generator."""
    
    SYSTEM_PROMPT = """You are a GCP gcloud expert. Generate gcloud commands.

Rules:
- Output ONLY the gcloud command, no explanations
- Use proper gcloud syntax
- Include project ID when appropriate
- Be security-conscious

Examples:
- "list instances" -> gcloud compute instances list
- "deploy function" -> gcloud functions deploy NAME --runtime python39 --trigger-http
- "list buckets" -> gsutil ls"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class AzurePlugin:
    """Azure CLI command generator."""
    
    SYSTEM_PROMPT = """You are an Azure CLI expert. Generate az commands.

Rules:
- Output ONLY the az command, no explanations
- Use proper az cli syntax
- Include resource group when appropriate

Examples:
- "list vms" -> az vm list
- "create storage" -> az storage account create --name NAME --resource-group GROUP
- "deploy app" -> az webapp up --name NAME"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class K8sPlugin:
    """Kubernetes kubectl command generator."""
    
    SYSTEM_PROMPT = """You are a Kubernetes kubectl expert. Generate kubectl commands.

Rules:
- Output ONLY the kubectl command, no explanations
- Use proper kubectl syntax
- Include namespace when relevant

Examples:
- "list pods" -> kubectl get pods
- "scale deployment" -> kubectl scale deployment NAME --replicas=3
- "view logs" -> kubectl logs POD_NAME -f
- "exec into pod" -> kubectl exec -it POD_NAME -- /bin/bash"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class TerraformPlugin:
    """Terraform command generator."""
    
    SYSTEM_PROMPT = """You are a Terraform expert. Generate terraform commands or HCL snippets.

Rules:
- Output the terraform command or HCL code
- Use proper terraform workflow (init, plan, apply)

Examples:
- "initialize" -> terraform init
- "preview changes" -> terraform plan
- "apply changes" -> terraform apply -auto-approve
- "create ec2" -> (HCL for aws_instance resource)"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)


class HelmPlugin:
    """Helm chart command generator."""
    
    SYSTEM_PROMPT = """You are a Helm expert. Generate helm commands.

Rules:
- Output ONLY the helm command, no explanations
- Use proper helm syntax

Examples:
- "install nginx" -> helm install nginx bitnami/nginx
- "list releases" -> helm list
- "upgrade chart" -> helm upgrade NAME CHART"""

    def __init__(self, engine):
        self.engine = engine
    
    def generate(self, prompt: str) -> Optional[str]:
        return self.engine.backend.generate(prompt, self.SYSTEM_PROMPT)
