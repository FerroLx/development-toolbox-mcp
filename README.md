# Development Toolbox MCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An extensible, AI-powered development toolbox built with the Model-Context-Protocol (MCP) framework. This repository provides a ready-to-use server with tools for code analysis and Docker management, designed to be called by any MCP-compatible AI agent.

This project also serves as the official source code for our tutorial series on building advanced MCPs.

## ✨ Features

*   **Code Analysis**: Perform linting with `ruff` and static type checking with `mypy`.
*   **Docker Control**: List and stop running Docker containers directly from your agent.
*   **Tutorial Project**: This repository represents the completed code for Part 1 of the "Building an AI-Powered Development Co-Pilot" tutorial series.

## 🚀 Getting Started

To run the server from the source code, follow these steps. This is the recommended setup for both using the tools and following the tutorial.

1.  **Prerequisites**:
    *   Python 3.10 or higher
    *   `uv` (install with `pip install uv`)
    *   Docker Desktop (must be running for the Docker tools to work)

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/FerroLx/development-toolbox-mcp
    cd development-toolbox-mcp
    ```

3.  **Install dependencies**:
    This command installs all dependencies and makes the `dev-toolbox` script available.
    ```bash
    uv pip install -e .
    ```

4.  **Run the server**:
    You can now run the server using `uv run`.
    ```bash
    uv run dev-toolbox
    ```
    The server will start on `http://localhost:9654`.

5.  **Connect Your Agent**: The MCP server is now running. Use the following URLs in your MCP client (e.g., Cursor, Claude Code, or the MCP Inspector):

    *   **Code Analysis Server**: `http://localhost:9654/code`
    *   **Docker Control Server**: `http://localhost:9654/docker`

## 🎓 Tutorial Series

This repository is the starting point for a tutorial series on building a sophisticated, AI-powered development co-pilot.

*   **Read Part 1: Your First MCP Server** - This tutorial walks you through building the exact code in this repository from scratch.

Future tutorials will build on this foundation to add more advanced features like stateful sessions, real-time log streaming, and external API integrations.

## 🤝 Contributing

Contributions are welcome! If you have an idea for a new tool or an improvement, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.
