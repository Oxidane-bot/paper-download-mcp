"""Download tools for single and batch paper downloads."""

import asyncio
import os
import time
from typing import Optional

from ..server import mcp, EMAIL, DEFAULT_OUTPUT_DIR
from ..models import DownloadPaperInput, BatchDownloadInput, DownloadResult
from ..formatters import format_download_result, format_batch_results
from ..scihub_core.client import SciHubClient


@mcp.tool()
async def paper_download(identifier: str, output_dir: Optional[str] = "./downloads") -> str:
    """
    Download a single academic paper by DOI or URL.

    This tool downloads papers from multiple sources (Sci-Hub, Unpaywall) with
    intelligent routing based on publication year:
    - Papers published before 2021: Try Sci-Hub first, fallback to Unpaywall
    - Papers published 2021 or later: Try Unpaywall first, fallback to Sci-Hub

    Args:
        identifier: DOI (e.g., '10.1038/nature12373') or URL (e.g., 'https://doi.org/...')
        output_dir: Directory to save the PDF (default: './downloads')

    Returns:
        Markdown-formatted string with download details (file path, metadata, source)
        or error message with suggestions if download fails

    Examples:
        - paper_download("10.1038/nature12373")
        - paper_download("https://doi.org/10.1038/s41586-021-03380-y", "/path/to/papers")
    """
    def _download() -> DownloadResult:
        """Synchronous wrapper for download operation."""
        start_time = time.time()

        try:
            # Initialize client with configuration
            client = SciHubClient(
                email=EMAIL,
                output_dir=output_dir or DEFAULT_OUTPUT_DIR
            )

            # Download paper
            file_path = client.download_paper(identifier)

            if not file_path:
                return DownloadResult(
                    doi=identifier,
                    success=False,
                    error="Paper not found in any source"
                )

            # Get file details
            file_size = os.path.getsize(file_path)
            download_time = time.time() - start_time

            # Try to extract metadata for better display
            title = None
            year = None
            source = None

            # Check which source was used
            # We can infer from the source manager's last used source
            # For now, we'll mark as successful without detailed source info
            # (can be enhanced later if needed)

            return DownloadResult(
                doi=identifier,
                success=True,
                file_path=os.path.abspath(file_path),
                file_size=file_size,
                title=title,
                year=year,
                source=source,
                download_time=download_time
            )

        except Exception as e:
            return DownloadResult(
                doi=identifier,
                success=False,
                error=str(e),
                download_time=time.time() - start_time
            )

    # Run synchronous download in thread pool
    result = await asyncio.to_thread(_download)

    # Format and return result
    return format_download_result(result)


@mcp.tool()
async def paper_batch_download(
    identifiers: list[str],
    output_dir: Optional[str] = "./downloads"
) -> str:
    """
    Download multiple academic papers sequentially with progress reporting.

    This tool downloads a list of papers one by one, reporting progress after each
    download. It includes automatic rate limiting (2-second delay between downloads)
    to comply with API usage policies.

    Args:
        identifiers: List of DOIs or URLs to download (1-50 papers maximum)
        output_dir: Directory to save the PDFs (default: './downloads')

    Returns:
        Markdown-formatted summary with:
        - Total statistics (count, success rate, total time)
        - List of successful downloads (with file paths and sources)
        - List of failed downloads (with error messages)

    Examples:
        - paper_batch_download(["10.1038/nature12373", "10.1126/science.1234567"])
        - paper_batch_download(dois_list, "/path/to/papers")

    Note:
        Downloads are sequential (not parallel) to respect API rate limits.
        Each download has a 2-second delay to avoid overwhelming servers.
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
            email=EMAIL,
            output_dir=output_dir or DEFAULT_OUTPUT_DIR
        )

        for i, identifier in enumerate(identifiers):
            start_time = time.time()

            try:
                # Download paper
                file_path = client.download_paper(identifier)

                if not file_path:
                    results.append(DownloadResult(
                        doi=identifier,
                        success=False,
                        error="Paper not found in any source"
                    ))
                else:
                    # Get file details
                    file_size = os.path.getsize(file_path)
                    download_time = time.time() - start_time

                    results.append(DownloadResult(
                        doi=identifier,
                        success=True,
                        file_path=os.path.abspath(file_path),
                        file_size=file_size,
                        download_time=download_time
                    ))

            except Exception as e:
                results.append(DownloadResult(
                    doi=identifier,
                    success=False,
                    error=str(e),
                    download_time=time.time() - start_time
                ))

            # Add delay between downloads (except after last one)
            if i < len(identifiers) - 1:
                time.sleep(2)

        return results

    # Run batch download in thread pool
    results = await asyncio.to_thread(_batch_download)

    # Format and return results
    return format_batch_results(results)
