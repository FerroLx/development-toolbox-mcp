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

    print(f"Starting server with {args.transport.upper()} transport...")
    uvicorn.run(app, host="0.0.0.0", port=9654)


if __name__ == "__main__":
    run()