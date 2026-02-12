"""Download tools for single and batch paper downloads."""

import asyncio

from ..adapters.core_results import core_to_mcp_download_result
from ..formatters import format_batch_results, format_download_result
from ..runtime import get_runtime_config
from ..server import mcp
from ..services.download_service import batch_download_sync, download_sync

MAX_BATCH_SIZE = 50
BATCH_DELAY_SECONDS = 2

# Backward-compatible export for tests and external imports.
_format_core_result = core_to_mcp_download_result


@mcp.tool()
async def paper_download(
    identifier: str,
    output_dir: str | None = "./downloads",
    to_markdown: bool = False,
    md_output_dir: str | None = None,
) -> str:
    """
    Download one academic paper by DOI, arXiv ID, or URL.
    Optionally converts the downloaded PDF to Markdown and stores the `.md` file in
    `md_output_dir` (default: `<output_dir>/md`).

    Prioritizes open access sources (Unpaywall, arXiv, CORE) before Sci-Hub.
    Sources: Unpaywall (OA), arXiv (OA), CORE (OA), Sci-Hub (last resort)

    Args:
        identifier: DOI, arXiv ID, or URL
        output_dir: Save directory (default: './downloads')
        to_markdown: Convert downloaded PDF to Markdown (default: False)
        md_output_dir: Directory for generated Markdown files (default: '<pdf_output_dir>/md')

    Returns:
        Markdown with file path, metadata, source, or error message

    Examples:
        paper_download("10.1038/nature12373")  # DOI
        paper_download("2301.00001")  # arXiv ID
        paper_download("https://arxiv.org/abs/2301.00001")  # URL
    """

    result = await asyncio.to_thread(
        download_sync,
        config=get_runtime_config(),
        identifier=identifier,
        output_dir=output_dir,
        to_markdown=to_markdown,
        md_output_dir=md_output_dir,
    )

    return format_download_result(result)


@mcp.tool()
async def paper_batch_download(
    identifiers: list[str],
    output_dir: str | None = "./downloads",
    to_markdown: bool = False,
    md_output_dir: str | None = None,
) -> str:
    """
    Download multiple papers sequentially (1-50 max, 2s delay).
    Optionally converts each PDF to Markdown and stores `.md` files in `md_output_dir`
    (default: `<output_dir>/md`).

    Prioritizes open access sources (Unpaywall, arXiv, CORE) before Sci-Hub.

    Args:
        identifiers: List of DOIs, arXiv IDs, or URLs
        output_dir: Save directory (default: './downloads')
        to_markdown: Convert downloaded PDFs to Markdown (default: False)
        md_output_dir: Directory for generated Markdown files (default: '<pdf_output_dir>/md')

    Returns:
        Markdown summary with statistics, successes, and failures

    Examples:
        paper_batch_download(["10.1038/nature12373", "2301.00001"])
        paper_batch_download(dois, "/papers")
    """
    # Validate input size
    if not identifiers:
        return "# Error\n\nNo identifiers provided. Please provide at least one DOI or URL."

    if len(identifiers) > MAX_BATCH_SIZE:
        return (
            "# Error\n\n"
            f"Too many identifiers ({len(identifiers)}). "
            f"Maximum {MAX_BATCH_SIZE} papers per batch.\n\n"
            "**Suggestion**: Split into multiple smaller batches."
        )

    results = await asyncio.to_thread(
        batch_download_sync,
        config=get_runtime_config(),
        identifiers=identifiers,
        output_dir=output_dir,
        to_markdown=to_markdown,
        md_output_dir=md_output_dir,
        delay_seconds=BATCH_DELAY_SECONDS,
    )

    return format_batch_results(results)
