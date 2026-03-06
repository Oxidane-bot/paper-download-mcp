#!/usr/bin/env python3
"""Tests for MCP tool registration and exports."""

import sys

import pytest

sys.path.insert(0, "src")

from paper_download_mcp.server import mcp
from paper_download_mcp.tools import download, metadata


@pytest.mark.asyncio
async def test_registered_tools_include_expected_names():
    tools = await mcp.list_tools()
    tool_names = {tool.name for tool in tools}

    assert "paper_download" in tool_names
    assert "paper_get_metadata" in tool_names


def test_tool_functions_are_importable():
    assert hasattr(download, "paper_download")
    assert hasattr(metadata, "paper_get_metadata")
