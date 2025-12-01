"""Metadata retrieval tool for academic papers."""

import asyncio

from ..server import mcp, EMAIL
from ..formatters import format_metadata
from ..scihub_core.sources.unpaywall_source import UnpaywallSource
from ..scihub_core.core.year_detector import YearDetector
from ..scihub_core.core.doi_processor import DOIProcessor


@mcp.tool()
async def paper_metadata(identifier: str) -> str:
    """
    Retrieve metadata for an academic paper without downloading the PDF.

    This tool queries metadata APIs (Unpaywall, Crossref) to get paper information
    including title, authors, year, journal, and open access status. It's useful
    for:
    - Checking paper availability before downloading
    - Getting paper details for citation purposes
    - Verifying DOI correctness
    - Quick paper lookups

    Args:
        identifier: DOI (e.g., '10.1038/nature12373') or URL (e.g., 'https://doi.org/...')

    Returns:
        JSON-formatted string containing paper metadata:
        - doi: Normalized DOI
        - title: Paper title
        - year: Publication year
        - authors: List of author names
        - journal: Journal name
        - is_oa: Open access status (boolean)
        - available_sources: List of sources where paper can be downloaded
        - [Additional fields from Unpaywall/Crossref APIs]

    Examples:
        - paper_metadata("10.1038/nature12373")
        - paper_metadata("https://doi.org/10.1126/science.1234567")

    Note:
        This is a fast, read-only operation (typically <1 second). No files are
        downloaded or created.
    """
    def _get_metadata() -> dict:
        """Synchronous wrapper for metadata retrieval."""
        # Normalize the identifier to DOI
        doi_processor = DOIProcessor()
        doi = doi_processor.normalize_doi(identifier)

        metadata = {
            "doi": doi,
            "available_sources": []
        }

        try:
            # Try Unpaywall first (primary metadata source)
            unpaywall = UnpaywallSource(email=EMAIL, timeout=10)
            unpaywall_data = unpaywall.get_metadata(doi)

            if unpaywall_data:
                metadata.update(unpaywall_data)

                # Determine available sources
                if unpaywall_data.get("is_oa"):
                    metadata["available_sources"].append("Unpaywall")

                # Always potentially available via Sci-Hub (for pre-2021 papers)
                year = unpaywall_data.get("year")
                if year and year < 2021:
                    metadata["available_sources"].append("Sci-Hub")

        except Exception as e:
            metadata["unpaywall_error"] = str(e)

        # Fallback to Crossref for year if not available
        if "year" not in metadata or not metadata["year"]:
            try:
                year_detector = YearDetector()
                year = year_detector.detect_year(doi)
                if year:
                    metadata["year"] = year

                    # Add Sci-Hub as potential source for old papers
                    if year < 2021 and "Sci-Hub" not in metadata["available_sources"]:
                        metadata["available_sources"].append("Sci-Hub")

            except Exception as e:
                metadata["crossref_error"] = str(e)

        # If no sources found and no year, it might be a very new or invalid DOI
        if not metadata["available_sources"]:
            metadata["error"] = (
                "Metadata not available from Unpaywall or Crossref. "
                "Please verify the DOI is correct."
            )

        return metadata

    # Run metadata retrieval in thread pool
    metadata = await asyncio.to_thread(_get_metadata)

    # Format and return as JSON
    return format_metadata(metadata)
