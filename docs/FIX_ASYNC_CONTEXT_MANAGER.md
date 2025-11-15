# Fix Summary: Async Context Manager Error

## Problem
The error `object _AsyncGeneratorContextManager can't be used in 'await' expression` was occurring because the code was trying to directly `await` the result of `stdio_client()`, which returns an async context manager, not a coroutine.

## Root Cause
```python
# WRONG - causes the error:
stdio_transport = await stdio_client(server_params)

# RIGHT - enter the async context manager:
self._stdio_cm = stdio_client(server_params)
self.read, self.write = await self._stdio_cm.__aenter__()
```

## Changes Made

### 1. Fixed `src/agent_host/calendar_agent.py`
- **Store the context manager**: Added `self._stdio_cm = None` in `__init__`
- **Properly enter context**: Use `__aenter__()` instead of `await` on the context manager
- **Properly exit context**: Updated `close()` to call `__aexit__()` on the stored context manager
- **Added timeouts**: Added 10s timeout for session initialization and 5s for listing tools
- **Added debug logging**: Print statements to track connection progress
- **Fixed path resolution**: Use absolute paths to the MCP server script
- **Added NODE_PATH**: Set NODE_PATH environment variable to help Node.js find modules

### 2. Fixed `mcp-server/server.js`
- **Added path utilities**: Import `fileURLToPath`, `dirname`, and `join` for proper path handling
- **Improved dotenv loading**: Try multiple locations for .env file:
  - Parent directory (`../env`)
  - Current working directory (`.env`)
- **Added debug logging**: Log working directory, server directory, and credential status
- **Added request logging**: Log when list_tools and call_tool requests are received

### 3. Made `list_tools()` robust
- Handle both object-style and dict-style tool representations
- Support multiple attribute names (`name`/`displayName`, `inputSchema`/`input_schema`)

## How to Test

### Minimal Test
```bash
python3 examples/test_connection.py
```

### Full Test
```bash
python3 examples/test_calendar.py
```

## Expected Output (Success)
```
Starting MCP server process...
[DEBUG] Working directory: /path/to/mcp-server
[DEBUG] Server directory: /path/to/mcp-server
[DEBUG] GOOGLE_CLIENT_ID set: true
[DEBUG] GOOGLE_REFRESH_TOKEN set: true
MCP server process started
Client session created
Initializing session...
Session initialized successfully
Listing available tools...
[DEBUG] Received list_tools request
Found 6 tools
Connected to Google Calendar MCP server
Available tools: ['list_events', 'get_event', 'create_event', 'update_event', 'delete_event', 'get_free_busy']
✓ Connection successful!
```

## Troubleshooting

### If you still get timeout errors:
1. Check that .env file exists and contains valid credentials:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REFRESH_TOKEN`
   
2. Verify Node.js and dependencies are installed:
   ```bash
   cd mcp-server
   npm install
   ```

3. Test the MCP server directly:
   ```bash
   cd mcp-server
   node server.js
   ```
   It should print "Google Calendar MCP Server running on stdio"

### If environment variables aren't being read:
- Check that you're running from the repo root directory
- Check .env file location (should be in repo root)
- Check for syntax errors in .env file

## Key Takeaways
1. **Async context managers** must be entered with `__aenter__()` or `async with`, not `await`
2. **Always store the context manager** if you need to exit it later
3. **Use timeouts** to prevent indefinite hanging
4. **Add debug logging** to diagnose communication issues
5. **Handle path resolution carefully** when spawning subprocesses

