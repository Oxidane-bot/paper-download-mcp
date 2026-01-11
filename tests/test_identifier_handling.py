#!/usr/bin/env python3
"""Identifier parsing tests (offline)."""

import sys

sys.path.insert(0, "src")

from paper_download_mcp.scihub_core.core.doi_processor import DOIProcessor
from paper_download_mcp.scihub_core.sources.arxiv_source import ArxivSource
from paper_download_mcp.scihub_core.sources.core_source import CORESource


def test_normalize_doi_strips_prefix():
    assert DOIProcessor.normalize_doi("doi:10.1000/xyz") == "10.1000/xyz"
    assert DOIProcessor.normalize_doi("DOI: 10.1000/xyz") == "10.1000/xyz"


def test_normalize_doi_removes_internal_whitespace():
    assert (
        DOIProcessor.normalize_doi("https://arxiv.org/\n abs/1706.03762")
        == "https://arxiv.org/abs/1706.03762"
    )
    assert DOIProcessor.normalize_doi("10.1000/ xyz") == "10.1000/xyz"


def test_arxiv_urls_are_recognized():
    source = ArxivSource()
    assert source.can_handle("https://arxiv.org/abs/2301.00001")
    assert source.can_handle("https://arxiv.org/pdf/2301.00001.pdf")


def test_core_handles_dois_only():
    source = CORESource()
    assert source.can_handle("10.1000/xyz")
    assert not source.can_handle("1202.2745")
