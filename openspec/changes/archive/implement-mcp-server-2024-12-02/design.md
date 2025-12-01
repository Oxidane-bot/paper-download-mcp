# Design Document: MCP Server Implementation

## Overview

This design document captures architectural decisions, trade-offs, and patterns for converting scihub-cli into an MCP server.

---

## Architecture Decisions

### AD-001: Code Reuse via Copy (Not Dependency)

**Decision**: Copy scihub-cli modules to `scihub_core/` instead of using it as a package dependency.

**Rationale**:
- **Isolation**: Changes to scihub-cli don't break MCP server
- **Simplicity**: No need to manage scihub-cli as PyPI package
- **Customization**: Can modify copied code if needed (though not planned for MVP)
- **Deployment**: Single self-contained package

**Trade-offs**:
- **Pro**: Complete control, no version conflicts
- **Pro**: Easy debugging (all code in one project)
- **Con**: Manual updates if scihub-cli improves
- **Con**: Code duplication (violates DRY at project level)

**Alternatives Considered**:
1. ✗ Make scihub-cli a dependency: Adds deployment complexity, version coupling
2. ✗ Git submodule: Confusing for contributors, deployment issues
3. ✓ Copy code: Simple, isolated, MVP-appropriate

---

### AD-002: FastMCP Framework Choice

**Decision**: Use FastMCP instead of official Anthropic Python SDK.

**Rationale**:
- **Developer Experience**: Decorator-style API is more Pythonic
- **Community Support**: 3.7k+ stars, active development
- **Official Status**: FastMCP 1.0 was merged into official SDK; maintains official support
- **Feature Completeness**: Built-in testing, auth, deployment tools
- **Documentation**: Comprehensive guides and examples

**Trade-offs**:
- **Pro**: Faster development (30-40% less boilerplate)
- **Pro**: Better documentation and examples
- **Pro**: Production-ready features (auth, deployment)
- **Con**: Slightly more dependencies
- **Con**: Potential divergence from official SDK in future

**Evidence**:
- [FastMCP vs SDK Comparison](https://medium.com/@FrankGoortani/comparing-model-context-protocol-mcp-server-frameworks-03df586118fd)
- User preference for Python + FastMCP confirmed

---

### AD-003: Async Wrapper Pattern (No Code Rewrite)

**Decision**: Use `asyncio.to_thread()` to wrap synchronous scihub-cli code instead of converting to async/await.

**Rationale**:
- **Zero Risk**: No modifications to battle-tested code
- **Fast Delivery**: Avoids 3-4 hours of async conversion work
- **Sufficient Performance**: Single-user scenario doesn't need true async
- **Clean Boundary**: Sync logic isolated in `_download()` wrapper functions

**Pattern**:
```python
@mcp.tool()
async def paper_download(params):
    def _sync_download():
        # All sync code here
        client = SciHubClient()
        return client.download_paper(params.identifier)

    # Wrap with async
    result = await asyncio.to_thread(_sync_download)
    return format_result(result)
```

**Trade-offs**:
- **Pro**: Zero code changes to scihub-cli
- **Pro**: Faster MVP delivery
- **Pro**: Easier debugging (familiar sync patterns)
- **Con**: Not "true" async (thread pool overhead)
- **Con**: Can't parallelize batch downloads easily

**Future Enhancement**: Migrate to aiohttp + true async if performance becomes issue.

---

### AD-004: stdio Transport (Not HTTP)

**Decision**: Use stdio transport for MVP, defer streamable HTTP.

**Rationale**:
- **User Scenario**: Primary use case is Claude Desktop (single-user, local)
- **Simplicity**: No network configuration, port management, auth
- **Performance**: stdio is fastest for local communication
- **Security**: No network exposure concerns

**Trade-offs**:
- **Pro**: Simplest deployment (just configure Claude Desktop)
- **Pro**: Best performance for local usage
- **Pro**: No security/auth complexity
- **Con**: Cannot support multi-user scenarios
- **Con**: Cannot deploy as web service

**Migration Path**: Can add HTTP transport later without breaking stdio users.

---

### AD-005: File Path Return (Not Base64)

**Decision**: Return absolute file paths instead of base64-encoded PDF content.

**Rationale**:
- **MCP Client Access**: Claude Desktop has filesystem access
- **Response Size**: File paths are tiny (vs 1.3x bloat for base64)
- **Performance**: No encoding/decoding overhead
- **Simplicity**: Existing scihub-cli already saves files

**Trade-offs**:
- **Pro**: Minimal response size
- **Pro**: No encoding overhead
- **Pro**: Files persisted on disk (useful for users)
- **Con**: Assumes client has filesystem access (true for Claude Desktop)
- **Con**: Not suitable for remote API scenarios (future HTTP transport can add base64)

---

### AD-006: Email Configuration via Environment Variable

**Decision**: Require email in `SCIHUB_CLI_EMAIL` env var (Claude Desktop config).

**Rationale**:
- **Unpaywall Compliance**: API requires valid email
- **Single-User Design**: One email per MCP server instance is appropriate
- **Claude Desktop Pattern**: Standard way to configure MCP servers
- **Security**: Keeps email out of tool parameters (less exposure)

**Configuration Priority**:
1. Environment variable `SCIHUB_CLI_EMAIL` (required)
2. Fallback to `~/.scihub-cli/config.json` (backward compatibility)
3. No default value (explicit configuration required)

**Validation**: Check on server startup, fail fast with clear error message.

---

## Component Design

### Layer Architecture

```
┌─────────────────────────────────────────┐
│     MCP Client (Claude Desktop)         │
└────────────────┬────────────────────────┘
                 │ stdio
                 │
┌────────────────▼────────────────────────┐
│         FastMCP Server Layer            │
│  - server.py (entry point)              │
│  - Tool registration (@mcp.tool)        │
│  - Email validation                     │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         MCP Tools Layer                 │
│  - tools/download.py (2 tools)          │
│  - tools/metadata.py (1 tool)           │
│  - Async wrappers (asyncio.to_thread)   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     Data Models & Formatters            │
│  - models.py (Pydantic input/output)    │
│  - formatters.py (Markdown/JSON)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     scihub_core (Copied Code)           │
│  - client.py (SciHubClient)             │
│  - sources/ (Sci-Hub, Unpaywall)        │
│  - core/ (routing, parsing, download)   │
│  - config/ (settings, mirrors)          │
│  - utils/ (retry, logging)              │
└─────────────────────────────────────────┘
```

**Layer Responsibilities**:
1. **FastMCP Server**: Protocol handling, tool registration, config validation
2. **MCP Tools**: Request parsing, response formatting, async coordination
3. **Models & Formatters**: Data validation, output serialization
4. **scihub_core**: All academic paper logic (unchanged from scihub-cli)

**Dependency Direction**: Top-down only (no circular dependencies).

---

### Data Flow

#### Single Paper Download Flow

```
1. User: "Download paper 10.1038/nature12373"
   │
   ▼
2. Claude Desktop → MCP Request (stdio)
   {
     "tool": "paper_download",
     "params": {"identifier": "10.1038/nature12373"}
   }
   │
   ▼
3. FastMCP Server → Tool Invocation
   - Validate params with Pydantic
   - Call paper_download()
   │
   ▼
4. Tool Layer → Async Wrapper
   - Wrap sync call in asyncio.to_thread()
   - Initialize SciHubClient(email=EMAIL)
   │
   ▼
5. scihub_core → Paper Download
   - Detect year via Crossref (2013)
   - Route to Sci-Hub (year < 2021)
   - Parse HTML for PDF URL
   - Download PDF
   - Validate (header, size)
   - Extract metadata
   - Save as "[2013] - Paper Title.pdf"
   │
   ▼
6. Tool Layer → Format Response
   - Build DownloadResult object
   - Format as Markdown
   │
   ▼
7. FastMCP Server → MCP Response (stdio)
   {
     "content": "# Paper Downloaded...",
     "isError": false
   }
   │
   ▼
8. Claude Desktop → Display to User
   "Successfully downloaded [2013] - Paper Title.pdf"
```

---

### Error Handling Architecture

**Three-Layer Strategy**:

1. **Input Validation** (Pydantic):
   - Type checking (string, int, list)
   - Range validation (min/max length, list size)
   - Pattern matching (email format)
   - Returns: HTTP 400 with validation error

2. **Business Logic Errors** (scihub_core):
   - Paper not found (404 from sources)
   - Network timeout (requests.Timeout)
   - Rate limiting (429 from APIs)
   - Returns: None or raises exception

3. **Tool Layer** (MCP tools):
   - Catch exceptions from scihub_core
   - Map to user-friendly Markdown errors
   - Include actionable suggestions
   - Returns: Error response with `isError: false` (soft failure)

**Example Error Flow**:
```python
# Layer 1: Pydantic catches invalid input
try:
    params = DownloadPaperInput(**raw_params)
except ValidationError as e:
    raise  # FastMCP handles as protocol error

# Layer 2: scihub_core returns None on failure
result = client.download_paper(doi)  # Returns None if not found

# Layer 3: Tool layer formats error
if result is None:
    return """# Download Failed

**DOI**: {doi}
**Error**: Paper not found in any source

Suggestions:
- Verify DOI is correct
- Try paper_metadata for availability check
"""
```

---

## Performance Considerations

### Response Time Targets

| Operation | Target | Typical | Max Acceptable |
|-----------|--------|---------|----------------|
| Get Metadata | < 1s | 0.5s | 2s |
| Single Download | < 5s | 2-3s | 10s |
| Batch (10 papers) | < 40s | 25-30s | 60s |

**Bottlenecks**:
1. **Mirror Selection** (first request only): 5-10s
   - Mitigation: Cached after first success
2. **Crossref Year Lookup**: 0.5-1s per paper
   - Mitigation: YearDetector caches results
3. **Sci-Hub HTML Parsing**: 1-2s
   - Mitigation: Efficient BeautifulSoup selectors
4. **Rate Limiting Delays**: 2s between batch downloads
   - Mitigation: User expectation management (progress reporting)

---

### Scalability Limits (MVP)

**By Design**:
- Single-user (stdio transport)
- Sequential downloads (rate limiting compliance)
- No database (stateless except YearDetector cache)
- No caching layer (except in-memory)

**Capacity**:
- Concurrent users: 1 (Claude Desktop session)
- Papers per batch: 50 (validation limit)
- Daily download estimate: ~200-500 papers (manual usage)

**Future Scaling**:
- Add HTTP transport for multi-user
- Add Redis/SQLite for persistent caching
- Add async downloads with rate limiter

---

## Security and Compliance

### Threat Model

**Out of Scope** (single-user, local deployment):
- Authentication (stdio to trusted local client)
- Authorization (user controls what downloads)
- Encryption (local-only, no network transmission)
- Rate limiting abuse (single user, built-in delays)

**In Scope**:
- Input validation (prevent injection attacks)
- Filesystem safety (validate output paths)
- Email privacy (env var, not in logs)
- Legal compliance (prominent disclaimer)

### Input Validation

**DOI/URL Sanitization**:
- Regex pattern: `10\.\d{4,}(?:\.\d+)*\/(?:(?!["&\'<>])\S)+`
- No shell command injection (no subprocess usage with user input)
- Path traversal prevention (validate output_dir is absolute)

**Email Validation**:
- Basic pattern check: `^[\w\.-]+@[\w\.-]+\.\w+$`
- Passed as URL parameter (properly encoded)
- Not logged or stored

### Legal Compliance

**README Disclaimer**:
```
## Legal Notice

This tool provides access to academic papers through multiple sources:
- **Unpaywall**: Legal open-access aggregator (recommended)
- **Sci-Hub**: Operates in legal gray area (use at own risk)

Users are responsible for compliance with applicable copyright laws.
This tool is intended for research and educational purposes only.

By using this tool, you acknowledge the legal risks and agree to use
responsibly in accordance with your local laws.
```

**Source Prioritization**:
- Prefer Unpaywall (legal) when both sources have content
- Route 2021+ papers to Unpaywall first (compliance-friendly)
- Log source used in response (transparency)

---

## Testing Strategy

### Testing Pyramid

```
        ┌─────────────┐
        │ E2E Tests   │  ← Claude Desktop integration (1-2 tests)
        └─────────────┘
       ┌───────────────┐
       │ Integration   │   ← MCP Inspector tests (5-10 tests)
       │    Tests      │
       └───────────────┘
      ┌─────────────────┐
      │  Unit Tests     │    ← Pydantic, formatters (20-30 tests)
      └─────────────────┘
     ┌───────────────────┐
     │  Linting/Types    │     ← ruff, mypy (continuous)
     └───────────────────┘
```

### Test Cases

**Unit Tests** (fast, no external deps):
- Pydantic validation (valid/invalid inputs)
- Formatter output (Markdown/JSON structure)
- Helper functions (DOI normalization, filename sanitization)

**Integration Tests** (mocked external APIs):
- Tool invocation with mocked SciHubClient
- Error handling paths
- Progress reporting (batch downloads)

**MCP Inspector Tests** (manual, real APIs):
- Each tool with valid inputs
- Error scenarios (invalid DOI, missing email)
- Performance checks (response times)

**E2E Tests** (Claude Desktop):
- Full conversation workflow
- File system verification
- User experience validation

---

## Deployment and Operations

### Installation

**Developer Setup**:
```bash
cd paper-download-mcp
uv sync
uv run python -m paper_download_mcp.server
```

**User Installation**:

No manual installation required. Claude Desktop will use `uvx` to automatically manage the environment.

**Claude Desktop Configuration** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {
        "SCIHUB_CLI_EMAIL": "researcher@university.edu"
      }
    }
  }
}
```

**Alternative: Manual Installation** (optional):
```bash
# For users who prefer manual installation
uv tool install paper-download-mcp

# Then use simpler Claude Desktop config
{
  "mcpServers": {
    "paper-download": {
      "command": "paper-download-mcp",
      "env": {"SCIHUB_CLI_EMAIL": "researcher@university.edu"}
    }
  }
}
```

### Monitoring

**Logging** (inherited from scihub-cli):
- INFO: Download start/complete
- WARNING: Mirror fallback, retries
- ERROR: Failed downloads, API errors

**No Metrics** (MVP):
- No telemetry
- No error tracking (Sentry, etc.)
- No performance monitoring

**Future Enhancements**:
- Optional telemetry (opt-in)
- Error reporting to maintainer
- Usage statistics

---

## Future Enhancements (Post-MVP)

### Phase 2 Features

1. **Parallel Batch Downloads**:
   - Migrate to aiohttp for true async
   - Smart rate limiting (adaptive delays)
   - Estimated time ~6-8 hours

2. **Download History**:
   - SQLite database
   - Track downloads, avoid duplicates
   - Query history via new tool
   - Estimated time ~4-6 hours

3. **Availability Checker Tool**:
   - `paper_check_availability`
   - Fast source checking without download
   - Estimated time ~2-3 hours

### Phase 3 Features

1. **Citation Export**:
   - BibTeX, RIS, EndNote formats
   - Extract from metadata
   - Estimated time ~3-4 hours

2. **Streamable HTTP Transport**:
   - Multi-user support
   - Authentication (API keys)
   - CORS configuration
   - Estimated time ~8-12 hours

3. **Full-Text Search**:
   - Index PDF content
   - Search within papers
   - Estimated time ~10-15 hours

---

## Risks and Mitigations

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Sci-Hub mirrors blocked | High | Medium | Multi-mirror list, Unpaywall fallback |
| FastMCP breaking changes | High | Low | Pin versions, monitor releases |
| Python async complexity | Medium | Low | Use proven patterns, minimal async surface |
| Dependency conflicts | Medium | Low | Use uv lock file, minimal deps |

### Operational Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Unpaywall API downtime | High | Low | Fallback to Crossref for metadata |
| Rate limiting | Medium | Medium | Built-in delays, clear errors |
| Email misconfiguration | Medium | Medium | Startup validation, clear error |
| Large batch timeouts | Low | Medium | 50-paper limit, progress reporting |

### Legal Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Sci-Hub legal issues | High | Low | Prominent disclaimer, user responsibility |
| Copyright complaints | Medium | Low | Prioritize Unpaywall, legal notice |
| API ToS violations | Low | Low | Respect rate limits, provide email |

---

## Success Metrics

**MVP Success** (within 4-6 hours):
- [ ] All 3 tools implemented and tested
- [ ] MCP Inspector testing successful
- [ ] Claude Desktop integration working
- [ ] README documentation complete
- [ ] OpenSpec validation passes

**User Success** (post-launch):
- User can download papers in natural conversation
- Download success rate > 80%
- Average response time < 5s per paper
- Zero crashes or protocol errors
- Clear error messages for all failures

**Technical Success**:
- Zero modifications to scihub_core code
- All async wrappers use consistent pattern
- Pydantic validation covers all inputs
- Tests achieve >70% coverage

---

## References

- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [scihub-cli Repository](../scihub-cli/)
- [Unpaywall API Docs](https://unpaywall.org/products/api)
- [Crossref API Docs](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)

---

**Document Status**: Draft
**Last Updated**: 2025-12-02
**Next Review**: After MVP completion
