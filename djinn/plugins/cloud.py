"""
Cloud Plugins - Cloud provider command generators.
"""


class AWSPlugin:
    """AWS CLI commands."""
    
    SYSTEM_PROMPT = """You are an AWS expert. Generate AWS CLI commands.
Output only the command."""
    
    TEMPLATES = {
        # S3
        "s3_ls": "aws s3 ls",
        "s3_ls_bucket": "aws s3 ls s3://{bucket}",
        "s3_cp": "aws s3 cp {source} s3://{bucket}/{key}",
        "s3_sync": "aws s3 sync {directory} s3://{bucket}",
        "s3_rm": "aws s3 rm s3://{bucket}/{key}",
        "s3_presign": "aws s3 presign s3://{bucket}/{key} --expires-in {seconds}",
        
        # EC2
        "ec2_list": "aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]' --output table",
        "ec2_start": "aws ec2 start-instances --instance-ids {instance_id}",
        "ec2_stop": "aws ec2 stop-instances --instance-ids {instance_id}",
        "ec2_terminate": "aws ec2 terminate-instances --instance-ids {instance_id}",
        
        # Lambda
        "lambda_list": "aws lambda list-functions",
        "lambda_invoke": "aws lambda invoke --function-name {function} output.json",
        "lambda_logs": "aws logs tail /aws/lambda/{function} --follow",
        
        # ECS
        "ecs_clusters": "aws ecs list-clusters",
        "ecs_services": "aws ecs list-services --cluster {cluster}",
        "ecs_deploy": "aws ecs update-service --cluster {cluster} --service {service} --force-new-deployment",
        
        # IAM
        "iam_users": "aws iam list-users",
        "iam_roles": "aws iam list-roles",
        "sts_whoami": "aws sts get-caller-identity",
        
        # CloudFormation
        "cf_stacks": "aws cloudformation list-stacks",
        "cf_deploy": "aws cloudformation deploy --template-file {template} --stack-name {name}",
        "cf_delete": "aws cloudformation delete-stack --stack-name {name}",
        
        # RDS
        "rds_instances": "aws rds describe-db-instances",
        "rds_snapshot": "aws rds create-db-snapshot --db-instance-identifier {instance} --db-snapshot-identifier {snapshot}",
        
        # SQS
        "sqs_list": "aws sqs list-queues",
        "sqs_send": "aws sqs send-message --queue-url {url} --message-body '{message}'",
        
        # Secrets Manager
        "secrets_list": "aws secretsmanager list-secrets",
        "secrets_get": "aws secretsmanager get-secret-value --secret-id {secret} --query SecretString --output text",
    }


class GCPPlugin:
    """Google Cloud Platform commands."""
    
    SYSTEM_PROMPT = """You are a GCP expert. Generate gcloud CLI commands.
Output only the command."""
    
    TEMPLATES = {
        # Compute
        "compute_list": "gcloud compute instances list",
        "compute_start": "gcloud compute instances start {instance} --zone={zone}",
        "compute_stop": "gcloud compute instances stop {instance} --zone={zone}",
        "compute_ssh": "gcloud compute ssh {instance} --zone={zone}",
        
        # Storage
        "gsutil_ls": "gsutil ls",
        "gsutil_cp": "gsutil cp {source} gs://{bucket}/{path}",
        "gsutil_sync": "gsutil rsync -r {directory} gs://{bucket}",
        
        # Cloud Run
        "run_list": "gcloud run services list",
        "run_deploy": "gcloud run deploy {service} --image={image} --platform=managed",
        "run_logs": "gcloud run services logs read {service}",
        
        # GKE
        "gke_clusters": "gcloud container clusters list",
        "gke_credentials": "gcloud container clusters get-credentials {cluster} --zone={zone}",
        
        # Cloud Functions
        "functions_list": "gcloud functions list",
        "functions_deploy": "gcloud functions deploy {name} --runtime={runtime} --trigger-http",
        "functions_logs": "gcloud functions logs read {name}",
        
        # IAM
        "projects": "gcloud projects list",
        "config_list": "gcloud config list",
        "auth_list": "gcloud auth list",
    }


class AzurePlugin:
    """Azure CLI commands."""
    
    SYSTEM_PROMPT = """You are an Azure expert. Generate az CLI commands.
Output only the command."""
    
    TEMPLATES = {
        # VMs
        "vm_list": "az vm list --output table",
        "vm_start": "az vm start --resource-group {rg} --name {name}",
        "vm_stop": "az vm stop --resource-group {rg} --name {name}",
        
        # Storage
        "storage_list": "az storage account list --output table",
        "blob_list": "az storage blob list --container-name {container} --account-name {account}",
        "blob_upload": "az storage blob upload --container-name {container} --name {name} --file {file}",
        
        # AKS
        "aks_list": "az aks list --output table",
        "aks_credentials": "az aks get-credentials --resource-group {rg} --name {name}",
        
        # Functions
        "func_list": "az functionapp list --output table",
        "func_deploy": "az functionapp deployment source config-zip --resource-group {rg} --name {name} --src {zip}",
        
        # Resource Groups
        "rg_list": "az group list --output table",
        "rg_create": "az group create --name {name} --location {location}",
        
        # Account
        "account_show": "az account show",
        "account_list": "az account list --output table",
    }


class DigitalOceanPlugin:
    """DigitalOcean CLI commands."""
    
    TEMPLATES = {
        "droplets": "doctl compute droplet list",
        "droplet_create": "doctl compute droplet create {name} --region {region} --image {image} --size {size}",
        "droplet_delete": "doctl compute droplet delete {id}",
        "ssh": "doctl compute ssh {id}",
        "databases": "doctl databases list",
        "apps": "doctl apps list",
        "spaces": "doctl spaces list",
    }


class HerokuPlugin:
    """Heroku CLI commands."""
    
    TEMPLATES = {
        "apps": "heroku apps",
        "logs": "heroku logs --tail --app {app}",
        "ps": "heroku ps --app {app}",
        "scale": "heroku ps:scale web={count} --app {app}",
        "config": "heroku config --app {app}",
        "config_set": "heroku config:set {key}={value} --app {app}",
        "run": "heroku run {command} --app {app}",
        "deploy": "git push heroku main",
        "restart": "heroku restart --app {app}",
    }


class VercelPlugin:
    """Vercel CLI commands."""
    
    TEMPLATES = {
        "deploy": "vercel",
        "deploy_prod": "vercel --prod",
        "list": "vercel ls",
        "logs": "vercel logs {url}",
        "env_add": "vercel env add {name}",
        "env_ls": "vercel env ls",
        "domains": "vercel domains ls",
    }


class NetlifyPlugin:
    """Netlify CLI commands."""
    
    TEMPLATES = {
        "deploy": "netlify deploy",
        "deploy_prod": "netlify deploy --prod",
        "status": "netlify status",
        "open": "netlify open",
        "dev": "netlify dev",
        "functions": "netlify functions:list",
        "logs": "netlify logs",
    }
