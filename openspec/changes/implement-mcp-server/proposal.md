# Proposal: Implement MCP Server

## Summary

Convert the existing scihub-cli Python CLI tool into a FastMCP-based MCP server that enables LLM agents to download academic papers programmatically. This change reuses 95%+ of scihub-cli's battle-tested code while wrapping it with clean MCP tool interfaces.

## Motivation

**Problem**: Academic paper downloading currently requires manual CLI invocation, which is incompatible with LLM agent workflows.

**Solution**: Expose scihub-cli's capabilities as MCP tools that can be invoked by Claude Desktop and other MCP clients.

**Benefits**:
- LLM agents can autonomously download papers based on conversation context
- Preserves scihub-cli's intelligent multi-source routing (Sci-Hub + Unpaywall)
- Minimal code changes (zero modifications to existing scihub-cli code)
- Fast MVP delivery (4-6 hours estimated)

## Scope

### In Scope (MVP)
- **3 Core MCP Tools**:
  1. `paper_download` - Download single paper by DOI/URL
  2. `paper_batch_download` - Download multiple papers with progress reporting
  3. `paper_metadata` - Get paper metadata without downloading

- **Infrastructure**:
  - FastMCP server setup with stdio transport
  - Pydantic input/output models
  - Response formatters (Markdown for downloads, JSON for metadata)
  - Async wrappers using `asyncio.to_thread()`

- **Documentation**:
  - README with Claude Desktop setup instructions
  - Tool docstrings with parameter descriptions
  - Legal disclaimer

### Out of Scope (Future Enhancements)
- Streamable HTTP transport (only stdio for MVP)
- Parallel batch downloads (sequential only for rate limiting)
- Download history tracking (no database)
- Citation export (BibTeX, RIS)
- Advanced availability checking tool

### Non-Goals
- Modifying existing scihub-cli code (copy as-is)
- Migrating from requests to aiohttp (keep synchronous)
- Multi-tenant deployment (single-user only)

## Dependencies

### External
- FastMCP framework (>= 0.2.0)
- scihub-cli codebase (sibling directory `../scihub-cli/`)
- Unpaywall API (requires email configuration)
- Crossref API (no auth required)
- Sci-Hub mirrors (availability varies)

### Internal
- No dependencies on other OpenSpec changes (first implementation)

## Success Criteria

### Functional Requirements
- [ ] Successfully download papers using DOI input (e.g., `10.1038/nature12373`)
- [ ] Successfully download papers using URL input (e.g., `https://doi.org/...`)
- [ ] Batch download 10+ papers with success/failure summary
- [ ] Get metadata without downloading PDF
- [ ] Intelligent source routing works (<2021 → Sci-Hub, ≥2021 → Unpaywall)
- [ ] Files saved with correct format: `[YYYY] - Title.pdf`
- [ ] Clear error messages with actionable suggestions

### Integration Requirements
- [ ] Works in Claude Desktop with stdio transport
- [ ] Email configuration via environment variable
- [ ] Files save to specified output directory
- [ ] MCP Inspector testing successful

### Quality Requirements
- [ ] All tools have comprehensive docstrings
- [ ] Input validation via Pydantic models
- [ ] Legal disclaimer in README
- [ ] No code duplication (DRY principle)

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| FastMCP API changes | High | Low | Pin to stable version (>=0.2.0), review latest docs |
| Sci-Hub mirrors fail | High | Medium | Multi-mirror fallback (already in scihub-cli), Unpaywall backup |
| Rate limiting issues | Medium | High | Built-in 2s delays, batch size limit (50), clear error messages |
| Async wrapper complexity | Medium | Low | Use proven `asyncio.to_thread()` pattern, minimal changes |
| Email config missing | Medium | Medium | Validate on startup, clear error message with setup instructions |

## Alternatives Considered

### 1. TypeScript SDK Instead of FastMCP
**Rejected**: Would require complete rewrite of scihub-cli code (1-2 weeks vs 4-6 hours).

### 2. Migrate to aiohttp for True Async
**Rejected**: Adds risk and development time without meaningful performance gain for single-user scenario.

### 3. Streamable HTTP Transport
**Deferred**: stdio sufficient for MVP. Can add HTTP in future for multi-user deployments.

### 4. Base64-Encoded File Returns
**Rejected**: Bloats responses (1.3x larger), unnecessary when client has filesystem access.

## Implementation Strategy

### Phased Delivery

**Phase 1: Foundation** (1 hour)
- Create project structure
- Copy scihub-cli core modules
- Setup pyproject.toml with dependencies

**Phase 2: Core Tools** (2-2.5 hours)
- Implement Pydantic models
- Implement response formatters
- Implement `paper_download`
- Implement `paper_batch_download`

**Phase 3: Metadata Tool** (0.5-1 hour)
- Implement `paper_metadata`

**Phase 4: Testing & Documentation** (1-1.5 hours)
- MCP Inspector testing
- README documentation
- Basic integration tests

**Total Estimated Time**: 4.5-5.5 hours (buffer: 0.5-1 hour)

### Code Reuse Strategy
- Copy entire `scihub_cli/` directory to `src/paper_download_mcp/scihub_core/`
- Import existing classes: `SciHubClient`, `SourceManager`, `UnpaywallSource`
- Zero modifications to copied code (clean integration boundary)
- New MCP code in separate modules: `server.py`, `models.py`, `formatters.py`, `tools/`

## Open Questions

1. **Should we support custom mirror configuration in tool parameters?**
   - Lean toward: No for MVP (use scihub-cli defaults), add later if needed

2. **How verbose should progress reporting be for batch downloads?**
   - Lean toward: Simple percentage + count (e.g., "Downloading 5/10")

3. **Should we cache Crossref year lookups to improve performance?**
   - Lean toward: Yes, YearDetector already has caching (reuse as-is)

## Related Changes

None (this is the first change in the project)

## Stakeholders

- **Users**: Researchers using Claude Desktop to manage academic papers
- **Maintainer**: Project owner (user @oxidane)
- **Dependencies**: scihub-cli project (read-only access)

---

**Proposal Status**: Draft
**Author**: Claude (AI Assistant)
**Created**: 2025-12-02
**Target Completion**: 2025-12-02 (same day MVP)
