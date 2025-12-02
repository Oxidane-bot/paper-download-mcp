# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-12-02

### Changed
- **Environment Variable Rename**: `SCIHUB_CLI_EMAIL` → `PAPER_DOWNLOAD_EMAIL` (backward compatible)
- **Environment Variable Rename**: `SCIHUB_OUTPUT_DIR` → `PAPER_DOWNLOAD_OUTPUT_DIR` (backward compatible)
- Updated all documentation to use new environment variable names

### Added
- Reference to [scihub-cli](https://github.com/Oxidane-bot/scihub-cli) project in README
- Backward compatibility support: old environment variable names still work

### Fixed
- Corrected scihub-cli GitHub repository URL in documentation

## [0.1.0] - 2024-12-02

### Added
- Initial release of paper-download-mcp
- MCP server with three tools for academic paper management:
  - `paper_download`: Download single papers by DOI or URL
  - `paper_batch_download`: Download multiple papers with progress tracking
  - `paper_metadata`: Retrieve paper metadata without downloading
- Intelligent multi-source routing:
  - Sci-Hub for papers published before 2021
  - Unpaywall for papers published 2021 or later
  - Automatic fallback between sources
- Integration with Claude Desktop via MCP protocol
- Support for PDF validation and metadata extraction
- Batch download with 2-second rate limiting for API compliance
- Comprehensive error handling and user-friendly error messages
- MIT License

### Documentation
- Complete README with installation and usage instructions
- MCP Inspector testing guide
- Legal disclaimer for academic paper access
- Upstream sync workflow for maintainers
- Implementation summary and deployment history

### Infrastructure
- Built with official Anthropic MCP SDK (`mcp[cli]>=1.0.0`)
- Python 3.10+ support
- `uvx` deployment support for zero-installation usage
- Type-safe implementation with Pydantic models

[0.1.1]: https://github.com/Oxidane-bot/paper-download-mcp/releases/tag/v0.1.1
[0.1.0]: https://github.com/Oxidane-bot/paper-download-mcp/releases/tag/v0.1.0
