"""Download tools for single and batch paper downloads."""

import asyncio
import os
import time

from ..formatters import format_batch_results, format_download_result
from ..models import DownloadResult
from ..scihub_core.client import SciHubClient
from ..server import DEFAULT_OUTPUT_DIR, EMAIL, mcp


@mcp.tool()
async def paper_download(identifier: str, output_dir: str | None = "./downloads") -> str:
    """
    Download academic paper by DOI, arXiv ID, or URL.

    Sources: Sci-Hub, Unpaywall, arXiv, CORE (intelligent routing by year)
    Formats: DOI (10.xxx), arXiv (2301.00001), URLs

    Args:
        identifier: DOI, arXiv ID, or URL
        output_dir: Save directory (default: './downloads')

    Returns:
        Markdown with file path, metadata, source, or error message
    """

    def _download() -> DownloadResult:
        """Synchronous wrapper for download operation."""
        start_time = time.time()

        try:
            # Initialize client with configuration
            client = SciHubClient(email=EMAIL, output_dir=output_dir or DEFAULT_OUTPUT_DIR)  # type: ignore

            # Download paper
            file_path = client.download_paper(identifier)

            if not file_path:
                return DownloadResult(
                    doi=identifier, success=False, error="Paper not found in any source"
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
                download_time=download_time,
            )

        except Exception as e:
            return DownloadResult(
                doi=identifier, success=False, error=str(e), download_time=time.time() - start_time
            )

    # Run synchronous download in thread pool
    result = await asyncio.to_thread(_download)

    # Format and return result
    return format_download_result(result)


@mcp.tool()
async def paper_batch_download(
    identifiers: list[str], output_dir: str | None = "./downloads"
) -> str:
    """
    Download multiple papers sequentially (1-50 max).

    Sources: Sci-Hub, Unpaywall, arXiv, CORE
    Rate limit: 2-second delay between downloads

    Args:
        identifiers: List of DOIs, arXiv IDs, or URLs
        output_dir: Save directory (default: './downloads')

    Returns:
        Markdown summary with statistics, successes, and failures
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
        client = SciHubClient(email=EMAIL, output_dir=output_dir or DEFAULT_OUTPUT_DIR)  # type: ignore

        for i, identifier in enumerate(identifiers):
            start_time = time.time()

            try:
                # Download paper
                file_path = client.download_paper(identifier)

                if not file_path:
                    results.append(
                        DownloadResult(
                            doi=identifier, success=False, error="Paper not found in any source"
                        )
                    )
                else:
                    # Get file details
                    file_size = os.path.getsize(file_path)
                    download_time = time.time() - start_time

                    results.append(
                        DownloadResult(
                            doi=identifier,
                            success=True,
                            file_path=os.path.abspath(file_path),
                            file_size=file_size,
                            download_time=download_time,
                        )
                    )

            except Exception as e:
                results.append(
                    DownloadResult(
                        doi=identifier,
                        success=False,
                        error=str(e),
                        download_time=time.time() - start_time,
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
