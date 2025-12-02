# Paper Download MCP Server

[![PyPI version](https://badge.fury.io/py/paper-download-mcp.svg)](https://badge.fury.io/py/paper-download-mcp)
[![Python Version](https://img.shields.io/pypi/pyversions/paper-download-mcp.svg)](https://pypi.org/project/paper-download-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/paper-download-mcp)](https://pepy.tech/project/paper-download-mcp)

MCP server for downloading academic papers from multiple sources with intelligent routing.

> **Note**: This project is built on top of [scihub-cli](https://github.com/Oxidane-bot/scihub-cli), adapting its core functionality for MCP integration. If you find this useful, consider starring both projects!

## Features

- **Multi-Source Support**: Downloads from Sci-Hub and Unpaywall with automatic fallback
- **Intelligent Routing**: Year-based source selection (<2021 → Sci-Hub, ≥2021 → Unpaywall)
- **3 MCP Tools**:
  - `paper_download` - Download single paper by DOI or URL
  - `paper_batch_download` - Download multiple papers with progress reporting
  - `paper_metadata` - Get paper metadata without downloading PDF
- **Clean Filenames**: `[YYYY] - Paper Title.pdf` format
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

Download a single academic paper by DOI or URL.

**Parameters:**
- `identifier` (required): DOI or URL (e.g., `10.1038/nature12373`)
- `output_dir` (optional): Output directory (default: `./downloads`)

**Example:**
```
Download the paper 10.1038/nature12373
```

**Returns:**
- Markdown with download details (file path, size, source, timing)
- Error message with suggestions if download fails

### paper_batch_download

Download multiple papers sequentially with progress reporting.

**Parameters:**
- `identifiers` (required): List of DOIs or URLs (1-50 maximum)
- `output_dir` (optional): Output directory (default: `./downloads`)

**Example:**
```
Download these papers: 10.1038/nature12373, 10.1126/science.1234567
```

**Returns:**
- Markdown summary with statistics
- List of successful downloads
- List of failed downloads with errors

**Note:** Downloads are sequential with 2-second delays for rate limiting.

### paper_metadata

Retrieve paper metadata without downloading the PDF.

**Parameters:**
- `identifier` (required): DOI or URL

**Example:**
```
Get metadata for 10.1038/nature12373
```

**Returns:**
- JSON with paper details:
  - DOI, title, year, authors, journal
  - Open access status
  - Available download sources

## How It Works

### Intelligent Source Routing

The server uses year-based routing to maximize download success:

1. **Publication year < 2021**: Try Sci-Hub first (frozen in 2020), fallback to Unpaywall
2. **Publication year ≥ 2021**: Try Unpaywall first (legal OA), fallback to Sci-Hub
3. **Year unknown**: Conservative approach (Unpaywall → Sci-Hub)

### Download Process

1. Normalize DOI from URL/identifier
2. Detect publication year via Crossref API
3. Route to appropriate source based on year
4. Download PDF with retry on failure
5. Validate file (PDF header, size check)
6. Generate filename: `[YYYY] - Title.pdf`
7. Return absolute file path

### Rate Limiting

- 2-second delay between batch downloads
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
- Use `paper_metadata` to check availability
- Try again later (mirrors may recover)

### Download times out

**Causes:**
- Slow network connection
- Sci-Hub mirror selection taking too long
- Large PDF file

**Solutions:**
- Check internet connection
- Retry (mirror selection is cached after first success)
- Single papers typically complete in <10 seconds

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
│       │   ├── download.py     # Download tools
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
async def paper_download(...):
    def _sync_download():
        # Synchronous scihub-cli code
        client = SciHubClient()
        return client.download_paper(doi)

    # Run in thread pool
    result = await asyncio.to_thread(_sync_download)
    return format_result(result)
```

This preserves the battle-tested scihub-cli code without modifications.

## Performance

| Operation | Target | Typical | Max |
|-----------|--------|---------|-----|
| Get Metadata | <1s | 0.5s | 2s |
| Single Download | <5s | 2-3s | 10s |
| Batch (10 papers) | <40s | 25-30s | 60s |

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
