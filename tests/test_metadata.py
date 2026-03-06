#!/usr/bin/env python3
"""Integration test for Unpaywall metadata retrieval."""

import asyncio
import os
import sys

import pytest

sys.path.insert(0, "src")

from paper_download_mcp.scihub_core.sources.unpaywall_source import UnpaywallSource


@pytest.mark.asyncio
async def test_unpaywall_api_returns_metadata():
    doi = "10.1038/nature12373"
    email = (
        os.getenv("PAPER_DOWNLOAD_EMAIL") or os.getenv("SCIHUB_CLI_EMAIL") or "test@university.edu"
    )

    def _get_metadata() -> dict | None:
        unpaywall = UnpaywallSource(email=email, timeout=10)
        return unpaywall.get_metadata(doi)

    metadata = await asyncio.to_thread(_get_metadata)

    assert isinstance(metadata, dict), "Expected metadata dictionary from Unpaywall"
    assert metadata.get("title"), "Expected title in Unpaywall metadata"
    assert isinstance(metadata.get("year"), int), "Expected numeric year in metadata"
    assert "is_oa" in metadata
