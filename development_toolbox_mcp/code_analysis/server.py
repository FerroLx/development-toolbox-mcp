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
            check=False,  # ruff exits with non-zero code if issues are found
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
            check=False,  # mypy exits with non-zero code if issues are found
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