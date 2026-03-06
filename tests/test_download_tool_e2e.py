#!/usr/bin/env python3
"""Tool-layer end-to-end tests for paper_download."""

import sys

import pytest

sys.path.insert(0, "src")

from paper_download_mcp.models import DownloadResult
from paper_download_mcp.runtime import RuntimeConfig
from paper_download_mcp.tools import download as download_tool


def _success_result(identifier: str) -> DownloadResult:
    return DownloadResult(
        doi=identifier,
        success=True,
        file_path="/tmp/demo.pdf",
        file_size=12_345,
        source="Unpaywall",
        download_time=0.12,
    )


@pytest.mark.asyncio
async def test_paper_download_e2e_passes_none_output_dir_when_omitted(monkeypatch):
    captured: dict = {}

    def fake_download_many_sync(**kwargs):
        captured.update(kwargs)
        return [_success_result(kwargs["identifiers"][0])]

    monkeypatch.setattr(download_tool, "download_many_sync", fake_download_many_sync)
    monkeypatch.setattr(
        download_tool,
        "get_runtime_config",
        lambda: RuntimeConfig(
            email="test@university.edu", default_output_dir="/tmp/runtime-default"
        ),
    )

    output = await download_tool.paper_download(identifiers=["10.1000/demo"])

    assert captured["output_dir"] is None
    assert captured["config"].default_output_dir == "/tmp/runtime-default"
    assert "# Download Summary" in output
    assert "**Total Papers**: 1" in output
    assert "**Successful**: 1 (100.0%)" in output


@pytest.mark.asyncio
async def test_paper_download_e2e_passes_explicit_output_dir(monkeypatch):
    captured: dict = {}

    def fake_download_many_sync(**kwargs):
        captured.update(kwargs)
        return [_success_result(kwargs["identifiers"][0])]

    monkeypatch.setattr(download_tool, "download_many_sync", fake_download_many_sync)
    monkeypatch.setattr(
        download_tool,
        "get_runtime_config",
        lambda: RuntimeConfig(
            email="test@university.edu", default_output_dir="/tmp/runtime-default"
        ),
    )

    await download_tool.paper_download(
        identifiers=["10.1000/demo"],
        output_dir="/tmp/explicit",
    )

    assert captured["output_dir"] == "/tmp/explicit"
