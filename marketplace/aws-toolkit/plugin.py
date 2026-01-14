"""
AWS Toolkit Plugin for DJINN
S3, EC2, Lambda management shortcuts.
"""
import click
from rich.console import Console
from rich.table import Table
import os

console = Console()

# Plugin Metadata
PLUGIN_NAME = "aws-toolkit"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "AWS shortcuts: S3, EC2, Lambda."
PLUGIN_CATEGORY = "cloud"


def get_boto3_client(service):
    """Get boto3 client."""
    try:
        import boto3
        return boto3.client(service)
    except ImportError:
        console.print("[error]boto3 not installed. Run: pip install boto3[/error]")
        return None
    except Exception as e:
        console.print(f"[error]AWS Error: {e}[/error]")
        return None


@click.group()
def aws():
    """AWS toolkit commands."""
    pass


# ========== S3 Commands ==========

@aws.group()
def s3():
    """S3 commands."""
    pass


@s3.command(name="ls")
@click.argument("bucket", required=False)
@click.option("--prefix", default="", help="Key prefix")
def s3_list(bucket, prefix):
    """List S3 buckets or objects."""
    client = get_boto3_client("s3")
    if not client:
        return
    
    if not bucket:
        # List buckets
        response = client.list_buckets()
        
        console.print("\n[bold cyan]📦 S3 Buckets[/bold cyan]\n")
        
        table = Table()
        table.add_column("Bucket", style="cyan")
        table.add_column("Created")
        
        for b in response["Buckets"]:
            table.add_row(b["Name"], str(b["CreationDate"].date()))
        
        console.print(table)
    else:
        # List objects
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=50)
        
        console.print(f"\n[bold cyan]📦 Objects in {bucket}[/bold cyan]\n")
        
        table = Table()
        table.add_column("Key", style="cyan")
        table.add_column("Size")
        table.add_column("Modified")
        
        for obj in response.get("Contents", []):
            size = f"{obj['Size'] / 1024:.1f} KB"
            table.add_row(obj["Key"], size, str(obj["LastModified"].date()))
        
        console.print(table)


@s3.command(name="cp")
@click.argument("source")
@click.argument("destination")
def s3_copy(source, destination):
    """Copy files to/from S3."""
    client = get_boto3_client("s3")
    if not client:
        return
    
    try:
        if source.startswith("s3://"):
            # Download from S3
            bucket, key = source[5:].split("/", 1)
            client.download_file(bucket, key, destination)
            console.print(f"[success]✓ Downloaded to {destination}[/success]")
        elif destination.startswith("s3://"):
            # Upload to S3
            bucket, key = destination[5:].split("/", 1)
            client.upload_file(source, bucket, key)
            console.print(f"[success]✓ Uploaded to {destination}[/success]")
        else:
            console.print("[error]Source or destination must be an S3 URI (s3://...)[/error]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


# ========== EC2 Commands ==========

@aws.group()
def ec2():
    """EC2 commands."""
    pass


@ec2.command(name="ls")
def ec2_list():
    """List EC2 instances."""
    client = get_boto3_client("ec2")
    if not client:
        return
    
    response = client.describe_instances()
    
    console.print("\n[bold cyan]🖥️  EC2 Instances[/bold cyan]\n")
    
    table = Table()
    table.add_column("Instance ID", style="cyan")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("State")
    table.add_column("IP")
    
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            name = next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "-")
            state = instance["State"]["Name"]
            state_color = "green" if state == "running" else "red" if state == "stopped" else "yellow"
            
            table.add_row(
                instance["InstanceId"],
                name,
                instance["InstanceType"],
                f"[{state_color}]{state}[/{state_color}]",
                instance.get("PublicIpAddress", "-")
            )
    
    console.print(table)


@ec2.command(name="start")
@click.argument("instance_id")
def ec2_start(instance_id):
    """Start an EC2 instance."""
    client = get_boto3_client("ec2")
    if not client:
        return
    
    try:
        client.start_instances(InstanceIds=[instance_id])
        console.print(f"[success]✓ Starting instance {instance_id}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@ec2.command(name="stop")
@click.argument("instance_id")
def ec2_stop(instance_id):
    """Stop an EC2 instance."""
    client = get_boto3_client("ec2")
    if not client:
        return
    
    try:
        client.stop_instances(InstanceIds=[instance_id])
        console.print(f"[success]✓ Stopping instance {instance_id}[/success]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


# ========== Lambda Commands ==========

@aws.group()
def lambdafn():
    """Lambda commands."""
    pass


@lambdafn.command(name="ls")
def lambda_list():
    """List Lambda functions."""
    client = get_boto3_client("lambda")
    if not client:
        return
    
    response = client.list_functions()
    
    console.print("\n[bold cyan]λ Lambda Functions[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Runtime")
    table.add_column("Memory")
    table.add_column("Timeout")
    
    for fn in response["Functions"]:
        table.add_row(
            fn["FunctionName"],
            fn.get("Runtime", "-"),
            f"{fn['MemorySize']} MB",
            f"{fn['Timeout']}s"
        )
    
    console.print(table)


@lambdafn.command(name="invoke")
@click.argument("function_name")
@click.option("--payload", default="{}", help="JSON payload")
def lambda_invoke(function_name, payload):
    """Invoke a Lambda function."""
    client = get_boto3_client("lambda")
    if not client:
        return
    
    import json
    
    try:
        response = client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=payload.encode()
        )
        
        result = json.loads(response["Payload"].read())
        console.print(f"\n[success]Response:[/success]")
        console.print_json(data=result)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


# Export the main command
main = aws

if __name__ == "__main__":
    aws()
