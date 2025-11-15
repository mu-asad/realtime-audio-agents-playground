# MCP Session Initialization Timeout - Troubleshooting Guide

## Problem
The MCP Python client times out when calling `session.initialize()` with the error:
```
TimeoutError: Timeout while initializing MCP session
```

## Root Cause
The MCP server (Node.js) is not responding to the initialization request from the Python MCP client. This indicates a communication breakdown between the client and server over stdio.

## Diagnostic Steps

### 1. Verify Node.js and Dependencies

```bash
# Check Node.js is installed
node --version

# Install MCP server dependencies
cd mcp-server
npm install
```

### 2. Test MCP Server Directly

Run the diagnostic script:
```bash
python3 scripts/diagnose_mcp.py
```

This will check:
- Server script exists
- Node.js is accessible
- Dependencies are installed
- Server process can start

### 3. Test Direct MCP Connection

Run the direct connection test:
```bash
python3 scripts/test_mcp_direct.py
```

This bypasses the CalendarAgentHost wrapper and tests the MCP connection directly.

### 4. Check Environment Variables

```bash
python3 scripts/check_env.py
```

Ensure all required Google Calendar credentials are set:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

## Common Issues and Solutions

### Issue 1: MCP SDK Version Mismatch

The Python MCP client and Node.js MCP server must use compatible protocol versions.

**Check versions:**
```bash
# Python MCP version
pip show mcp

# Node.js MCP version
cd mcp-server
npm list @modelcontextprotocol/sdk
```

**Solution:** Ensure both are using compatible versions (both should be 0.5.x or similar).

### Issue 2: Server Crashes on Startup

If the server crashes immediately, you won't see it in the timeout error.

**Debug:**
Add logging to see server stderr:
```python
# In the stdio_client call, check if there's a way to capture stderr
```

**Check server manually:**
```bash
cd mcp-server
node server.js
```

You should see:
```
[DEBUG] Working directory: /path/to/mcp-server
[DEBUG] Server directory: /path/to/mcp-server  
[DEBUG] GOOGLE_CLIENT_ID set: true
[DEBUG] GOOGLE_REFRESH_TOKEN set: true
[DEBUG] Creating StdioServerTransport...
[DEBUG] Connecting server to transport...
Google Calendar MCP Server running on stdio
```

### Issue 3: Missing Session Context Entry

The `ClientSession` must be entered as a context manager before calling `initialize()`.

**Current implementation:**
```python
session = ClientSession(read, write)
await session.__aenter__()  # Enter context
await session.initialize()  # Now this can work
```

### Issue 4: Environment Variables Not Passed

If environment variables aren't reaching the Node.js process:

**Option A:** Set them globally before running
```bash
export GOOGLE_CLIENT_ID="..."
export GOOGLE_CLIENT_SECRET="..."
export GOOGLE_REFRESH_TOKEN="..."
python3 examples/test_connection.py
```

**Option B:** Ensure .env file is in the repo root
```bash
ls -la .env
```

## Changes Made to Fix Original Error

### 1. Fixed Async Context Manager Usage
**Before (WRONG):**
```python
stdio_transport = await stdio_client(server_params)  # ❌ Can't await context manager
```

**After (CORRECT):**
```python
stdio_cm = stdio_client(server_params)
read, write = await stdio_cm.__aenter__()  # ✓ Enter context manager
```

### 2. Added Session Context Entry
```python
session = ClientSession(read, write)
await session.__aenter__()  # Enter session context before initialize()
await session.initialize()
```

### 3. Added Timeouts and Better Error Messages
```python
try:
    await asyncio.wait_for(session.initialize(), timeout=30.0)
except asyncio.TimeoutError:
    raise RuntimeError(
        "Timeout while initializing MCP session. "
        "The MCP server may not be responding. Check that:\n"
        "1. Node.js is installed and accessible\n"
        "2. MCP server dependencies are installed\n"
        "3. Google credentials are valid in .env file"
    )
```

### 4. Added Debug Logging
Added print statements at each step to see where the process hangs.

## Next Steps

If you're still seeing timeout errors after following this guide:

1. **Capture server logs:** Modify the stdio_client call to log stderr from the Node process
2. **Check protocol compatibility:** Verify Python and Node MCP SDK versions match
3. **Test server isolation:** Run the Node server in a separate terminal and manually send JSON-RPC messages
4. **Check firewall/permissions:** Ensure Node.js can be executed and stdio isn't being blocked

## Testing Hierarchy

Run tests in this order:

1. ✅ `python3 scripts/check_env.py` - Check environment
2. ✅ `python3 scripts/diagnose_mcp.py` - Check server can start  
3. ✅ `python3 scripts/test_mcp_direct.py` - Test MCP connection
4. ✅ `python3 examples/test_connection.py` - Test via CalendarAgentHost
5. ✅ `python3 examples/test_calendar.py` - Full integration test

Each step must pass before moving to the next.

## Technical Details

### MCP Communication Flow

1. **Python Client** starts Node.js server as subprocess with stdio transport
2. **Node.js Server** connects its stdio to `StdioServerTransport`
3. **Python Client** enters stdio context manager → gets read/write streams
4. **Python Client** creates `ClientSession(read, write)`
5. **Python Client** enters session context manager
6. **Python Client** calls `session.initialize()` → sends JSON-RPC "initialize" request
7. **Node.js Server** receives "initialize" request via stdin
8. **Node.js Server** responds with capabilities via stdout
9. **Python Client** receives response and completes initialization

**The timeout occurs at step 8** - the server never responds to the initialize request.

### Why This Happens

- Server crashed before receiving request
- Server can't parse the JSON-RPC message
- Protocol version mismatch
- Session context not entered (our fix)
- stdio streams not properly connected

## Summary

The original `_AsyncGeneratorContextManager can't be used in 'await' expression` error is **FIXED**.

The new timeout error suggests a different issue with the MCP server communication that requires:
1. Verifying the server starts correctly
2. Checking MCP SDK version compatibility
3. Ensuring the session context is properly entered (done)
4. Debugging the actual JSON-RPC communication

Use the diagnostic scripts provided to narrow down the exact cause.

