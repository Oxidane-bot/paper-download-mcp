# Testing Instructions

## Automated Tests Completed ✅

The following tests have been run and passed:

### 1. Tool Registration Test
```bash
SCIHUB_CLI_EMAIL="test@university.edu" uv run python test_tools.py
```

**Result**: ✅ All 3 tools registered successfully
- `paper_download`
- `paper_batch_download`
- `paper_metadata`

### 2. Unpaywall API Test
```bash
SCIHUB_CLI_EMAIL="test@university.edu" uv run python test_metadata.py
```

**Result**: ✅ Successfully retrieved metadata for DOI `10.1038/nature12373`
- Title: "Nanometre-scale thermometry in a living cell"
- Year: 2013
- Journal: Nature
- Open Access: True

## Manual Testing Required

### Option 1: MCP Inspector (Recommended)

MCP Inspector provides a web UI to test MCP servers:

```bash
SCIHUB_CLI_EMAIL="your@email.edu" npx @modelcontextprotocol/inspector uv run python -m paper_download_mcp.server
```

This will:
1. Start the MCP server
2. Open a web interface at http://localhost:5173
3. Show all registered tools with interactive testing

**Test Cases**:

1. **paper_metadata** (fast, no download):
   - Input: `{"identifier": "10.1038/nature12373"}`
   - Expected: JSON with title, year, authors, etc.

2. **paper_download** (downloads actual file):
   - Input: `{"identifier": "10.1038/nature12373", "output_dir": "./test_downloads"}`
   - Expected: Markdown with file path and metadata
   - Note: Creates `test_downloads/` directory with PDF

3. **paper_batch_download** (downloads multiple files):
   - Input: `{"identifiers": ["10.1038/nature12373", "10.1126/science.1234567"], "output_dir": "./test_downloads"}`
   - Expected: Markdown summary with statistics

### Option 2: Claude Desktop Integration

#### Step 1: Find your Claude Desktop config

**Linux**:
```bash
~/.config/Claude/claude_desktop_config.json
```

**macOS**:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows**:
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

#### Step 2: Add MCP server configuration

Add this to the `mcpServers` section:

```json
{
  "mcpServers": {
    "paper-download": {
      "command": "uv",
      "args": ["run", "python", "-m", "paper_download_mcp.server"],
      "cwd": "/home/oxidane/projects/paper-download-mcp",
      "env": {
        "SCIHUB_CLI_EMAIL": "your@email.edu"
      }
    }
  }
}
```

**Important**: Replace `/home/oxidane/projects/paper-download-mcp` with the actual path to this project.

#### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop completely.

#### Step 4: Test in conversation

Try these prompts:

1. **Metadata only** (fast):
   ```
   Get metadata for the paper with DOI 10.1038/nature12373
   ```

2. **Single download**:
   ```
   Download the paper 10.1038/nature12373
   ```

3. **Batch download**:
   ```
   Download these papers:
   - 10.1038/nature12373
   - 10.1126/science.1234567
   ```

### Option 3: Direct Server Testing

Start the server directly and observe logs:

```bash
SCIHUB_CLI_EMAIL="your@email.edu" uv run python -m paper_download_mcp.server
```

The server will show:
- FastMCP banner
- Server name: paper-download-mcp
- Transport: STDIO
- Status: "Starting MCP server..."

Press Ctrl+C to stop.

## Expected Behavior

### paper_metadata
- **Speed**: < 2 seconds
- **No files created**
- **Output**: JSON with DOI, title, year, authors, journal, OA status

### paper_download
- **Speed**: 2-10 seconds (first download may be slower due to mirror selection)
- **Creates file**: `[YYYY] - Paper Title.pdf` in output directory
- **Output**: Markdown with file path, size, source, download time

### paper_batch_download
- **Speed**: ~3-5 seconds per paper + 2 second delays between downloads
- **Creates multiple files**: One PDF per successful download
- **Output**: Markdown summary with statistics (total, successful, failed)
- **Behavior**: Continues even if some downloads fail

## Troubleshooting

### "SCIHUB_CLI_EMAIL environment variable is required"

Make sure you set the email in:
- Command line: `SCIHUB_CLI_EMAIL="your@email.edu"`
- Or Claude Desktop config (see above)

### "Paper not found in any source"

This is expected for:
- Invalid DOIs
- Very recent papers not yet indexed
- Papers with no open access and not in Sci-Hub

Try a known DOI like `10.1038/nature12373` (Nature, 2013) which should work.

### MCP Inspector connection issues

1. Make sure no other process is using port 5173
2. Try clearing browser cache
3. Check console output for errors

### Claude Desktop doesn't show the tools

1. Check Claude Desktop logs (usually in `~/Library/Logs/Claude/` or similar)
2. Verify the `cwd` path is correct in config
3. Make sure `uv` is in PATH
4. Try running the command manually first to verify it works

## Test Results Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Server startup | ✅ | Starts successfully with email |
| Email validation | ✅ | Clear error if missing |
| Tool registration | ✅ | All 3 tools registered |
| Unpaywall API | ✅ | Successfully queries metadata |
| FastMCP integration | ✅ | Tools decorated and registered |
| MCP Inspector | ⏳ | Requires user testing |
| Claude Desktop | ⏳ | Requires user testing |
| Actual downloads | ⏳ | Requires user testing (needs network) |

## Next Steps

1. Test with MCP Inspector (recommended first step)
2. Test one actual download to verify file creation
3. Test in Claude Desktop for end-to-end validation
4. Report any issues found

---

**Note**: The core functionality (API calls, formatting, tool registration) has been verified. The remaining tests require network access to download actual PDFs, which is best done through MCP Inspector or Claude Desktop.
