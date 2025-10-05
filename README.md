# Development Toolbox MCP

A collection of MCP servers providing development tools for code analysis and Docker control.

## Features

- **Code Analysis**: Perform linting with `ruff` and static type checking with `mypy`.
- **Docker Control**: Manage your Docker containers right from your agent.

## Installation

To ensure the `dev-toolbox` command is available, install the project in editable mode along with its development dependencies using `uv`:

```bash
uv pip install -e .[dev]
```

## Running the Server

You can run the server using the `dev-toolbox` script with `uv run`:

```bash
uv run dev-toolbox
```

By default, the server uses Server-Sent Events (SSE). You can also run it with Streamable HTTP by passing arguments after `--`:

```bash
uv run dev-toolbox -- --transport stream-http
```

The MCPs will be available at:

  - **Code Analysis**: `http://localhost:9654/code`
  - **Docker Control**: `http://localhost:9654/docker`

## How to Use

Connect your MCP agent to the server endpoints to start using the tools.

### Code Analysis Tools

  - `run_linter(project_path: str)`: Runs Ruff on the specified path and returns a report.
  - `run_type_checker(project_path: str)`: Runs Mypy on the specified path and returns a report.

### Docker Control Tools

  - `list_containers(all_containers: bool = False)`: Lists all Docker containers.
  - `stop_container(container_id: str)`: Stops a container by its ID.

## License

This project is licensed under the MIT License.
