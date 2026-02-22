"""Blocking download workflows used by MCP tools."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        enable_core=False,
        fast_fail=True,
    )


def download_many_sync(
    *,
    config: RuntimeConfig,
    identifiers: list[str],
    output_dir: str | None,
    to_markdown: bool,
    md_output_dir: str | None,
    delay_seconds: int = 2,
    parallel: int = 10,
) -> list[DownloadResult]:
    """Download multiple papers with optional parallel workers using blocking core APIs."""
    results: list[DownloadResult] = []
    parallel = max(1, parallel)
    client = _build_client(
        config=config,
        output_dir=output_dir,
        to_markdown=to_markdown,
        md_output_dir=md_output_dir,
    )

    if parallel == 1 or len(identifiers) <= 1:
        for index, identifier in enumerate(identifiers):
            try:
                results.append(core_to_mcp_download_result(client.download_paper(identifier)))
            except Exception as e:
                results.append(DownloadResult(doi=identifier, success=False, error=str(e)))

            if index < len(identifiers) - 1:
                time.sleep(delay_seconds)
        return results

    workers = min(parallel, len(identifiers))
    ordered_results: list[DownloadResult | None] = [None] * len(identifiers)

    def _download_one(index: int, identifier: str) -> tuple[int, DownloadResult]:
        try:
            result = core_to_mcp_download_result(client.download_paper(identifier))
        except Exception as e:
            result = DownloadResult(doi=identifier, success=False, error=str(e))
        return index, result

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_index = {
            executor.submit(_download_one, index, identifier): index
            for index, identifier in enumerate(identifiers)
        }
        for future in as_completed(future_to_index):
            index, result = future.result()
            ordered_results[index] = result

    return [result for result in ordered_results if result is not None]
