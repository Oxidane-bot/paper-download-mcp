#!/usr/bin/env python3
"""Tests for MCP tool signature defaults."""

import inspect
import sys

sys.path.insert(0, "src")

from paper_download_mcp.tools.download import paper_download
from paper_download_mcp.tools.metadata import paper_get_metadata


def test_paper_download_signature_defaults():
    signature = inspect.signature(paper_download)

    assert "identifiers" in signature.parameters
    assert "identifier" not in signature.parameters
    assert "to_markdown" in signature.parameters
    assert signature.parameters["to_markdown"].default is False
    assert "md_output_dir" in signature.parameters
    assert signature.parameters["md_output_dir"].default is None


def test_paper_get_metadata_signature():
    signature = inspect.signature(paper_get_metadata)

    assert list(signature.parameters.keys()) == ["identifier"]
