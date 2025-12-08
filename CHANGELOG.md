# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2025-12-08

### Added
- **arXiv Source Support**: New ArxivSource for downloading preprints from arXiv
  - Support multiple arXiv ID formats (YYMM.NNNNN, arxiv:YYMM.NNNNN)
  - Automatic format detection and validation
  - Free and open access to all arXiv papers
  - Integrated into intelligent routing chain
  - No API key or email required

### Changed
- **Improved Source Routing**: Enhanced intelligent routing with arXiv integration
  - arXiv IDs detected → arXiv prioritized first
  - Recent papers (≥2021): Unpaywall → arXiv → CORE → Sci-Hub
  - Older papers (<2021): Sci-Hub → Unpaywall → arXiv → CORE
  - Unknown year: Unpaywall → arXiv → CORE → Sci-Hub
- **Updated Tool Documentation**: All MCP tool docstrings now mention arXiv support
  - `paper_download`: Added arXiv ID examples and routing information
  - `paper_batch_download`: Added arXiv support in description
  - `paper_metadata`: Added arXiv metadata fetching information

### Technical Notes
- Better coverage for recent CS/Physics/Math preprints
- arXiv metadata fetched from official arXiv API
- 100% API compatible with previous versions

## [0.1.3] - 2025-12-08

### Changed
- **Core Cleanup**: Synced `scihub_core` with upstream scihub-cli (commit 23f6ea6)
  - Email is now optional - Unpaywall source only enabled when email is provided
  - Sci-Hub and CORE sources work without email
  - Simplified source initialization logic

### Removed
- **Unused Dependencies**: Removed cloudscraper, requests-html, fake-useragent
- **Unused Source Files**: Removed OpenAlex and Semantic Scholar source implementations (0% success rate)
- **Unused Network Files**: Removed bypass.py and proxy.py modules
- **Unused Utilities**: Removed stealth_utils.py (experimental features)
- Total reduction: ~1,356 lines of unused code removed

### Fixed
- Type annotations updated to use modern `X | None` syntax throughout scihub_core
- Import statements optimized for better compatibility

### Technical Notes
- This update maintains 100% API compatibility
- Email is still recommended for best results (enables Unpaywall source)
- Codebase is now leaner and more maintainable

## [0.1.2] - 2025-12-04

### Changed
- **Core Update**: Synced `scihub_core` with upstream [scihub-cli v0.2.0](https://github.com/Oxidane-bot/scihub-cli) (commit d531071)
  - Enhanced ruff configuration with additional rule sets (UP, B, C4, SIM)
  - Fixed 327 linting issues across codebase
  - Improved code quality with modern Python patterns
- **Type Annotations**: Migrated from `typing.List/Dict/Optional` to modern syntax (`list`, `dict`, `X | None`)
- **Code Style**: All code now formatted with consistent ruff style (double quotes, 100 char line length)

### Added
- New source implementations in scihub_core: CORE, OpenAlex, Semantic Scholar (available but not active)
- curl_cffi bypass support for Sci-Hub mirror access
- Intelligent rate limiting (2s delay per domain)
- Comprehensive ruff format configuration

### Fixed
- Year type handling in Unpaywall metadata (int instead of str for proper comparison)
- Import organization across all modules
- Deprecated typing imports replaced with modern equivalents

### Technical Notes
- This update maintains 100% API compatibility
- All MCP tools continue to work identically
- Core improvements focused on code quality and maintainability

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
