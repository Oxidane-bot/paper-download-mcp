#!/usr/bin/env python3
"""Tests for markdown conversion result mapping and formatting."""

import sys

sys.path.insert(0, "src")

from paper_download_mcp.formatters import format_batch_results, format_download_result
from paper_download_mcp.models import DownloadResult
from paper_download_mcp.scihub_core.models import DownloadResult as CoreDownloadResult
from paper_download_mcp.tools.download import _format_core_result


def test_format_core_result_maps_markdown_fields():
    core_result = CoreDownloadResult(
        identifier="10.1000/demo",
        normalized_identifier="10.1000/demo",
        success=True,
        file_path="/tmp/paper.pdf",
        file_size=12000,
        source="Unpaywall",
        metadata={"title": "Demo Paper", "year": 2024},
        title="Demo Paper",
        year=2024,
        md_path="/tmp/md/paper.md",
        md_success=True,
        md_error=None,
    )

    result = _format_core_result(core_result)

    assert result.md_path == "/tmp/md/paper.md"
    assert result.md_success is True
    assert result.md_error is None


def test_single_formatter_includes_markdown_status_and_error():
    result = DownloadResult(
        doi="10.1000/demo",
        success=True,
        file_path="/tmp/paper.pdf",
        file_size=10240,
        source="Unpaywall",
        md_path="/tmp/md/paper.md",
        md_success=False,
        md_error="pymupdf4llm is not installed",
    )

    output = format_download_result(result)

    assert "Markdown Conversion**: Failed" in output
    assert "Markdown Path" in output
    assert "Markdown Error" in output


def test_batch_formatter_includes_markdown_details():
    results = [
        DownloadResult(
            doi="10.1000/success",
            success=True,
            file_path="/tmp/success.pdf",
            file_size=20480,
            source="Unpaywall",
            md_success=True,
            md_path="/tmp/md/success.md",
        ),
        DownloadResult(doi="10.1000/fail", success=False, error="not found"),
    ]

    output = format_batch_results(results)

    assert "Markdown: Success" in output
    assert "Markdown Path" in output
    assert "Failed Downloads" in output
