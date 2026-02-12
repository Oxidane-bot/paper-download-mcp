# Paper Download MCP Server

[![PyPI version](https://badge.fury.io/py/paper-download-mcp.svg)](https://badge.fury.io/py/paper-download-mcp)
[![Python Version](https://img.shields.io/pypi/pyversions/paper-download-mcp.svg)](https://pypi.org/project/paper-download-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/paper-download-mcp)](https://pepy.tech/project/paper-download-mcp)

MCP server for downloading academic papers from multiple sources with intelligent routing.

> **Note**: This project is built on top of [scihub-cli](https://github.com/Oxidane-bot/scihub-cli), adapting its core functionality for MCP integration. If you find this useful, consider starring both projects!

## Features

- **Multi-Source Support**: Downloads from multiple sources with automatic fallback
  - **arXiv**: Prioritized for preprints (free, no API key needed)
  - **Unpaywall**: For open access papers (requires email)
  - **Direct PDF**: Handles direct PDF URLs
  - **PMC**: PubMed Central articles
  - **HTML Landing**: Extracts PDF links from article pages
  - **Sci-Hub**: Fallback for older papers (coverage-driven)
  - **CORE**: Additional OA fallback
- **Intelligent Routing**: Priority-based source selection with year-aware routing
- **2 MCP Tools**:
  - `paper_download` - Download one or more papers by DOI/arXiv ID/URL
  - `paper_get_metadata` - Get paper metadata without downloading PDF
- **Clean Filenames**: `[YYYY] - Paper Title.pdf` format
- **Optional Markdown Conversion**: Convert downloaded PDFs to Markdown (`to_markdown`)
- **Rate Limiting**: Built-in delays for API compliance
- **Comprehensive Error Messages**: Actionable suggestions on failures

## Installation

### For Users (Recommended)

No manual installation required! Use `uvx` for automatic environment management:

```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {
        "PAPER_DOWNLOAD_EMAIL": "your-email@university.edu"
      }
    }
  }
}
```

### For Developers

```bash
git clone <repository-url>
cd paper-download-mcp
uv sync
uv run python -m paper_download_mcp.server
```

## Configuration

### Required Environment Variables

- `PAPER_DOWNLOAD_EMAIL`: Your email address (required for Unpaywall API compliance)
  - Example: `researcher@university.edu`
  - Used for Unpaywall API tracking and contact purposes

### Optional Environment Variables

- `PAPER_DOWNLOAD_OUTPUT_DIR`: Default output directory (default: `./downloads`)

### Claude Desktop Setup

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {
        "PAPER_DOWNLOAD_EMAIL": "your-email@university.edu",
        "PAPER_DOWNLOAD_OUTPUT_DIR": "/path/to/papers"
      }
    }
  }
}
```

After configuration, restart Claude Desktop.

## Tools

### paper_download

Download one or more academic papers by DOI, arXiv ID, or URL.
The tool runs sequentially in one call and supports optional PDF-to-Markdown conversion.

**Parameters:**
- `identifiers` (required): List of identifiers (DOI/arXiv ID/URL), 1-50 items
- `output_dir` (optional): Output directory (default: `./downloads`)
- `to_markdown` (optional): Convert downloaded PDFs to Markdown (default: `false`)
- `md_output_dir` (optional): Markdown output directory (default: `<output_dir>/md`)

**Example:**
```
paper_download([
  "10.1038/nature12373",
  "2301.00001"
])
```

**Returns:**
- Markdown summary with total/success/failure statistics
- Per-item success details (title, path, source, markdown status)
- Per-item failure reasons and suggestions

**Notes:**
- Single-paper download is just a one-item `identifiers` list.
- Requests are sequential with a 2-second delay between items.

### paper_get_metadata

Retrieve paper metadata without downloading the PDF.

**Parameters:**
- `identifier` (required): DOI, arXiv ID, or URL

**Example:**
```
paper_get_metadata("10.1038/nature12373")
```

**Returns:**
- JSON with paper details:
  - DOI, title, year, authors, journal
  - Open access status
  - Available download sources

## How It Works

### Intelligent Source Routing

The server uses priority routing to keep fast sources first:

1. **arXiv IDs/URLs**: Try arXiv first, then OA sources if needed
2. **DOIs (year < 2021)**: OA sources first, Sci-Hub last
3. **DOIs (year ≥ 2021)**: OA sources only (Sci-Hub has no coverage)
4. **Year unknown**: OA sources first, Sci-Hub last

### Download Process

1. Normalize DOI from URL/identifier
2. Detect publication year via Crossref API (DOIs only)
3. Route to appropriate source based on priority/year
4. Download PDF with retry on failure
5. Validate file (PDF header, size check)
6. Generate filename: `[YYYY] - Title.pdf`
7. Return absolute file path

### Rate Limiting

- 2-second delay between items within one `paper_download` request
- Respects Unpaywall API limits (~100k requests/day)
- Built-in exponential backoff retry (3 attempts max)

## Troubleshooting

### "PAPER_DOWNLOAD_EMAIL environment variable is required"

**Solution**: Set the email in your Claude Desktop config (see Configuration section above).

### "Paper not found in any source"

**Possible causes:**
- Invalid or incorrect DOI
- Paper too recent (not yet indexed)
- Paper behind paywall with no open access version
- Sci-Hub mirrors temporarily unavailable

**Solutions:**
- Verify DOI on doi.org
- Use `paper_get_metadata` to check availability
- Try again later (mirrors may recover)

### Download times out

**Causes:**
- Slow network connection
- Sci-Hub mirror selection taking too long
- Large PDF file

**Solutions:**
- Check internet connection
- Retry (mirror selection is cached after first success)
- Single papers typically complete in <15 seconds

### Downloaded file is corrupted

The server validates PDFs before returning. If you encounter corruption:
1. Check disk space
2. Verify file permissions in output directory
3. Try different paper (may be source issue)

## Testing

### MCP Inspector

Test the server with MCP Inspector:

```bash
export PAPER_DOWNLOAD_EMAIL=test@example.com
npx @modelcontextprotocol/inspector uv run python -m paper_download_mcp.server
```

### Unit Tests

```bash
uv run pytest
```

## Legal Notice

**IMPORTANT**: This tool provides access to academic papers through multiple sources:

- **Unpaywall** (https://unpaywall.org): Legal open-access aggregator operated by OurResearch. Recommended and prioritized when available.

- **Sci-Hub**: Operates in a legal gray area. While it provides access to research, it may violate copyright laws in some jurisdictions. Use at your own risk.

**User Responsibilities:**
- You are responsible for compliance with applicable copyright laws in your jurisdiction
- This tool is intended for research and educational purposes only
- The maintainers assume no liability for how you use this tool
- When possible, prefer legal open-access sources (Unpaywall)

By using this tool, you acknowledge these legal considerations and agree to use it responsibly.

## Project Structure

```
paper-download-mcp/
├── src/
│   └── paper_download_mcp/
│       ├── server.py           # FastMCP entry point
│       ├── models.py           # Pydantic input schemas
│       ├── formatters.py       # Markdown/JSON formatters
│       ├── tools/
│       │   ├── download.py     # Download tool
│       │   └── metadata.py     # Metadata tool
│       └── scihub_core/        # Copied from scihub-cli
├── pyproject.toml
├── README.md
└── .gitignore
```

## Architecture

### Layer Architecture

1. **FastMCP Server Layer**: Protocol handling, tool registration, config validation
2. **MCP Tools Layer**: Request parsing, response formatting, async coordination
3. **Models & Formatters**: Data validation, output serialization
4. **scihub_core Layer**: Academic paper logic (unchanged from scihub-cli)

### Async Pattern

All tools use `asyncio.to_thread()` to wrap synchronous scihub-cli code:

```python
@mcp.tool()
async def paper_download(identifiers: list[str], ...):
    def _sync_download_many():
        # Synchronous scihub-cli code
        return download_many_sync(identifiers=identifiers, ...)

    # Run in thread pool
    results = await asyncio.to_thread(_sync_download_many)
    return format_batch_results(results)
```

This preserves the battle-tested scihub-cli code without modifications.

## Performance

| Operation | Target | Typical | Max |
|-----------|--------|---------|-----|
| Get Metadata | <1s | 0.5s | 2s |
| Download (1 paper) | <5s | 2-3s | 10s |
| Download (10 papers) | <40s | 25-30s | 60s |

**Note**: First download may take longer (5-10s) due to mirror selection. Subsequent downloads use cached mirror.

## Contributing

### For Maintainers: Syncing from scihub-cli

The `scihub_core/` directory contains code copied from the upstream [scihub-cli](../scihub-cli) project. When bugs are fixed or features added to scihub-cli:

**Workflow:**
1. Fix/implement in `scihub-cli` project first
2. Run tests and commit to scihub-cli
3. Copy updated files to `paper-download-mcp/src/paper_download_mcp/scihub_core/`
4. Test MCP server functionality
5. Commit with message referencing upstream commit:
   ```
   sync: Update <file> from scihub-cli (<description>)

   Synced from scihub-cli commit <hash>
   <details of changes>
   ```

**Last sync**: scihub-cli@9787efc (2024-12-02) - Fixed year type bug in UnpaywallSource

## License

MIT License - See LICENSE file for details

## Credits

- Built with [FastMCP](https://gofastmcp.com)
- Uses [scihub-cli](https://github.com/Oxidane-bot/scihub-cli) as core download engine
- Metadata from [Unpaywall](https://unpaywall.org) and [Crossref](https://www.crossref.org)

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Open an issue on GitHub (include error messages and steps to reproduce)

---

**Disclaimer**: This tool is provided as-is for research and educational purposes. Users assume all responsibility for compliance with applicable laws and regulations.
