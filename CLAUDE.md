<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

---

# Paper Download MCP Server - Implementation Guide

## Project Overview

**Purpose**: Convert scihub-cli Python CLI tool into an MCP server for downloading academic papers via LLM agents.

**Core Value**:
- Intelligent multi-source routing (Sci-Hub + Unpaywall)
- Year-based source selection (2021 threshold)
- 95%+ code reuse from scihub-cli (zero refactoring)
- Fast MVP delivery (4-6 hours)

---

## Critical Constraints

### 🚫 DO NOT Modify scihub_core Code
- **Rule**: All code copied from `../scihub-cli/` to `scihub_core/` MUST remain unchanged
- **Rationale**: Battle-tested code, zero regression risk
- **Exception**: Only fix import paths (relative imports within scihub_core)
- **Verification**: No changes to core logic, classes, or methods

### 🔒 Synchronous Code Preservation
- **Rule**: Keep all scihub_core code synchronous (uses `requests`, not `aiohttp`)
- **Pattern**: Use `asyncio.to_thread()` to wrap sync calls in async tools
- **Example**:
  ```python
  @mcp.tool()
  async def paper_download(params):
      def _sync_download():
          client = SciHubClient()
          return client.download_paper(params.identifier)

      result = await asyncio.to_thread(_sync_download)
      return format_result(result)
  ```

### 📛 Naming Convention
- **MCP Tools**: Use `paper_` prefix (NOT `scihub_`)
  - ✅ `paper_download`, `paper_batch_download`, `paper_metadata`
  - ❌ `scihub_download_paper`, `scihub_batch_download`
- **Rationale**: Multi-source support (Sci-Hub + Unpaywall), avoid misleading names
- **Module Names**:
  - Package: `paper_download_mcp`
  - Core code: `scihub_core` (preserved from scihub-cli)

### 📧 Email Configuration Required
- **Environment Variable**: `SCIHUB_CLI_EMAIL` (required for Unpaywall API)
- **Validation**: Check on server startup, fail fast with clear error
- **Configuration**: Set in Claude Desktop config (`claude_desktop_config.json`)

### 📦 Deployment Method
- **Production**: Use `uvx` (no manual installation)
- **Claude Desktop Config**:
  ```json
  {
    "mcpServers": {
      "paper-download": {
        "command": "uvx",
        "args": ["paper-download-mcp"],
        "env": {"SCIHUB_CLI_EMAIL": "user@university.edu"}
      }
    }
  }
  ```
- **Development**: Use `uv run python -m paper_download_mcp.server`

---

## Implementation Priorities

### Phase 1: Foundation (1 hour)
1. Create project structure (`src/paper_download_mcp/`)
2. Configure `pyproject.toml` (FastMCP, requests, beautifulsoup4, pydantic)
3. Copy scihub-cli core modules to `scihub_core/` (18 files)
4. Fix import paths, verify integration

### Phase 2: Core Tools (2-2.5 hours)
1. Implement Pydantic models (`models.py`)
2. Implement formatters (`formatters.py` - Markdown/JSON)
3. Implement `paper_download` tool
4. Implement `paper_batch_download` tool

### Phase 3: Metadata Tool (0.5-1 hour)
1. Implement `paper_metadata` tool

### Phase 4: Testing & Docs (1-1.5 hours)
1. MCP Inspector testing (manual)
2. Write README with `uvx` setup
3. Add legal disclaimer

**Total**: 4.5-5.5 hours (MVP complete)

---

## Key Technical Decisions

### AD-001: FastMCP Framework
- **Why**: Decorator-style API, official support, 3.7k+ stars, complete ecosystem
- **Alternative Rejected**: Anthropic SDK (more boilerplate)

### AD-002: stdio Transport
- **Why**: Single-user Claude Desktop scenario, simplest deployment
- **Future**: Can add HTTP for multi-user later

### AD-003: File Path Return (Not Base64)
- **Why**: Claude Desktop has filesystem access, avoid 1.3x response bloat
- **Pattern**: Download to disk, return absolute path

### AD-004: Sequential Batch Downloads
- **Why**: Rate limiting compliance (2-second delays), MVP simplicity
- **Future**: Can add true async with aiohttp later

---

## MCP Tool Specifications

### 1. `paper_download`
**Input**: `{identifier: str, output_dir?: str}`
**Output**: Markdown with file path, metadata, source, timing
**Behavior**:
- Normalize DOI/URL → DOI
- Detect year via Crossref
- Route: year < 2021 → Sci-Hub first, else → Unpaywall first
- Download PDF, validate (header + size)
- Save as `[YYYY] - Title.pdf`

### 2. `paper_batch_download`
**Input**: `{identifiers: str[], output_dir?: str}` (max 50)
**Output**: Markdown summary (total, success, failed, file list)
**Behavior**:
- Sequential downloads (not parallel)
- 2-second delay between downloads
- Progress via `ctx.report_progress()`
- Continue on failure (don't stop batch)

### 3. `paper_metadata`
**Input**: `{identifier: str}`
**Output**: JSON metadata (DOI, title, year, authors, journal, OA status)
**Behavior**:
- Query Unpaywall API (primary)
- Fallback to Crossref (year detection)
- Fast (<1 second), no file download

---

## Error Handling Strategy

### Three-Layer Approach

1. **Input Validation** (Pydantic):
   - Type/range checks automatic
   - Returns validation error to MCP client

2. **Business Logic** (scihub_core):
   - Network errors: Retry 3x with exponential backoff
   - API errors: Source fallback (Sci-Hub ↔ Unpaywall)
   - Returns `None` on failure (graceful)

3. **Tool Layer** (MCP tools):
   - Convert `None` to user-friendly Markdown errors
   - Include actionable suggestions
   - Example:
     ```markdown
     # Download Failed
     **DOI**: 10.1234/invalid
     **Error**: Paper not found in any source

     Suggestions:
     - Verify DOI is correct (check on doi.org)
     - Try paper_metadata to check availability
     - Paper may be too recent (not indexed yet)
     ```

---

## Testing Checklist

### MCP Inspector Tests (Manual)
- [ ] `paper_download` with valid DOI (2013 paper → Sci-Hub)
- [ ] `paper_download` with valid URL (2021 paper → Unpaywall)
- [ ] `paper_download` with invalid DOI (error handling)
- [ ] `paper_batch_download` with 5 papers (mixed success/failure)
- [ ] `paper_metadata` with valid DOI (JSON response)
- [ ] Progress reporting visible during batch download

### Claude Desktop E2E Test
- [ ] Configure with `uvx` command
- [ ] Download paper in conversation
- [ ] Verify file exists at reported path
- [ ] Filename format correct: `[YYYY] - Title.pdf`

---

## Legal and Compliance

### Legal Disclaimer (Required in README)
```markdown
## Legal Notice

This tool provides access to academic papers through:
- **Unpaywall**: Legal open-access aggregator (recommended)
- **Sci-Hub**: Operates in legal gray area (use at own risk)

Users are responsible for compliance with applicable copyright laws.
This tool is for research and educational purposes only.
```

### Rate Limiting
- 2-second delay between batch downloads
- Respect Unpaywall API limits (~100k requests/day)
- Email required for Unpaywall compliance

---

## File Organization

### Project Structure
```
paper-download-mcp/
├── pyproject.toml              # uv project config
├── README.md                   # User documentation
├── src/
│   └── paper_download_mcp/
│       ├── __init__.py
│       ├── server.py           # FastMCP entry point
│       ├── models.py           # Pydantic schemas
│       ├── formatters.py       # Markdown/JSON formatters
│       ├── tools/
│       │   ├── download.py     # paper_download, paper_batch_download
│       │   └── metadata.py     # paper_metadata
│       └── scihub_core/        # ⚠️ NO MODIFICATIONS
│           ├── client.py
│           ├── sources/
│           ├── core/
│           ├── network/
│           ├── config/
│           └── utils/
└── tests/
    ├── test_models.py
    ├── test_formatters.py
    └── test_integration.py
```

### Filename Convention for Downloaded Papers
- Format: `[YYYY] - Paper Title.pdf`
- Sanitize: Remove `< > : " / \ | ? *`
- Max length: 100 characters (excluding extension)
- Example: `[2013] - Nanometre-scale thermometry in a living cell.pdf`

---

## Common Pitfalls to Avoid

### ❌ DON'T
- Modify scihub_core code (keep as-is)
- Use `scihub_` prefix for tool names (use `paper_`)
- Convert to full async/await (keep sync with `asyncio.to_thread`)
- Return base64-encoded PDFs (return file paths)
- Add emojis to logs (user preference)
- Implement parallel downloads in MVP (sequential only)
- Skip email validation on startup

### ✅ DO
- Copy scihub_core code verbatim (only fix imports)
- Use `paper_` prefix for all tool names
- Wrap sync calls with `asyncio.to_thread()`
- Return absolute file paths
- Validate email on server startup
- Include legal disclaimer in README
- Use `uvx` in deployment instructions
- Add 2-second delays between batch downloads

---

## Quick Reference Commands

### Development
```bash
# Setup
uv sync

# Run server
uv run python -m paper_download_mcp.server

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run python -m paper_download_mcp.server

# Validate OpenSpec
openspec validate implement-mcp-server --strict
```

### User Deployment
```bash
# No installation needed - uvx handles it
# Just configure Claude Desktop:
{
  "mcpServers": {
    "paper-download": {
      "command": "uvx",
      "args": ["paper-download-mcp"],
      "env": {"SCIHUB_CLI_EMAIL": "user@university.edu"}
    }
  }
}
```

---

## Success Criteria

**MVP Complete When**:
- [ ] All 3 tools implemented and tested
- [ ] MCP Inspector tests pass
- [ ] Claude Desktop integration works
- [ ] README with `uvx` setup complete
- [ ] Legal disclaimer included
- [ ] OpenSpec validation passes
- [ ] Zero modifications to scihub_core code

**Time Budget**: 4-6 hours total
