# Paper Download MCP Server

MCP server for downloading academic papers from multiple sources (Sci-Hub + Unpaywall).

## Installation

```bash
uvx paper-download-mcp
```

## Configuration

Set the `SCIHUB_CLI_EMAIL` environment variable (required for Unpaywall API).

## Claude Desktop Setup

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {
        "SCIHUB_CLI_EMAIL": "your-email@university.edu"
      }
    }
  }
}
```

## Tools

- `paper_download` - Download a single paper by DOI or URL
- `paper_batch_download` - Download multiple papers with progress reporting
- `paper_metadata` - Get paper metadata without downloading

## Legal Notice

This tool provides access to academic papers through multiple sources:
- **Unpaywall**: Legal open-access aggregator (recommended)
- **Sci-Hub**: Operates in legal gray area (use at own risk)

Users are responsible for compliance with applicable copyright laws.
This tool is intended for research and educational purposes only.
