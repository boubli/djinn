"""
Kubernetes Plugin for DJINN
Enhanced kubectl wrapper with AI hints.
"""
import click
from rich.console import Console
from rich.table import Table
import subprocess
import json

console = Console()

PLUGIN_NAME = "kubernetes"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Enhanced Kubernetes management."


def run_kubectl(args, capture=True):
    """Run kubectl command."""
    cmd = ["kubectl"] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            subprocess.run(cmd)
            return True, "", ""
    except FileNotFoundError:
        return False, "", "kubectl not installed"


@click.group()
def k8s():
    """Kubernetes commands."""
    pass


@k8s.command(name="pods")
@click.option("-n", "--namespace", default="default")
@click.option("-A", "--all-namespaces", is_flag=True)
def list_pods(namespace, all_namespaces):
    """List pods."""
    args = ["get", "pods", "-o", "json"]
    if all_namespaces:
        args.append("-A")
    else:
        args.extend(["-n", namespace])
    
    success, stdout, stderr = run_kubectl(args)
    
    if not success:
        console.print(f"[error]{stderr}[/error]")
        return
    
    data = json.loads(stdout)
    
    console.print(f"\n[bold cyan]☸️  Pods[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Ready")
    table.add_column("Status")
    table.add_column("Restarts")
    table.add_column("Age")
    if all_namespaces:
        table.add_column("Namespace")
    
    for pod in data.get("items", []):
        name = pod["metadata"]["name"]
        ns = pod["metadata"]["namespace"]
        
        containers = pod["status"].get("containerStatuses", [])
        ready = sum(1 for c in containers if c.get("ready"))
        total = len(containers)
        
        status = pod["status"]["phase"]
        status_color = "green" if status == "Running" else "yellow" if status == "Pending" else "red"
        
        restarts = sum(c.get("restartCount", 0) for c in containers)
        
        # Calculate age
        from datetime import datetime, timezone
        created = pod["metadata"]["creationTimestamp"]
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - created_dt
        age_str = f"{age.days}d" if age.days > 0 else f"{age.seconds // 3600}h"
        
        row = [name, f"{ready}/{total}", f"[{status_color}]{status}[/{status_color}]", str(restarts), age_str]
        if all_namespaces:
            row.append(ns)
        
        table.add_row(*row)
    
    console.print(table)


@k8s.command(name="logs")
@click.argument("pod")
@click.option("-n", "--namespace", default="default")
@click.option("-c", "--container")
@click.option("-f", "--follow", is_flag=True)
@click.option("--tail", default=100, type=int)
def pod_logs(pod, namespace, container, follow, tail):
    """Get pod logs."""
    args = ["logs", pod, "-n", namespace, f"--tail={tail}"]
    if container:
        args.extend(["-c", container])
    if follow:
        args.append("-f")
    
    run_kubectl(args, capture=False)


@k8s.command(name="exec")
@click.argument("pod")
@click.argument("command", nargs=-1)
@click.option("-n", "--namespace", default="default")
@click.option("-c", "--container")
def exec_pod(pod, command, namespace, container):
    """Execute command in pod."""
    args = ["exec", "-it", pod, "-n", namespace]
    if container:
        args.extend(["-c", container])
    args.append("--")
    args.extend(command if command else ["sh"])
    
    run_kubectl(args, capture=False)


@k8s.command(name="describe")
@click.argument("resource")
@click.argument("name")
@click.option("-n", "--namespace", default="default")
def describe_resource(resource, name, namespace):
    """Describe a resource."""
    run_kubectl(["describe", resource, name, "-n", namespace], capture=False)


@k8s.command(name="apply")
@click.argument("file_path")
@click.option("-n", "--namespace")
def apply_manifest(file_path, namespace):
    """Apply a manifest."""
    args = ["apply", "-f", file_path]
    if namespace:
        args.extend(["-n", namespace])
    
    success, stdout, stderr = run_kubectl(args)
    
    if success:
        console.print(f"[success]{stdout}[/success]")
    else:
        console.print(f"[error]{stderr}[/error]")


@k8s.command(name="delete")
@click.argument("resource")
@click.argument("name")
@click.option("-n", "--namespace", default="default")
@click.option("--force", is_flag=True)
def delete_resource(resource, name, namespace, force):
    """Delete a resource."""
    args = ["delete", resource, name, "-n", namespace]
    if force:
        args.extend(["--force", "--grace-period=0"])
    
    success, stdout, stderr = run_kubectl(args)
    
    if success:
        console.print(f"[success]{stdout}[/success]")
    else:
        console.print(f"[error]{stderr}[/error]")


@k8s.command(name="services")
@click.option("-n", "--namespace", default="default")
@click.option("-A", "--all-namespaces", is_flag=True)
def list_services(namespace, all_namespaces):
    """List services."""
    args = ["get", "services", "-o", "json"]
    if all_namespaces:
        args.append("-A")
    else:
        args.extend(["-n", namespace])
    
    success, stdout, stderr = run_kubectl(args)
    
    if not success:
        console.print(f"[error]{stderr}[/error]")
        return
    
    data = json.loads(stdout)
    
    console.print(f"\n[bold cyan]🔌 Services[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Cluster IP")
    table.add_column("External IP")
    table.add_column("Ports")
    
    for svc in data.get("items", []):
        name = svc["metadata"]["name"]
        svc_type = svc["spec"]["type"]
        cluster_ip = svc["spec"].get("clusterIP", "-")
        external_ips = svc["status"].get("loadBalancer", {}).get("ingress", [])
        external_ip = external_ips[0].get("ip", "-") if external_ips else "-"
        
        ports = []
        for p in svc["spec"].get("ports", []):
            ports.append(f"{p['port']}:{p.get('nodePort', p['port'])}/{p['protocol']}")
        
        table.add_row(name, svc_type, cluster_ip, external_ip, ", ".join(ports))
    
    console.print(table)


@k8s.command(name="deployments")
@click.option("-n", "--namespace", default="default")
def list_deployments(namespace):
    """List deployments."""
    args = ["get", "deployments", "-n", namespace, "-o", "json"]
    
    success, stdout, stderr = run_kubectl(args)
    
    if not success:
        console.print(f"[error]{stderr}[/error]")
        return
    
    data = json.loads(stdout)
    
    console.print(f"\n[bold cyan]🚀 Deployments[/bold cyan]\n")
    
    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Ready")
    table.add_column("Up-to-date")
    table.add_column("Available")
    
    for dep in data.get("items", []):
        name = dep["metadata"]["name"]
        replicas = dep["spec"].get("replicas", 0)
        ready = dep["status"].get("readyReplicas", 0)
        updated = dep["status"].get("updatedReplicas", 0)
        available = dep["status"].get("availableReplicas", 0)
        
        ready_color = "green" if ready == replicas else "yellow"
        
        table.add_row(name, f"[{ready_color}]{ready}/{replicas}[/{ready_color}]", str(updated), str(available))
    
    console.print(table)


@k8s.command(name="scale")
@click.argument("deployment")
@click.argument("replicas", type=int)
@click.option("-n", "--namespace", default="default")
def scale_deployment(deployment, replicas, namespace):
    """Scale a deployment."""
    args = ["scale", "deployment", deployment, f"--replicas={replicas}", "-n", namespace]
    
    success, stdout, stderr = run_kubectl(args)
    
    if success:
        console.print(f"[success]✓ Scaled {deployment} to {replicas} replicas[/success]")
    else:
        console.print(f"[error]{stderr}[/error]")


@k8s.command(name="rollout")
@click.argument("action", type=click.Choice(["status", "restart", "undo", "history"]))
@click.argument("deployment")
@click.option("-n", "--namespace", default="default")
def rollout(action, deployment, namespace):
    """Manage deployment rollouts."""
    args = ["rollout", action, f"deployment/{deployment}", "-n", namespace]
    run_kubectl(args, capture=False)


@k8s.command(name="port-forward")
@click.argument("pod")
@click.argument("ports")
@click.option("-n", "--namespace", default="default")
def port_forward(pod, ports, namespace):
    """Forward ports to a pod."""
    console.print(f"[bold cyan]🔀 Forwarding {ports}...[/bold cyan]")
    run_kubectl(["port-forward", pod, ports, "-n", namespace], capture=False)


main = k8s

if __name__ == "__main__":
    k8s()
