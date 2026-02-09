#!/usr/bin/env python3
"""Tests for MCP download tool signature defaults."""

import inspect
import sys

sys.path.insert(0, "src")

from paper_download_mcp.tools.download import paper_batch_download, paper_download


def test_paper_download_signature_defaults():
    signature = inspect.signature(paper_download)

    assert "to_markdown" in signature.parameters
    assert signature.parameters["to_markdown"].default is False
    assert "md_output_dir" in signature.parameters
    assert signature.parameters["md_output_dir"].default is None


def test_paper_batch_download_signature_defaults():
    signature = inspect.signature(paper_batch_download)

    assert "to_markdown" in signature.parameters
    assert signature.parameters["to_markdown"].default is False
    assert "md_output_dir" in signature.parameters
    assert signature.parameters["md_output_dir"].default is None
