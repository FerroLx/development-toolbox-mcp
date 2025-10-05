import docker
from docker.client import DockerClient
from docker.errors import NotFound
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional

docker_mcp = FastMCP(name="DockerControlServer", stateless_http=True)

docker_client: Optional[DockerClient] = None
try:
    docker_client = docker.from_env()
except docker.errors.DockerException as e:
    print(f"Docker not available: {e}")

@docker_mcp.tool()
def list_containers(all_containers: bool = False) -> List[Dict[str, Any]]:
    """
    Lists all Docker containers.
    """
    if not docker_client:
        return [{"error": "Docker is not running or is not installed."}]

    containers = docker_client.containers.list(all=all_containers)
    return [
        {
            "id": c.short_id,
            "name": c.name,
            "image": c.image.tags[0] if c.image.tags else "N/A",
            "status": c.status,
        }
        for c in containers
    ]

@docker_mcp.tool()
def stop_container(container_id: str) -> Dict[str, str]:
    """
    Stops a running Docker container by its ID.
    """
    if not docker_client:
        return {"error": "Docker is not running or is not installed."}

    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        return {"status": "success", "message": f"Container {container_id} stopped."}
    except NotFound:
        return {"status": "error", "message": f"Container {container_id} not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
