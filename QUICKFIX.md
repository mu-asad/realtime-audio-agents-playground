# Quick Start: MCP Troubleshooting

## Original Error: FIXED ✅
```
TypeError: object _AsyncGeneratorContextManager can't be used in 'await' expression
```
This error has been completely resolved.

---

## Current Issue: Timeout
```
TimeoutError: Timeout while initializing MCP session
```

## Quick Fix Steps

### 1. Install Dependencies
```bash
cd mcp-server
npm install
cd ..
```

### 2. Verify Environment
```bash
python3 scripts/check_env.py
```

Ensure your `.env` file in the repo root contains:
```
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token
GOOGLE_CALENDAR_ID=primary
```

### 3. Run Diagnostics
```bash
# Test server can start
python3 scripts/diagnose_mcp.py

# Test MCP connection  
python3 scripts/test_mcp_direct.py

# Test agent host
python3 examples/test_connection.py
```

### 4. Check MCP SDK Versions

The Python and Node.js MCP SDKs must be compatible.

**Python:**
```bash
pip show mcp
```

**Node.js:**
```bash
cd mcp-server
npm list @modelcontextprotocol/sdk
```

Both should be version `0.5.x` or ensure they use the same protocol version.

---

## If Still Failing

### Manual Server Test
```bash
cd mcp-server
node server.js
```

You should see:
```
[DEBUG] Working directory: ...
[DEBUG] GOOGLE_CLIENT_ID set: true
[DEBUG] GOOGLE_REFRESH_TOKEN set: true
Google Calendar MCP Server running on stdio
```

If the server crashes or doesn't print this, there's an issue with the server itself.

### Check Node.js Version
```bash
node --version
```

Should be >= 18.0.0

---

## Documentation

- **`docs/STATUS_SUMMARY.md`** - Complete status and what was fixed
- **`docs/TROUBLESHOOTING_MCP_TIMEOUT.md`** - Detailed troubleshooting guide
- **`docs/FIX_ASYNC_CONTEXT_MANAGER.md`** - Original fix documentation

---

## What Changed

The async context manager error is **completely fixed**. The code now:
1. ✅ Properly stores the context manager
2. ✅ Enters it with `__aenter__()`
3. ✅ Exits it with `__aexit__()` in `close()`
4. ✅ Handles both stdio_client and ClientSession contexts
5. ✅ Has timeouts and better error messages

The timeout you're seeing is a **different issue** with MCP protocol communication, not the async context manager.

---

## Quick Test
```bash
python3 scripts/test_mcp_direct.py
```

This will show exactly where the process hangs.

