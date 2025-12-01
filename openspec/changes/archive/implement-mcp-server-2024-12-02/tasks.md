# Implementation Tasks

## Overview
This task list breaks down the MCP server implementation into small, verifiable work items that deliver incremental user-visible progress. Tasks are ordered by dependency and can be executed sequentially.

---

## Phase 1: Foundation (1 hour)

### Task 1.1: Create Project Structure
**Description**: Set up the basic directory layout and configuration files.

**Actions**:
- Create `src/paper_download_mcp/` directory structure
- Create `__init__.py` files for all modules
- Create subdirectories: `tools/`, `scihub_core/`

**Validation**:
- Directory tree matches planned structure
- All `__init__.py` files exist

**Estimated Time**: 10 minutes

---

### Task 1.2: Configure pyproject.toml
**Description**: Define project metadata, dependencies, and entry points.

**Actions**:
- Create `pyproject.toml` with project metadata
- Add dependencies: fastmcp, requests, beautifulsoup4, pydantic
- Define script entry point: `paper-download-mcp`
- Configure build system (hatchling or setuptools)

**Validation**:
- `uv sync` installs all dependencies without errors
- Entry point can be invoked (even if it errors due to missing code)

**Estimated Time**: 15 minutes

---

### Task 1.3: Copy scihub-cli Core Modules
**Description**: Copy all necessary modules from ../scihub-cli/ to scihub_core/.

**Actions**:
- Copy the following files from `../scihub-cli/scihub_cli/`:
  - `client.py`
  - `metadata_utils.py`
  - `sources/` (base.py, scihub_source.py, unpaywall_source.py)
  - `core/` (all 7 modules)
  - `network/session.py`
  - `config/` (all 3 modules)
  - `utils/` (logging.py, retry.py)
- Add `__init__.py` to all copied directories
- Fix import paths to use relative imports within scihub_core

**Validation**:
- Can import `from paper_download_mcp.scihub_core.client import SciHubClient`
- No import errors when importing core classes

**Estimated Time**: 25 minutes

---

### Task 1.4: Verify Core Code Integration
**Description**: Ensure copied scihub-cli code works without modifications.

**Actions**:
- Create simple test script that instantiates `SciHubClient`
- Run basic smoke test (no actual download, just initialization)
- Verify all dependencies are satisfied

**Validation**:
- `SciHubClient()` can be instantiated
- No missing dependency errors
- All imports resolve correctly

**Estimated Time**: 10 minutes

---

## Phase 2: Data Models and Formatters (45 minutes)

### Task 2.1: Implement Pydantic Input Models
**Description**: Create validated input schemas for all MCP tools.

**Actions**:
- Create `src/paper_download_mcp/models.py`
- Implement `DownloadPaperInput` with:
  - `identifier: str` (required, min_length=5, max_length=500)
  - `output_dir: Optional[str]` (default="./downloads")
- Implement `BatchDownloadInput` with:
  - `identifiers: List[str]` (min_items=1, max_items=50)
  - `output_dir: Optional[str]`
- Implement `GetMetadataInput` with:
  - `identifier: str` (required)

**Validation**:
- Models can be imported and instantiated
- Validation works (reject empty identifier, list > 50 items)
- Can serialize/deserialize to JSON

**Estimated Time**: 20 minutes

---

### Task 2.2: Implement Internal Result Models
**Description**: Create internal data classes for passing results between layers.

**Actions**:
- In `models.py`, add `DownloadResult` dataclass:
  - `doi: str`, `success: bool`, `file_path: Optional[str]`
  - `file_size: Optional[int]`, `title: Optional[str]`, `year: Optional[int]`
  - `source: Optional[str]`, `download_time: Optional[float]`, `error: Optional[str]`

**Validation**:
- Can create instances with various combinations of fields
- Serializes to dict cleanly

**Estimated Time**: 10 minutes

---

### Task 2.3: Implement Response Formatters
**Description**: Create formatters for Markdown and JSON output.

**Actions**:
- Create `src/paper_download_mcp/formatters.py`
- Implement `format_download_result(result: DownloadResult) -> str`
  - Success case: Markdown with DOI, title, year, file path, size, source, time
  - Failure case: Error message with suggestions
- Implement `format_batch_results(results: List[DownloadResult]) -> str`
  - Summary: total, successful, failed, total time
  - Success list with file paths
  - Failure list with error messages
- Implement `format_metadata(metadata: dict) -> str`
  - JSON formatting with indentation

**Validation**:
- Functions produce well-formatted output
- Markdown renders correctly in preview
- JSON is valid and pretty-printed

**Estimated Time**: 15 minutes

---

## Phase 3: MCP Server Setup (30 minutes)

### Task 3.1: Create Server Entry Point
**Description**: Initialize FastMCP server and configure email validation.

**Actions**:
- Create `src/paper_download_mcp/server.py`
- Import and initialize FastMCP: `mcp = FastMCP("paper-download-mcp")`
- Read `SCIHUB_CLI_EMAIL` from environment
- Validate email is present, raise clear error if missing
- Implement `main()` function that calls `mcp.run()`
- Add `if __name__ == "__main__"` guard

**Validation**:
- Can run `python -m paper_download_mcp.server` (should fail with email error)
- With `SCIHUB_CLI_EMAIL` set, server starts successfully
- MCP Inspector can connect to server

**Estimated Time**: 15 minutes

---

### Task 3.2: Create Tool Module Structure
**Description**: Set up the tools package with proper imports.

**Actions**:
- Create `src/paper_download_mcp/tools/__init__.py`
- Create empty `src/paper_download_mcp/tools/download.py`
- Create empty `src/paper_download_mcp/tools/metadata.py`
- Import tool modules in `server.py` (will auto-register via decorators)

**Validation**:
- No import errors when importing tool modules
- Server still starts successfully

**Estimated Time**: 10 minutes

---

### Task 3.3: Add Global Configuration Management
**Description**: Centralize environment variable access.

**Actions**:
- In `server.py`, create config module-level variables:
  - `EMAIL = os.getenv("SCIHUB_CLI_EMAIL")`
  - `DEFAULT_OUTPUT_DIR = os.getenv("SCIHUB_OUTPUT_DIR", "./downloads")`
- Add validation helper: `def _require_email() -> str`
- Export config for use in tool modules

**Validation**:
- Config variables accessible from tool modules
- Validation function raises clear errors

**Estimated Time**: 5 minutes

---

## Phase 4: Download Tools Implementation (1.5 hours)

### Task 4.1: Implement paper_download
**Description**: Create MCP tool for single paper download.

**Actions**:
- In `tools/download.py`, implement:
  ```python
  @mcp.tool()
  async def paper_download(params: DownloadPaperInput) -> str:
  ```
- Add comprehensive docstring with parameter descriptions
- Create sync wrapper function `_download()` that:
  - Instantiates `SciHubClient` with email and output_dir
  - Calls `client.download_paper(params.identifier)`
  - Captures result with timing
  - Builds `DownloadResult` object
- Use `await asyncio.to_thread(_download)` for async execution
- Format and return result using `format_download_result()`
- Add error handling with try/except

**Validation**:
- Tool appears in MCP Inspector tool list
- Can download a known paper (e.g., `10.1038/nature12373`)
- Returns formatted Markdown response
- File exists at reported path
- Error cases return helpful messages

**Estimated Time**: 45 minutes

---

### Task 4.2: Implement paper_batch_download
**Description**: Create MCP tool for batch download with progress reporting.

**Actions**:
- In `tools/download.py`, implement:
  ```python
  @mcp.tool()
  async def paper_batch_download(params: BatchDownloadInput, ctx: Context) -> str:
  ```
- Add comprehensive docstring
- Create sync wrapper `_batch_download()` that:
  - Iterates through identifiers
  - Reports progress via `ctx.report_progress()`
  - Collects all results in list
  - Calculates total statistics
- Use `await asyncio.to_thread(_batch_download)` (note: progress reporting needs special handling)
- Format and return results using `format_batch_results()`

**Validation**:
- Tool appears in MCP Inspector
- Can download 3-5 papers in batch
- Progress updates visible during execution
- Summary shows correct success/failure counts
- All files exist at reported paths

**Estimated Time**: 45 minutes

---

## Phase 5: Metadata Tool Implementation (30 minutes)

### Task 5.1: Implement paper_metadata
**Description**: Create MCP tool for metadata-only queries.

**Actions**:
- In `tools/metadata.py`, implement:
  ```python
  @mcp.tool()
  async def paper_metadata(params: GetMetadataInput) -> str:
  ```
- Add comprehensive docstring
- Create sync wrapper `_get_metadata()` that:
  - Uses `UnpaywallSource` to query metadata
  - Falls back to `YearDetector` (Crossref) if Unpaywall fails
  - Builds metadata dict
- Use `await asyncio.to_thread(_get_metadata)`
- Format and return using `format_metadata()`

**Validation**:
- Tool appears in MCP Inspector
- Returns metadata for known paper
- JSON is valid and well-formatted
- Fast execution (< 2 seconds)
- Fallback works when Unpaywall unavailable

**Estimated Time**: 30 minutes

---

## Phase 6: Testing (45 minutes)

### Task 6.1: Manual MCP Inspector Testing
**Description**: Test all tools through MCP Inspector.

**Actions**:
- Start server: `npx @modelcontextprotocol/inspector uv run python -m paper_download_mcp.server`
- Test `paper_download`:
  - Valid DOI: `10.1038/nature12373` (2013, should use Sci-Hub)
  - Valid URL: `https://doi.org/10.1038/s41586-021-03380-y` (2021, should use Unpaywall)
  - Invalid DOI: `10.1234/invalid` (should error gracefully)
- Test `paper_batch_download`:
  - Mixed list of 3 valid + 1 invalid DOI
  - Verify progress updates
  - Check summary stats
- Test `paper_metadata`:
  - Valid DOI, verify fields
  - Invalid DOI, verify error

**Validation**:
- All tests pass with expected results
- Error messages are clear and actionable
- Files exist and are valid PDFs
- Performance is acceptable (< 5s per paper)

**Estimated Time**: 30 minutes

---

### Task 6.2: Create Basic Unit Tests
**Description**: Add automated tests for key functions.

**Actions**:
- Create `tests/test_models.py`:
  - Test Pydantic validation (valid/invalid inputs)
- Create `tests/test_formatters.py`:
  - Test Markdown formatting
  - Test JSON formatting
- Create `tests/test_integration.py`:
  - Mock test for tool invocation (no real downloads)

**Validation**:
- `pytest` runs without errors
- All tests pass
- Coverage includes input validation and formatting

**Estimated Time**: 15 minutes

---

## Phase 7: Documentation (30 minutes)

### Task 7.1: Write README
**Description**: Comprehensive documentation for installation and usage.

**Actions**:
- Create/update `README.md` with:
  - Project description and features
  - Installation instructions (using `uvx` - no manual install needed)
  - Configuration section (environment variables)
  - Claude Desktop setup with `uvx` example:
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
  - Tool documentation (all 3 tools with examples)
  - Legal disclaimer (Sci-Hub usage)
  - Troubleshooting section

**Validation**:
- README is clear and complete
- All links work
- Examples are correct
- Legal disclaimer is prominent

**Estimated Time**: 20 minutes

---

### Task 7.2: Add Inline Documentation
**Description**: Ensure all code has proper docstrings and comments.

**Actions**:
- Review all tool functions for comprehensive docstrings
- Add module-level docstrings to all Python files
- Add comments for complex logic (e.g., async wrappers)
- Ensure type hints are present throughout

**Validation**:
- Every public function has docstring
- Docstrings follow Google or NumPy style
- Type hints pass mypy check (if applicable)

**Estimated Time**: 10 minutes

---

## Phase 8: Final Validation (15 minutes)

### Task 8.1: OpenSpec Validation
**Description**: Validate proposal against OpenSpec requirements.

**Actions**:
- Run `openspec validate implement-mcp-server --strict`
- Fix any validation errors
- Ensure all spec deltas are properly formatted

**Validation**:
- Validation passes with no errors
- All requirements have scenarios
- Spec deltas are correctly structured

**Estimated Time**: 10 minutes

---

### Task 8.2: End-to-End Acceptance Test
**Description**: Full workflow test in Claude Desktop.

**Actions**:
- Configure Claude Desktop with MCP server
- Test in real conversation:
  - "Download the paper with DOI 10.1038/nature12373"
  - "Download these 5 papers: [list]"
  - "Get metadata for DOI 10.1126/science.1234567"
- Verify all files downloaded correctly
- Check user experience is smooth

**Validation**:
- All downloads successful
- Responses are helpful and formatted well
- No confusing errors
- Performance is acceptable

**Estimated Time**: 5 minutes

---

## Summary

**Total Tasks**: 21 tasks across 8 phases
**Estimated Total Time**: 4.75-5.25 hours (excluding buffer)
**Critical Path**: Phase 1 → 2 → 3 → 4 → 5 (all sequential)
**Parallelizable**: Testing (Phase 6) and Documentation (Phase 7) can overlap

**Key Dependencies**:
- Phase 2 depends on Phase 1 (need scihub_core modules)
- Phase 3 depends on Phase 2 (need models and formatters)
- Phase 4-5 depend on Phase 3 (need server setup)
- Phase 6-8 can start after Phase 5 completes

**Risk Mitigation**:
- Each task is independently verifiable
- Failures caught early through incremental testing
- Can skip advanced features (e.g., progress reporting) if time-constrained
