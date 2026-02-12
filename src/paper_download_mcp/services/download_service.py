"""Blocking download workflows used by MCP tools."""

from __future__ import annotations

import time

from ..adapters.core_results import core_to_mcp_download_result
from ..models import DownloadResult
from ..runtime import RuntimeConfig
from ..scihub_core.client import SciHubClient


def _build_client(
    *,
    config: RuntimeConfig,
    output_dir: str | None,
    to_markdown: bool,
    md_output_dir: str | None,
) -> SciHubClient:
    """Create a configured SciHubClient instance for tool execution."""
    return SciHubClient(
        email=config.email or "",
        output_dir=output_dir or config.default_output_dir,
        convert_to_md=to_markdown,
        md_output_dir=md_output_dir,
    )


def download_sync(
    *,
    config: RuntimeConfig,
    identifier: str,
    output_dir: str | None,
    to_markdown: bool,
    md_output_dir: str | None,
) -> DownloadResult:
    """Download one paper using blocking core APIs."""
    try:
        client = _build_client(
            config=config,
            output_dir=output_dir,
            to_markdown=to_markdown,
            md_output_dir=md_output_dir,
        )
        return core_to_mcp_download_result(client.download_paper(identifier))
    except Exception as e:
        return DownloadResult(doi=identifier, success=False, error=str(e))


def batch_download_sync(
    *,
    config: RuntimeConfig,
    identifiers: list[str],
    output_dir: str | None,
    to_markdown: bool,
    md_output_dir: str | None,
    delay_seconds: int = 2,
) -> list[DownloadResult]:
    """Download multiple papers sequentially using blocking core APIs."""
    results: list[DownloadResult] = []
    client = _build_client(
        config=config,
        output_dir=output_dir,
        to_markdown=to_markdown,
        md_output_dir=md_output_dir,
    )

    for index, identifier in enumerate(identifiers):
        try:
            results.append(core_to_mcp_download_result(client.download_paper(identifier)))
        except Exception as e:
            results.append(DownloadResult(doi=identifier, success=False, error=str(e)))

        if index < len(identifiers) - 1:
            time.sleep(delay_seconds)

    return results
