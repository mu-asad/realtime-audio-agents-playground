# Helper Scripts

This directory contains helper scripts for the Realtime Audio Agents Playground.

## Available Scripts

### `check_env.py`

Verifies that required environment variables are set in your `.env` file.

**Usage:**
```bash
python scripts/check_env.py
```

**What it checks:**
- Google Calendar credentials (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, CALENDAR_ID)
- Spotify credentials (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

**When to use:**
- After initial setup
- When troubleshooting authentication issues
- Before running integration tests

## Getting OAuth Refresh Tokens

### Google Calendar

```bash
cd google-calendar-mcp-server
npm install
node get-refresh-token.js
# Follow the prompts to get your refresh token
```

### Spotify

```bash
cd spotify-mcp-server
npm install
node get-refresh-token.js
# Follow the prompts to get your refresh token
```

## Setup Flow

1. **Configure credentials:**
   ```bash
   cp .env.example .env
   # Edit .env and add your CLIENT_ID and CLIENT_SECRET for each service
   ```

2. **Get refresh tokens:**
   ```bash
   # For Google Calendar
   cd google-calendar-mcp-server && node get-refresh-token.js && cd ..
   
   # For Spotify
   cd spotify-mcp-server && node get-refresh-token.js && cd ..
   ```

3. **Verify environment:**
   ```bash
   python scripts/check_env.py
   ```

4. **Run tests:**
   ```bash
   python examples/test_calendar.py
   python examples/test_spotify.py
   ```

## Troubleshooting

### "Module not found" error

Install dependencies:
```bash
pip install -r requirements.txt
cd google-calendar-mcp-server && npm install && cd ..
cd spotify-mcp-server && npm install && cd ..
```

### "Invalid credentials" error

1. Verify CLIENT_ID and CLIENT_SECRET are correct in `.env`
2. Ensure you copied the full authorization code
3. Check that required APIs are enabled in Google Cloud Console / Spotify Dashboard

### "Refresh token not working" error

Generate a new refresh token:
```bash
# For Google Calendar
cd google-calendar-mcp-server && node get-refresh-token.js

# For Spotify
cd spotify-mcp-server && node get-refresh-token.js
```
