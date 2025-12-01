# Project Context

## Purpose

Convert the existing scihub-cli Python command-line tool into an MCP (Model Context Protocol) server that enables LLM agents to download academic papers programmatically through a standardized tool interface.

**Core Goals**:
- Preserve scihub-cli's intelligent multi-source routing (Sci-Hub + Unpaywall)
- Reuse 95%+ of existing battle-tested code with zero refactoring
- Provide clean MCP tool interfaces for paper download and metadata retrieval
- Enable Claude Desktop and other MCP clients to access academic papers

## Tech Stack

- **Language**: Python 3.10+
- **MCP Framework**: FastMCP (official Python SDK with decorator-style API)
- **Package Manager**: uv (as per user's global conventions)
- **Core Dependencies**:
  - fastmcp >= 0.2.0 (MCP server framework)
  - requests >= 2.25.1 (HTTP client, from scihub-cli)
  - beautifulsoup4 >= 4.9.3 (HTML parsing, from scihub-cli)
  - pydantic >= 2.0.0 (data validation)
- **Transport**: stdio (for local single-user scenarios, primarily Claude Desktop)

## Project Conventions

### Code Style
- Follow existing scihub-cli conventions (PEP 8 compliant)
- Use Pydantic for all input/output validation
- Type hints throughout new MCP code
- Docstrings for all public functions and tools
- No emojis in logs or console output (user preference)

### Architecture Patterns
- **High Cohesion, Low Coupling**: Each module has single responsibility
- **Dependency Injection**: Constructor-based injection for testability
- **Strategy Pattern**: Multi-source routing via abstract PaperSource interface
- **Async Wrapper Pattern**: Use `asyncio.to_thread()` to wrap synchronous scihub-cli code (zero modification approach)
- **MCP Tool Design**: One tool per capability, clear input/output contracts

### Testing Strategy
- Preserve existing scihub-cli unit tests (no modifications)
- Add MCP integration tests for tool invocations
- Use MCP Inspector for manual tool testing
- Mock external APIs (Sci-Hub, Unpaywall, Crossref) in automated tests

### Git Workflow
- Standard feature branch workflow
- Descriptive commit messages following OpenSpec conventions
- Use OpenSpec change tracking for all major features

## Domain Context

### Academic Paper Downloading
- **DOI (Digital Object Identifier)**: Unique identifier for academic papers (e.g., `10.1038/nature12373`)
- **Sci-Hub**: Shadow library providing free access to paywalled papers (legal gray area, frozen in 2020)
- **Unpaywall**: Legal open-access aggregator with API (requires email registration)
- **Crossref**: DOI resolution service with metadata API

### Intelligent Source Routing
scihub-cli implements year-based source selection:
- Papers published < 2021: Sci-Hub (better coverage, 85%+)
- Papers published >= 2021: Unpaywall (Sci-Hub frozen, only OA available)
- Year detection via Crossref API
- Automatic fallback between sources

### Metadata Extraction
Papers are saved with structured filenames: `[YYYY] - Paper Title.pdf`
- Metadata sources: Unpaywall API > HTML parsing > DOI-based fallback
- Filename sanitization (remove special characters, length limits)
- PDF validation (header check, minimum size threshold)

## Important Constraints

### Legal and Ethical
- Sci-Hub operates in legal gray area; must include prominent disclaimer
- Prioritize Unpaywall (legal) over Sci-Hub when both available
- Rate limiting to avoid abuse (2-second delays between downloads)
- Email required for Unpaywall API compliance

### Technical
- **Synchronous Code Preservation**: Existing scihub-cli uses synchronous `requests` library; must wrap with async (not rewrite)
- **Single-User Design**: MVP targets local Claude Desktop usage (not multi-tenant server)
- **File-Based Output**: MCP tools return file paths (not base64-encoded content)
- **Batch Size Limits**: Maximum 50 papers per batch to avoid timeouts
- **Email Configuration**: Must be provided via MCP server config (environment variable)

### Performance
- Mirror selection can take 5-10 seconds on first request (caches afterward)
- Typical download time: 2-5 seconds per paper
- Batch downloads are sequential (rate limiting compliance)
- Metadata-only queries: < 1 second

## External Dependencies

### APIs
- **Unpaywall API** (`https://api.unpaywall.org/v2/`)
  - Requires valid email in query params
  - Rate limit: ~100k requests/day
  - Returns JSON metadata and OA PDF URLs

- **Crossref API** (`https://api.crossref.org/works/{doi}`)
  - No authentication required
  - Used for year detection and fallback metadata
  - Rate limit: 50 requests/second

- **Sci-Hub Mirrors** (multiple domains, frequently changing)
  - No authentication required
  - HTML scraping for PDF URLs
  - Cloudflare protection on some mirrors
  - Mirror availability testing on startup

### Existing Codebase
- **scihub-cli** (`../scihub-cli/scihub_cli/`)
  - Source repository: ../scihub-cli (sibling directory)
  - All core modules will be copied to `src/paper_download_mcp/scihub_core/`
  - No modifications to copied code (clean integration boundary)

### MCP Ecosystem
- **Claude Desktop**: Primary deployment target
- **MCP Inspector**: Testing and debugging tool
- **FastMCP Framework**: Server implementation framework
