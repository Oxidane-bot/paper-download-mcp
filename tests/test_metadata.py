#!/usr/bin/env python3
"""Test paper_metadata tool with a real API call."""

import asyncio
import os
import sys

import pytest

# Set email before imports
os.environ["SCIHUB_CLI_EMAIL"] = "test@university.edu"

sys.path.insert(0, "src")

from paper_download_mcp.scihub_core.sources.unpaywall_source import UnpaywallSource


@pytest.mark.asyncio
async def test_unpaywall_api():
    """Test Unpaywall API directly."""
    print("=" * 60)
    print("Testing Unpaywall API")
    print("=" * 60)

    doi = "10.1038/nature12373"
    print(f"\nQuerying metadata for DOI: {doi}")

    def _get_metadata():
        unpaywall = UnpaywallSource(email=os.environ["SCIHUB_CLI_EMAIL"], timeout=10)
        return unpaywall.get_metadata(doi)

    try:
        metadata = await asyncio.to_thread(_get_metadata)

        if metadata:
            print("\n✓ Successfully retrieved metadata!")
            print("\nKey fields:")
            for key in ["doi", "title", "year", "journal", "is_oa"]:
                if key in metadata:
                    value = metadata[key]
                    if isinstance(value, str) and len(value) > 60:
                        value = value[:60] + "..."
                    print(f"  {key}: {value}")

            print(f"\nTotal fields: {len(metadata)}")
            return True
        else:
            print("\n✗ No metadata returned")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_unpaywall_api())
    sys.exit(0 if success else 1)
