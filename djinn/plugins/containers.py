"""
Container Plugins - Docker and Kubernetes command generators.
"""


class DockerPlugin:
    """Docker commands."""
    
    SYSTEM_PROMPT = """You are a Docker expert. Generate docker commands.
Output only the command."""
    
    TEMPLATES = {
        # Container lifecycle
        "run": "docker run -d --name {name} -p {host_port}:{container_port} {image}",
        "run_it": "docker run -it --rm {image} {command}",
        "start": "docker start {container}",
        "stop": "docker stop {container}",
        "restart": "docker restart {container}",
        "rm": "docker rm {container}",
        "rm_force": "docker rm -f {container}",
        
        # Container info
        "ps": "docker ps",
        "ps_all": "docker ps -a",
        "logs": "docker logs {container}",
        "logs_follow": "docker logs -f {container}",
        "inspect": "docker inspect {container}",
        "top": "docker top {container}",
        "stats": "docker stats",
        
        # Execute
        "exec": "docker exec -it {container} {command}",
        "exec_bash": "docker exec -it {container} /bin/bash",
        "exec_sh": "docker exec -it {container} /bin/sh",
        
        # Images
        "images": "docker images",
        "pull": "docker pull {image}",
        "push": "docker push {image}",
        "build": "docker build -t {name}:{tag} .",
        "tag": "docker tag {source} {target}",
        "rmi": "docker rmi {image}",
        "history": "docker history {image}",
        
        # Cleanup
        "prune_containers": "docker container prune -f",
        "prune_images": "docker image prune -f",
        "prune_volumes": "docker volume prune -f",
        "prune_all": "docker system prune -af --volumes",
        "prune_builder": "docker builder prune -f",
        
        # Volumes
        "volume_ls": "docker volume ls",
        "volume_create": "docker volume create {name}",
        "volume_rm": "docker volume rm {name}",
        
        # Networks
        "network_ls": "docker network ls",
        "network_create": "docker network create {name}",
        "network_rm": "docker network rm {name}",
        "network_inspect": "docker network inspect {name}",
        
        # Copy
        "cp_to": "docker cp {source} {container}:{destination}",
        "cp_from": "docker cp {container}:{source} {destination}",
        
        # Save/Load
        "save": "docker save -o {file}.tar {image}",
        "load": "docker load -i {file}.tar",
        
        # Login
        "login": "docker login",
        "logout": "docker logout",
    }


class DockerComposePlugin:
    """Docker Compose commands."""
    
    TEMPLATES = {
        "up": "docker-compose up -d",
        "down": "docker-compose down",
        "down_volumes": "docker-compose down -v",
        "build": "docker-compose build",
        "build_no_cache": "docker-compose build --no-cache",
        "pull": "docker-compose pull",
        "push": "docker-compose push",
        "ps": "docker-compose ps",
        "logs": "docker-compose logs -f",
        "logs_service": "docker-compose logs -f {service}",
        "exec": "docker-compose exec {service} {command}",
        "restart": "docker-compose restart",
        "restart_service": "docker-compose restart {service}",
        "stop": "docker-compose stop",
        "start": "docker-compose start",
        "config": "docker-compose config",
        "scale": "docker-compose scale {service}={count}",
    }


class KubernetesPlugin:
    """Kubernetes commands."""
    
    SYSTEM_PROMPT = """You are a Kubernetes expert. Generate kubectl commands.
Output only the command."""
    
    TEMPLATES = {
        # Get resources
        "get_pods": "kubectl get pods",
        "get_pods_all": "kubectl get pods -A",
        "get_pods_wide": "kubectl get pods -o wide",
        "get_services": "kubectl get services",
        "get_deployments": "kubectl get deployments",
        "get_nodes": "kubectl get nodes",
        "get_namespaces": "kubectl get namespaces",
        "get_configmaps": "kubectl get configmaps",
        "get_secrets": "kubectl get secrets",
        "get_ingress": "kubectl get ingress",
        "get_pv": "kubectl get pv",
        "get_pvc": "kubectl get pvc",
        "get_all": "kubectl get all",
        
        # Describe
        "describe_pod": "kubectl describe pod {name}",
        "describe_service": "kubectl describe service {name}",
        "describe_deployment": "kubectl describe deployment {name}",
        "describe_node": "kubectl describe node {name}",
        
        # Apply/Delete
        "apply": "kubectl apply -f {file}",
        "apply_dir": "kubectl apply -f {directory}/",
        "delete": "kubectl delete -f {file}",
        "delete_pod": "kubectl delete pod {name}",
        "delete_deployment": "kubectl delete deployment {name}",
        
        # Logs
        "logs": "kubectl logs {pod}",
        "logs_follow": "kubectl logs -f {pod}",
        "logs_previous": "kubectl logs --previous {pod}",
        "logs_container": "kubectl logs {pod} -c {container}",
        
        # Execute
        "exec": "kubectl exec -it {pod} -- {command}",
        "exec_bash": "kubectl exec -it {pod} -- /bin/bash",
        "exec_sh": "kubectl exec -it {pod} -- /bin/sh",
        
        # Port forward
        "port_forward": "kubectl port-forward {pod} {local_port}:{remote_port}",
        "port_forward_svc": "kubectl port-forward svc/{service} {local_port}:{remote_port}",
        
        # Scale
        "scale": "kubectl scale deployment {name} --replicas={count}",
        
        # Rollout
        "rollout_status": "kubectl rollout status deployment/{name}",
        "rollout_history": "kubectl rollout history deployment/{name}",
        "rollout_undo": "kubectl rollout undo deployment/{name}",
        "rollout_restart": "kubectl rollout restart deployment/{name}",
        
        # Create
        "create_ns": "kubectl create namespace {name}",
        "create_secret": "kubectl create secret generic {name} --from-literal={key}={value}",
        "create_configmap": "kubectl create configmap {name} --from-file={file}",
        "create_deployment": "kubectl create deployment {name} --image={image}",
        
        # Set
        "set_image": "kubectl set image deployment/{name} {container}={image}",
        "set_env": "kubectl set env deployment/{name} {key}={value}",
        
        # Copy
        "cp_to": "kubectl cp {source} {pod}:{destination}",
        "cp_from": "kubectl cp {pod}:{source} {destination}",
        
        # Context
        "config_contexts": "kubectl config get-contexts",
        "config_use": "kubectl config use-context {context}",
        "config_current": "kubectl config current-context",
        
        # Top
        "top_pods": "kubectl top pods",
        "top_nodes": "kubectl top nodes",
        
        # Events
        "events": "kubectl get events --sort-by='.lastTimestamp'",
        
        # Debug
        "debug": "kubectl debug {pod} -it --image=busybox",
    }


class HelmPlugin:
    """Helm package manager commands."""
    
    TEMPLATES = {
        "repo_add": "helm repo add {name} {url}",
        "repo_update": "helm repo update",
        "repo_list": "helm repo list",
        "search": "helm search repo {chart}",
        "install": "helm install {release} {chart}",
        "install_values": "helm install {release} {chart} -f {values_file}",
        "upgrade": "helm upgrade {release} {chart}",
        "uninstall": "helm uninstall {release}",
        "list": "helm list",
        "list_all": "helm list -A",
        "history": "helm history {release}",
        "rollback": "helm rollback {release} {revision}",
        "status": "helm status {release}",
        "show_values": "helm show values {chart}",
    }


class PodmanPlugin:
    """Podman container commands."""
    
    TEMPLATES = {
        "run": "podman run -d --name {name} {image}",
        "ps": "podman ps",
        "stop": "podman stop {container}",
        "rm": "podman rm {container}",
        "images": "podman images",
        "build": "podman build -t {name} .",
        "logs": "podman logs {container}",
        "exec": "podman exec -it {container} {command}",
    }
