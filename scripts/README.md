# Helper Scripts

This directory contains helper scripts for setting up and verifying the Google Calendar MCP integration.

## Available Scripts

### 1. `verify_setup.py`

Verifies that all dependencies and components are properly installed and configured.

**Usage:**
```bash
python scripts/verify_setup.py
```

**What it checks:**
- ✓ Python dependencies are installed
- ✓ Node.js dependencies are installed
- ✓ MCP server file exists and is valid
- ✓ Agent host module can be imported
- ✓ Documentation files exist
- ✓ Configuration files exist

**When to use:**
- After initial setup
- After installing dependencies
- Before running tests
- When troubleshooting issues

### 2. `get-refresh-token.js` (Moved)

**Note:** This script has been moved to `google-calendar-mcp-server/get-refresh-token.js`.

Interactive script to obtain a Google OAuth refresh token.

**Usage:**
```bash
# First, add your CLIENT_ID and CLIENT_SECRET to .env
cd google-calendar-mcp-server
npm install  # Only needed the first time
node get-refresh-token.js
```

**Steps:**
1. The script will display an authorization URL
2. Visit the URL in your browser
3. Sign in with your Google account
4. Grant the requested permissions
5. Copy the authorization code
6. Paste it into the terminal
7. Copy the refresh token to your `.env` file

**What you need:**
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 Client ID and Client Secret
- A web browser

**Output:**
- Refresh token for use in `.env` file
- Access token (for reference)
- Token expiry information

### 3. Example: Running the OAuth Flow

```bash
# Step 1: Set up your credentials
cp .env.example .env
# Edit .env and add your CLIENT_ID and CLIENT_SECRET

# Step 2: Get refresh token
cd google-calendar-mcp-server
npm install
node get-refresh-token.js

# Follow the prompts...

# Step 3: Add refresh token to .env
# GOOGLE_REFRESH_TOKEN=your-refresh-token-here

# Step 4: Verify setup
cd ..
python scripts/verify_setup.py

# Step 5: Run tests
python examples/test_calendar.py
```

## Troubleshooting

### "Module not found" error

Make sure you've installed all dependencies:
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies for MCP server
cd google-calendar-mcp-server && npm install
```

### "Invalid credentials" error

1. Verify your CLIENT_ID and CLIENT_SECRET are correct
2. Make sure you copied the full authorization code
3. Check that the Calendar API is enabled in your Google Cloud project

### "Refresh token not working" error

Refresh tokens can be revoked or expired. Get a new one:
1. Run `node google-calendar-mcp-server/get-refresh-token.js` again
2. Make sure you see the consent screen (use `prompt: 'consent'`)
3. Copy the new refresh token to `.env`

## Development

To add new scripts:

1. Create a new `.py` or `.js` file in this directory
2. Make it executable: `chmod +x your-script.py`
3. Add a shebang line: `#!/usr/bin/env python3` or `#!/usr/bin/env node`
4. Document it in this README

## Files in This Directory

- `verify_setup.py` - Verification script for checking installation
- `check_env.py` - Check environment variables
- `diagnose_mcp.py` - Diagnose MCP server issues
- `test_mcp_direct.py` - Test MCP connection directly
- `README.md` - This file
