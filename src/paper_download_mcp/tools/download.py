"""Download tool for one or more papers."""

import asyncio

from ..adapters.core_results import core_to_mcp_download_result
from ..formatters import format_batch_results
from ..runtime import get_runtime_config
from ..server import mcp
from ..services.download_service import download_many_sync

MAX_BATCH_SIZE = 50
BATCH_DELAY_SECONDS = 2

# Backward-compatible export for tests and external imports.
_format_core_result = core_to_mcp_download_result


@mcp.tool()
async def paper_download(
    identifiers: list[str],
    output_dir: str | None = "./downloads",
    to_markdown: bool = False,
    md_output_dir: str | None = None,
) -> str:
    """
    Download one or more academic papers by DOI, arXiv ID, or URL.
    Runs sequentially (1-50 max, 2s delay between items) and optionally converts PDFs
    to Markdown in `md_output_dir` (default: `<output_dir>/md`).

    Args:
        identifiers: List of DOIs, arXiv IDs, or URLs
        output_dir: Save directory (default: './downloads')
        to_markdown: Convert downloaded PDFs to Markdown (default: False)
        md_output_dir: Directory for generated Markdown files (default: '<output_dir>/md')

    Returns:
        Markdown summary with statistics, successes, and failures

    Examples:
        paper_download(["10.1038/nature12373"])  # single item
        paper_download(["10.1038/nature12373", "2301.00001"])  # multiple items
    """
    if not identifiers:
        return (
            "# Error\n\nNo identifiers provided. Please provide at least one DOI, arXiv ID, or URL."
        )

    if len(identifiers) > MAX_BATCH_SIZE:
        return (
            "# Error\n\n"
            f"Too many identifiers ({len(identifiers)}). "
            f"Maximum {MAX_BATCH_SIZE} papers per batch.\n\n"
            "**Suggestion**: Split into multiple smaller batches."
        )

    results = await asyncio.to_thread(
        download_many_sync,
        config=get_runtime_config(),
        identifiers=identifiers,
        output_dir=output_dir,
        to_markdown=to_markdown,
        md_output_dir=md_output_dir,
        delay_seconds=BATCH_DELAY_SECONDS,
    )

    return format_batch_results(results)
