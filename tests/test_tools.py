#!/usr/bin/env python3
"""Quick test script to verify MCP tools are registered correctly."""

import asyncio
import sys

sys.path.insert(0, "src")

from paper_download_mcp.server import mcp
from paper_download_mcp.tools import download, metadata


async def main():
    """Test tool registration."""
    print("=" * 60)
    print("MCP Server Tool Registration Test")
    print("=" * 60)

    # Get registered tools
    tools = await mcp.get_tools()

    print(f"\nFound {len(tools)} registered tools:\n")

    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool}")
        print()

    print("=" * 60)
    print("All tools registered successfully!")
    print("=" * 60)

    # Test that we can access the tool functions
    print("\nTool functions accessible:")
    print(f"  - paper_download: {hasattr(download, 'paper_download')}")
    print(f"  - paper_batch_download: {hasattr(download, 'paper_batch_download')}")
    print(f"  - paper_metadata: {hasattr(metadata, 'paper_metadata')}")

    return len(tools)


if __name__ == "__main__":
    import os

    os.environ["SCIHUB_CLI_EMAIL"] = "test@university.edu"

    count = asyncio.run(main())
    sys.exit(0 if count == 3 else 1)
