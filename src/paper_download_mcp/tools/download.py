"""Download tools for single and batch paper downloads."""

import asyncio
import os
import time

from ..formatters import format_batch_results, format_download_result
from ..models import DownloadResult
from ..scihub_core.client import SciHubClient
from ..scihub_core.models import DownloadResult as CoreDownloadResult
from ..server import DEFAULT_OUTPUT_DIR, EMAIL, mcp


def _format_core_result(core_result: CoreDownloadResult) -> DownloadResult:
    """Convert scihub-core download results into MCP-friendly results."""
    doi = core_result.normalized_identifier or core_result.identifier
    file_path = os.path.abspath(core_result.file_path) if core_result.file_path else None
    md_path = os.path.abspath(core_result.md_path) if core_result.md_path else None
    file_size = core_result.file_size
    if file_path and file_size is None and os.path.exists(file_path):
        file_size = os.path.getsize(file_path)

    source = core_result.source
    if not source and isinstance(core_result.metadata, dict):
        source = core_result.metadata.get("source")

    return DownloadResult(
        doi=doi,
        success=core_result.success,
        file_path=file_path,
        file_size=file_size,
        title=core_result.title,
        year=core_result.year,
        source=source,
        download_time=core_result.download_time,
        error=core_result.error,
        md_path=md_path,
        md_success=core_result.md_success,
        md_error=core_result.md_error,
    )


@mcp.tool()
async def paper_download(
    identifier: str,
    output_dir: str | None = "./downloads",
    to_markdown: bool = False,
    md_output_dir: str | None = None,
) -> str:
    """
    Download academic paper by DOI, arXiv ID, or URL.

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

    def _download() -> DownloadResult:
        """Synchronous wrapper for download operation."""
        try:
            # Initialize client with configuration
            client = SciHubClient(
                email=EMAIL or "",
                output_dir=output_dir or DEFAULT_OUTPUT_DIR,
                convert_to_md=to_markdown,
                md_output_dir=md_output_dir,
            )

            # Download paper
            core_result = client.download_paper(identifier)
            return _format_core_result(core_result)

        except Exception as e:
            return DownloadResult(doi=identifier, success=False, error=str(e))

    # Run synchronous download in thread pool
    result = await asyncio.to_thread(_download)

    # Format and return result
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

    if len(identifiers) > 50:
        return (
            "# Error\n\n"
            f"Too many identifiers ({len(identifiers)}). "
            "Maximum 50 papers per batch.\n\n"
            "**Suggestion**: Split into multiple smaller batches."
        )

    def _batch_download() -> list[DownloadResult]:
        """Synchronous wrapper for batch download operation."""
        results = []
        client = SciHubClient(
            email=EMAIL or "",
            output_dir=output_dir or DEFAULT_OUTPUT_DIR,
            convert_to_md=to_markdown,
            md_output_dir=md_output_dir,
        )

        for i, identifier in enumerate(identifiers):
            try:
                core_result = client.download_paper(identifier)
                results.append(_format_core_result(core_result))
            except Exception as e:
                results.append(
                    DownloadResult(
                        doi=identifier,
                        success=False,
                        error=str(e),
                    )
                )

            # Add delay between downloads (except after last one)
            if i < len(identifiers) - 1:
                time.sleep(2)

        return results

    # Run batch download in thread pool
    results = await asyncio.to_thread(_batch_download)

    # Format and return results
    return format_batch_results(results)
