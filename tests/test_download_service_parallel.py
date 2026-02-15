#!/usr/bin/env python3
"""Tests for batch download service concurrency behavior (offline)."""

import sys
from unittest.mock import Mock

sys.path.insert(0, "src")

from paper_download_mcp.runtime import RuntimeConfig
from paper_download_mcp.scihub_core.models import DownloadResult as CoreDownloadResult
from paper_download_mcp.services import download_service


def _runtime_config() -> RuntimeConfig:
    return RuntimeConfig(email="test@university.edu", default_output_dir="./downloads")


def _core_result(identifier: str) -> CoreDownloadResult:
    return CoreDownloadResult(
        identifier=identifier,
        normalized_identifier=identifier,
        success=True,
        file_path=f"/tmp/{identifier.replace('/', '_')}.pdf",
        file_size=12345,
        source="Unpaywall",
        metadata={"title": "Demo", "year": 2020},
        title="Demo",
        year=2020,
    )


def test_parallel_download_does_not_sleep_between_items(monkeypatch):
    identifiers = ["10.1000/a", "10.1000/b", "10.1000/c"]
    fake_client = Mock()
    fake_client.download_paper.side_effect = lambda identifier: _core_result(identifier)

    monkeypatch.setattr(download_service, "_build_client", lambda **kwargs: fake_client)
    sleep_mock = Mock()
    monkeypatch.setattr(download_service.time, "sleep", sleep_mock)

    results = download_service.download_many_sync(
        config=_runtime_config(),
        identifiers=identifiers,
        output_dir="./downloads",
        parallel=3,
        to_markdown=False,
        md_output_dir=None,
        delay_seconds=2,
    )

    assert [result.doi for result in results] == identifiers
    assert fake_client.download_paper.call_count == len(identifiers)
    assert sleep_mock.call_count == 0


def test_sequential_download_keeps_inter_item_sleep(monkeypatch):
    identifiers = ["10.1000/a", "10.1000/b", "10.1000/c"]
    fake_client = Mock()
    fake_client.download_paper.side_effect = lambda identifier: _core_result(identifier)

    monkeypatch.setattr(download_service, "_build_client", lambda **kwargs: fake_client)
    sleep_mock = Mock()
    monkeypatch.setattr(download_service.time, "sleep", sleep_mock)

    results = download_service.download_many_sync(
        config=_runtime_config(),
        identifiers=identifiers,
        output_dir="./downloads",
        parallel=1,
        to_markdown=False,
        md_output_dir=None,
        delay_seconds=2,
    )

    assert [result.doi for result in results] == identifiers
    assert fake_client.download_paper.call_count == len(identifiers)
    assert sleep_mock.call_count == len(identifiers) - 1
