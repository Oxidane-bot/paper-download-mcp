"""FastMCP server entry point for paper download MCP server."""

import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("paper-download-mcp")

# Global configuration
EMAIL = os.getenv("SCIHUB_CLI_EMAIL")
DEFAULT_OUTPUT_DIR = os.getenv("SCIHUB_OUTPUT_DIR", "./downloads")


def _require_email() -> str:
    """
    Validate that email configuration is present.

    Returns:
        Email address

    Raises:
        ValueError: If SCIHUB_CLI_EMAIL environment variable is not set
    """
    if not EMAIL:
        raise ValueError(
            "SCIHUB_CLI_EMAIL environment variable is required.\n"
            "This email is used for Unpaywall API compliance.\n\n"
            "To configure:\n"
            "1. Set environment variable: export SCIHUB_CLI_EMAIL=your-email@university.edu\n"
            "2. Or add to Claude Desktop config:\n"
            '   {\n'
            '     "mcpServers": {\n'
            '       "paper-download": {\n'
            '         "command": "uvx",\n'
            '         "args": ["paper-download-mcp"],\n'
            '         "env": {"SCIHUB_CLI_EMAIL": "your-email@university.edu"}\n'
            '       }\n'
            '     }\n'
            '   }\n'
        )
    return EMAIL


def main():
    """Main entry point for the MCP server."""
    # Validate email configuration on startup
    _require_email()

    # Import tools to register them with the server
    # Must import before mcp.run() to ensure tools are registered
    from .tools import download, metadata  # noqa: F401

    # Run the FastMCP server with stdio transport
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
