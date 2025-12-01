"""MCP tools for paper download operations."""

# Import modules to trigger @mcp.tool() decorators
from . import download  # noqa: F401
from . import metadata  # noqa: F401

__all__ = ['download', 'metadata']
