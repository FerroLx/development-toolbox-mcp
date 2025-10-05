# Tutorial: Building Your First MCP Server for Development

Welcome to the first part of our series on building a powerful, personal development co-pilot with the MCP (Machine-Coded Protocol) framework. In this tutorial, we'll lay the foundation by creating a web server that exposes custom tools for code analysis and Docker container management.

By the end, you'll have a functional MCP server that you can connect to from any MCP-compatible agent, giving you a taste of how you can extend your development environment with custom-built tools.

## What is an MCP?

Think of an MCP as a personal, programmable toolkit. It's a server that you build and run, which exposes a set of "tools" (essentially functions) that an AI agent can call. Instead of being limited to a pre-defined set of actions, you can create your own tools to automate workflows, interact with local files, or integrate with any API you can imagine.

In this series, we'll start with simple tools and gradually build a sophisticated, AI-powered development assistant.

## Prerequisites

Before we begin, make sure you have the following installed:
*   **Python 3.10 or higher**
*   **uv**: A fast Python package installer and resolver. If you don't have it, you can install it with `pip install uv`.
*   **Docker Desktop**: Required for the Docker control part of our project. Make sure it's running.
*   **Node.js**: Required to run the MCP Inspector.

## Step 1: Project Structure

First, let's create our project directory and files. This structure keeps our different toolsets organized.

```
development-toolbox-mcp/
├── pyproject.toml
└── development_toolbox_mcp/
    ├── __init__.py
    ├── main.py
    ├── code_analysis/
    │   ├── __init__.py
    │   └── server.py
    └── docker_control/
        ├── __init__.py
        └── server.py
```

Create the directories and empty `__init__.py` files. We'll fill in the other files in the next steps.

## Step 2: Defining the Project with `pyproject.toml`

The `pyproject.toml` file is the heart of our project's configuration. It defines our dependencies and creates a command-line script to run our server.

Create `pyproject.toml` and add the following content:

```toml
[project]
name = "development-toolbox-mcp"
version = "0.1.0"
description = "A collection of MCP servers for code analysis and Docker control."
authors = [
    { name = "João Ferro", email = "jgmferro@gmail.com" },
]
readme = "README.md"
license = { text = "MIT" }

dependencies = [
    "mcp==1.16.0",
    "uvicorn==0.37.0",
    "starlette==0.48.0",
    "docker==7.1.0",
    "ruff==0.13.3",
    "mypy==1.18.2",
    "types-docker==7.1.0.20250916"
]

[project.scripts]
dev-toolbox = "development_toolbox_mcp.main:run"

[project.optional-dependencies]
dev = [
    "pytest",
]
```

This file tells Python what packages our project needs to run and defines the `dev-toolbox` command, which will be our entry point.

## Step 3: Building the Main Server

The `main.py` file is responsible for creating the main web application and mounting our different MCPs as sub-applications. We'll use the Starlette web framework for this.

We've updated this file to explicitly set the endpoint paths to the root of each mount (e.g., `/code/`) and to apply the application `lifespan` manager only when necessary for certain transports.

Add the following to `development_toolbox_mcp/main.py`:

```python
import argparse
import contextlib
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from development_toolbox_mcp.code_analysis.server import code_analysis_mcp
from development_toolbox_mcp.docker_control.server import docker_mcp


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """
    Manages the lifespan of all MCP servers.
    """

    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(code_analysis_mcp.session_manager.run())
        await stack.enter_async_context(docker_mcp.session_manager.run())
        yield


def create_app(use_streamable_http: bool = False) -> Starlette:
    """
    Creates the Starlette application with the appropriate transport.
    """
    if use_streamable_http:
        code_analysis_mcp.settings.streamable_http_path = "/"
        docker_mcp.settings.streamable_http_path = "/"
        routes = [
            Mount("/code", code_analysis_mcp.streamable_http_app()),
            Mount("/docker", docker_mcp.streamable_http_app()),
        ]
    else:
        code_analysis_mcp.settings.sse_path = "/"
        docker_mcp.settings.sse_path = "/"
        routes = [
            Mount("/code", app=code_analysis_mcp.sse_app()),
            Mount("/docker", app=docker_mcp.sse_app()),
        ]
    lifespan_to_use = lifespan if use_streamable_http else None
    return Starlette(routes=routes, lifespan=lifespan_to_use)


def run():
    """
    Runs the MCP server, defaulting to SSE, with an option for Streamable HTTP.
    """
    parser = argparse.ArgumentParser(description="Development Toolbox MCP Server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stream-http"],
        default="sse",
        help="The transport to use (defaults to sse).",
    )
    args = parser.parse_args()

    use_streamable = args.transport == "stream-http"
    app = create_app(use_streamable_http=use_streamable)

    print(f"Starting server with {args.transport.upper()} transport on http://localhost:9654")
    uvicorn.run(app, host="0.0.0.0", port=9654)


if __name__ == "__main__":
    run()
```

This script sets up two endpoints: `/code` and `/docker`. Each will host a different set of tools.

## Step 4: The Code Analysis MCP

Now, let's create our first set of tools. These will wrap popular command-line utilities (`ruff` for linting and `mypy` for type-checking) and expose them as MCP tools.

Add the following to `development_toolbox_mcp/code_analysis/server.py`:

```python
import subprocess
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any

code_analysis_mcp = FastMCP(name="CodeAnalysisServer", stateless_http=True)

@code_analysis_mcp.tool()
def run_linter(project_path: str) -> Dict[str, Any]:
    """
    Performs linting and static analysis using Ruff and returns the results.
    """
    try:
        result = subprocess.run(
            ["ruff", "check", project_path],
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "status": "success",
            "output": result.stdout or "No issues found.",
            "errors": result.stderr,
        }
    except FileNotFoundError:
        return {"status": "error", "message": "Ruff is not installed or not in PATH."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@code_analysis_mcp.tool()
def run_type_checker(project_path: str) -> Dict[str, Any]:
    """
    Performs static type checking using Mypy and returns the results.
    """
    try:
        result = subprocess.run(
            ["mypy", project_path],
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "status": "success",
            "output": result.stdout or "No type errors found.",
            "errors": result.stderr,
        }
    except FileNotFoundError:
        return {"status": "error", "message": "Mypy is not installed or not in PATH."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

The `@code_analysis_mcp.tool()` decorator is the magic that turns a regular Python function into an MCP tool that an agent can call.

## Step 5: The Docker Control MCP

Next, we'll build tools to interact with the Docker daemon. This demonstrates how to integrate with external services using a Python library.

Add the following to `development_toolbox_mcp/docker_control/server.py`:

```python
import docker
from docker.client import DockerClient
from docker.errors import NotFound, DockerException
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional

docker_mcp = FastMCP(name="DockerControlServer", stateless_http=True)

docker_client: Optional[DockerClient] = None
try:
    docker_client = docker.from_env()
except DockerException as e:
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
```

## Step 6: Running the Server

With all our code in place, it's time to install the dependencies and run the server.

1.  **Install Dependencies:**
    Open your terminal in the project's root directory (`development-toolbox-mcp/`) and run the following command. This installs all our dependencies and makes the `dev-toolbox` script available.

    ```bash
    uv pip install -e .
    ```

2.  **Run the Server:**
    Now, start the server with the command you defined in `pyproject.toml`.

    ```bash
    uv run dev-toolbox
    ```

You should see a message indicating the server has started on `http://localhost:9654`.

Your MCP server is now live! It's serving two toolsets:
*   **Code Analysis Tools:** at `http://localhost:9654/code`
*   **Docker Control Tools:** at `http://localhost:9654/docker`

## Step 7: Testing with the MCP Inspector

Now that your server is running, how do you interact with it? While you can connect any MCP-compatible agent, the easiest way to test your tools is with the **MCP Inspector**, a web-based UI for debugging and calling tools on any MCP server.

![MCP Inspector Screenshot](https://raw.githubusercontent.com/modelcontextprotocol/inspector/main/mcp-inspector.png)

### Running the Inspector

1.  **Keep your MCP server running** in your first terminal.
2.  Open a **new terminal** and run the following command to start the Inspector. This will download and run it without needing a manual installation.

    ```bash
    npx @modelcontextprotocol/inspector
    ```

3.  The Inspector UI will automatically open in your browser at `http://localhost:6274`.

### Connecting to Your Servers

Your toolbox exposes two separate MCP servers, so you'll connect to them one at a time.

1.  In the Inspector UI, make sure the **Transport** is set to **SSE (Server-Sent Events)**, as this is our server's default.
2.  To connect to the **Docker Control** tools, enter the following URL into the **Server URL** field and click **Connect**:

    ```
    http://localhost:9654/docker
    ```

3.  Once connected, you will see a list of available tools. Click on `list_containers`. You can change the `all_containers` argument and then click **Call** to see the result.
4.  To test the **Code Analysis** tools, disconnect and change the URL to the other endpoint:

    ```
    http://localhost:9654/code
    ```

5.  Connect again, and you'll see the `run_linter` and `run_type_checker` tools, ready to be tested.

The Inspector is an invaluable tool for debugging, and you can explore its more advanced features like CLI mode and configuration files in its official documentation.

## Conclusion and What's Next

Congratulations! You've successfully built and tested your first MCP server. You now have a personal, extensible toolbox that can perform code analysis and manage Docker containers. The full code for this tutorial is available on GitHub at [YOUR_GITHUB_PROJECT_LINK_HERE].

This is the foundational "sensory system" of our co-pilot—it can perform quick, stateless actions.

But our co-pilot can't *think* or *remember* yet.

In the next tutorial, we'll dive into one of the most powerful features of MCPs: **stateful sessions**. We'll build a "Refactoring Assistant" that can remember the context of a file, analyze its structure using Abstract Syntax Trees (ASTs), and guide you through a multi-step code refactoring.

Stay tuned!
