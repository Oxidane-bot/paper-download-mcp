# Specification: Paper Download Tools

## ADDED Requirements

### Requirement: Single Paper Download Tool

**ID**: PDT-001

The system MUST provide an MCP tool named `paper_download` that downloads a single academic paper given a DOI or URL identifier.

**Rationale**: Core capability for LLM agents to retrieve individual papers mentioned in conversations.

**Input Schema**:
- `identifier` (required, string, 5-500 chars): DOI (e.g., `10.1038/nature12373`) or paper URL
- `output_dir` (optional, string, default: `./downloads`): Directory path for saving PDF

**Output Format**: Markdown text containing:
- Paper metadata (DOI, title, year, journal)
- File path (absolute path to downloaded PDF)
- File size in KB
- Source used (Sci-Hub or Unpaywall)
- Download time in seconds

**Error Handling**:
- Invalid identifier format → validation error with suggestions
- Paper not found → clear message listing checked sources
- Network timeout → retry with exponential backoff (3 attempts max)
- File system errors → permission/disk space error message

**Annotations**:
- `readOnlyHint: false` (creates file)
- `destructiveHint: false` (no data modification)
- `idempotentHint: true` (same DOI = same result)
- `openWorldHint: true` (accesses external APIs)

#### Scenario: Download Paper by DOI

**Given** a valid DOI `10.1038/nature12373`

**When** user invokes `paper_download` with `identifier="10.1038/nature12373"`

**Then**:
- System detects publication year is 2013 (< 2021)
- System routes request to Sci-Hub source first
- System downloads PDF from Sci-Hub mirror
- System validates PDF (header check, size > 10KB)
- System extracts metadata (title, year, authors)
- System saves file as `[2013] - Nanometre-scale thermometry in a living cell.pdf`
- System returns Markdown response with file path and metadata
- Response includes download time < 10 seconds

#### Scenario: Download Recent Paper by URL

**Given** a valid paper URL `https://doi.org/10.1038/s41586-021-03380-y`

**When** user invokes `paper_download` with the URL as identifier

**Then**:
- System normalizes URL to DOI `10.1038/s41586-021-03380-y`
- System detects publication year is 2021 (>= 2021)
- System routes request to Unpaywall source first
- System queries Unpaywall API with configured email
- System downloads PDF from open access URL
- System saves file with year-title format
- System returns success response indicating Unpaywall source

#### Scenario: Handle Invalid DOI

**Given** an invalid DOI `10.1234/nonexistent`

**When** user invokes `paper_download` with invalid identifier

**Then**:
- System attempts Sci-Hub lookup (fails)
- System attempts Unpaywall lookup (fails)
- System returns Markdown error message containing:
  - "Paper not found in any source"
  - List of checked sources (Sci-Hub, Unpaywall)
  - Suggestion to verify DOI correctness
  - Suggestion to use `paper_metadata` for diagnosis

---

### Requirement: Batch Paper Download Tool

**ID**: PDT-002

The system MUST provide an MCP tool named `paper_batch_download` that downloads multiple papers sequentially with progress reporting.

**Rationale**: Enables efficient bulk paper retrieval for literature reviews or reference lists.

**Input Schema**:
- `identifiers` (required, list of strings, 1-50 items): List of DOIs or URLs
- `output_dir` (optional, string, default: `./downloads`): Directory path for saving PDFs

**Output Format**: Markdown text containing:
- Summary statistics (total, successful, failed, completion percentage)
- Total download time
- List of successful downloads (filename, size, source)
- List of failed downloads (identifier, error reason)

**Behavior**:
- Downloads execute sequentially (not parallel)
- 2-second delay between downloads (rate limiting)
- Progress reported via MCP Context API (`ctx.report_progress()`)
- Single failure does not stop batch processing
- Each download uses same logic as single paper download

**Performance**:
- Maximum 50 papers per batch (validation error if exceeded)
- Typical throughput: 20-30 papers per minute (including delays)
- Progress updates every paper completion

#### Scenario: Batch Download Mixed Papers

**Given** a list of 5 DOIs (3 old papers < 2021, 2 new papers >= 2021)

**When** user invokes `paper_batch_download` with the identifier list

**Then**:
- System processes papers sequentially
- Progress updates: "1/5", "2/5", "3/5", "4/5", "5/5"
- Old papers route to Sci-Hub first
- New papers route to Unpaywall first
- 2-second delay between each download
- Final response shows:
  - "Total: 5 papers"
  - "Successful: 5 (100%)"
  - "Failed: 0 (0%)"
  - List of all downloaded files with sources

#### Scenario: Handle Partial Batch Failure

**Given** a list of 4 DOIs (2 valid, 2 invalid)

**When** user invokes `paper_batch_download`

**Then**:
- System attempts all 4 downloads
- Valid papers download successfully
- Invalid papers fail gracefully
- Processing continues after failures
- Final response shows:
  - "Total: 4 papers"
  - "Successful: 2 (50%)"
  - "Failed: 2 (50%)"
  - Success list with 2 entries
  - Failure list with 2 entries and error reasons

#### Scenario: Reject Oversized Batch

**Given** a list of 51 DOIs

**When** user invokes `paper_batch_download`

**Then**:
- Pydantic validation fails
- System returns error: "Maximum 50 papers per batch"
- No downloads attempted
- Suggested solution: split into multiple smaller batches

---

### Requirement: Paper Metadata Tool

**ID**: PDT-003

The system MUST provide an MCP tool named `paper_metadata` that retrieves paper metadata without downloading the PDF.

**Rationale**: Fast metadata lookup for availability checking and paper preview.

**Input Schema**:
- `identifier` (required, string): DOI or URL

**Output Format**: JSON text containing:
- `doi` (string): Normalized DOI
- `title` (string): Paper title
- `year` (integer): Publication year
- `authors` (list of strings): Author names
- `journal` (string): Journal name
- `volume` (string, optional): Volume number
- `pages` (string, optional): Page range
- `is_oa` (boolean): Open access status
- `available_sources` (list of strings): Available download sources

**Data Sources** (priority order):
1. Unpaywall API (primary)
2. Crossref API (fallback for year)
3. DOI-only metadata (last resort)

**Performance**:
- Target response time: < 1 second
- No file downloads
- Minimal network requests (1-2 API calls)

**Annotations**:
- `readOnlyHint: true` (no side effects)
- `destructiveHint: false`
- `idempotentHint: true`
- `openWorldHint: true`

#### Scenario: Get Metadata for Known Paper

**Given** a valid DOI `10.1038/nature12373`

**When** user invokes `paper_metadata`

**Then**:
- System queries Unpaywall API
- Response completes in < 2 seconds
- Returns JSON with:
  - `doi`: "10.1038/nature12373"
  - `title`: "Nanometre-scale thermometry in a living cell"
  - `year`: 2013
  - `authors`: ["Kucsko, G.", "Maurer, P. C.", ...]
  - `journal`: "Nature"
  - `is_oa`: false
  - `available_sources`: ["Sci-Hub"]

#### Scenario: Fallback to Crossref for Year

**Given** a DOI where Unpaywall returns incomplete metadata

**When** user invokes `paper_metadata`

**Then**:
- System queries Unpaywall (partial result)
- System queries Crossref API for year
- Combines data from both sources
- Returns complete metadata JSON
- Total time < 2 seconds

#### Scenario: Handle Completely Unknown DOI

**Given** an invalid or very recent DOI not in any database

**When** user invokes `paper_metadata`

**Then**:
- Unpaywall returns 404
- Crossref returns 404
- System returns JSON with:
  - `doi`: (normalized identifier)
  - `error`: "Metadata not available"
  - `available_sources`: []
  - Suggestion to check DOI correctness

---

### Requirement: Intelligent Source Routing

**ID**: PDT-004

The system MUST implement year-based source selection to maximize download success rates.

**Rationale**: Sci-Hub frozen in 2020; Unpaywall better for recent papers (2021+).

**Routing Rules**:
- Publication year < 2021: Sci-Hub → Unpaywall (fallback)
- Publication year >= 2021: Unpaywall → Sci-Hub (fallback)
- Year unknown: Unpaywall → Sci-Hub (conservative)

**Year Detection**:
- Primary: Crossref API lookup
- Cache year results to avoid redundant API calls
- Timeout: 5 seconds max for year detection

**Fallback Chain**:
- If primary source fails, automatically try secondary source
- Both sources exhausted → return "not available" error
- Log which source succeeded for user visibility

#### Scenario: Route Old Paper to Sci-Hub

**Given** a DOI with publication year 2015

**When** download is requested

**Then**:
- System queries Crossref for year (returns 2015)
- System selects Sci-Hub as primary source
- System attempts Sci-Hub download
- If Sci-Hub succeeds, Unpaywall is not contacted
- Response indicates "Source: Sci-Hub"

#### Scenario: Route New Paper to Unpaywall

**Given** a DOI with publication year 2023

**When** download is requested

**Then**:
- System queries Crossref for year (returns 2023)
- System selects Unpaywall as primary source
- System queries Unpaywall API with email
- If Unpaywall succeeds, Sci-Hub is not contacted
- Response indicates "Source: Unpaywall"

#### Scenario: Fallback from Failed Primary Source

**Given** a 2020 paper available only on Unpaywall (edge case)

**When** download is requested

**Then**:
- System detects year 2020 (< 2021)
- System tries Sci-Hub first (fails - paper not in Sci-Hub)
- System falls back to Unpaywall (succeeds)
- Response indicates "Source: Unpaywall"
- Total time includes both attempts

---

### Requirement: Email Configuration

**ID**: PDT-005

The system MUST require email configuration for Unpaywall API compliance and MUST validate it on startup.

**Rationale**: Unpaywall API requires valid email for usage tracking and contact.

**Configuration Method**:
- Environment variable: `SCIHUB_CLI_EMAIL`
- Set in Claude Desktop config or system environment
- No hardcoded default email

**Validation**:
- Check email presence on server startup
- If missing, raise clear error with setup instructions
- Email format validation (basic pattern check)
- Pass email to Unpaywall API in all requests

**Error Messages**:
- Missing email: "SCIHUB_CLI_EMAIL environment variable is required. See README for setup instructions."
- Invalid format: "Invalid email format. Please provide a valid email address."

#### Scenario: Server Starts with Valid Email

**Given** environment variable `SCIHUB_CLI_EMAIL=researcher@university.edu`

**When** MCP server starts

**Then**:
- Email validation passes
- Server initializes successfully
- Email is used in all Unpaywall API requests
- No warning or error messages

#### Scenario: Server Fails Without Email

**Given** `SCIHUB_CLI_EMAIL` environment variable is not set

**When** MCP server attempts to start

**Then**:
- Email validation fails
- Server raises ValueError with message:
  - "SCIHUB_CLI_EMAIL environment variable is required"
  - "Add to Claude Desktop config: env.SCIHUB_CLI_EMAIL=your-email@domain.edu"
- Server does not start
- User sees clear setup instructions

---

### Requirement: File Organization and Naming

**ID**: PDT-006

The system MUST save downloaded PDFs with structured filenames that include year and title for easy organization.

**Rationale**: Descriptive filenames improve paper management and searchability.

**Filename Format**: `[YYYY] - Paper Title Here.pdf`

**Sanitization Rules**:
- Remove special characters: `< > : " / \ | ? *`
- Replace with spaces or hyphens
- Truncate to 100 characters (excluding extension)
- Preserve alphanumeric and basic punctuation

**File Path**:
- Save to `output_dir` parameter (default: `./downloads`)
- Create directory if not exists
- Return absolute path in response

**Validation**:
- Check PDF header (`%PDF`) before saving
- Verify file size > 10KB (reject suspiciously small files)
- Handle filename collisions (append counter if needed)

#### Scenario: Generate Filename from Metadata

**Given** a paper with:
- Title: "Nanometre-scale thermometry in a living cell"
- Year: 2013

**When** download completes successfully

**Then**:
- Filename is `[2013] - Nanometre-scale thermometry in a living cell.pdf`
- File saved to `{output_dir}/[2013] - Nanometre-scale thermometry in a living cell.pdf`
- Response includes absolute path
- File is valid PDF (header checked)

#### Scenario: Sanitize Special Characters

**Given** a paper title containing: `"Protein: structure/function & biology"`

**When** generating filename

**Then**:
- Special characters removed: `: / &`
- Resulting filename: `[2020] - Protein structure function biology.pdf`
- File saves successfully without filesystem errors

#### Scenario: Handle Long Titles

**Given** a paper with title exceeding 120 characters

**When** generating filename

**Then**:
- Title truncated to 100 characters
- Ellipsis not added (clean truncation)
- Year prefix and `.pdf` extension preserved
- Final filename under system limits (255 chars)

---

## Related Specifications

- **MCP Protocol Specification**: Defines tool interface contracts
- **FastMCP Documentation**: Framework-specific implementation patterns
- **scihub-cli Architecture**: Source code reference for core logic (no spec, code is source of truth)

---

## Cross-References

- PDT-001 (`paper_download`) depends on PDT-004 (routing) and PDT-006 (naming)
- PDT-002 (`paper_batch_download`) depends on PDT-001 (reuses single download logic)
- PDT-003 (`paper_metadata`) depends on PDT-005 (email config for Unpaywall)
- All tools depend on PDT-005 (email configuration)

---

## Implementation Notes

**Async Wrapper Pattern**:
All tools use `asyncio.to_thread()` to wrap synchronous scihub-cli code:
```python
async def paper_download(params):
    def _sync_download():
        client = SciHubClient(email=EMAIL)
        return client.download_paper(params.identifier)

    result = await asyncio.to_thread(_sync_download)
    return format_result(result)
```

This preserves scihub-cli code without modifications while satisfying FastMCP's async requirements.

**Error Handling Strategy**:
- Input validation: Pydantic models (automatic)
- Network errors: Retry with exponential backoff (scihub-cli built-in)
- API errors: Source fallback (scihub-cli built-in)
- Filesystem errors: Clear error messages with suggestions
- All errors return user-friendly Markdown with actionable advice

**Testing Strategy**:
- Unit tests: Pydantic validation, formatters
- Integration tests: Mock external APIs, test tool logic
- End-to-end tests: MCP Inspector manual testing
- Acceptance test: Real download in Claude Desktop

---

## Compliance and Legal

**Disclaimer**: README must include prominent legal notice:
- Sci-Hub operates in legal gray area
- Tool is for research and educational purposes
- Users responsible for compliance with applicable laws
- Prioritize Unpaywall (legal OA source) when available

**Rate Limiting**:
- 2-second delay between batch downloads
- Respect Unpaywall API limits (~100k requests/day)
- Built-in retry with exponential backoff
- No aggressive scraping or mirror abuse
