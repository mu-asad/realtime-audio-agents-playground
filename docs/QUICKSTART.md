# Quick Start Guide

Get up and running with Google Calendar MCP integration in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Google account with Calendar access

## Step 1: Clone and Install (2 minutes)

```bash
# Clone the repository
git clone https://github.com/mu-asad/azure-realtime-audio-playground.git
cd azure-realtime-audio-playground

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd mcp-server && npm install && cd ..
cd scripts && npm install && cd ..
```

## Step 2: Set Up Google Calendar API (5-10 minutes)

### 2.1 Enable the API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Calendar API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### 2.2 Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose **"Desktop app"** as the application type
4. Name it (e.g., "Calendar MCP Integration")
5. Click "Create"
6. Note your Client ID and Client Secret

### 2.3 Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use your preferred editor
```

Add:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_CALENDAR_ID=primary
```

## Step 3: Get Refresh Token (2 minutes)

```bash
cd scripts
node get-refresh-token.js
```

Follow the prompts:
1. Visit the authorization URL in your browser
2. Sign in and grant permissions
3. Copy the authorization code
4. Paste it in the terminal
5. Copy the refresh token to your `.env` file

Your `.env` should now have:
```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
GOOGLE_CALENDAR_ID=primary
```

## Step 4: Verify Setup (1 minute)

```bash
cd ..  # Back to project root
python scripts/verify_setup.py
```

You should see all checks pass! ✓

## Step 5: Run Your First Test (1 minute)

```bash
python examples/test_calendar.py
```

This will:
- Connect to Google Calendar
- List your upcoming events
- Create a test event
- Update it
- Delete it

## What's Next?

### Try Advanced Examples

```bash
python examples/advanced_examples.py
```

### Use in Your Code

```python
import asyncio
from src.agent_host import CalendarAgentHost

async def main():
    agent = CalendarAgentHost()
    
    try:
        await agent.connect_to_mcp_server()
        
        # List today's events
        events = await agent.list_events(max_results=10)
        print(f"Found {len(events['events'])} events")
        
        # Create an event
        result = await agent.create_event(
            summary="My Meeting",
            start_time="2025-11-20T14:00:00Z",
            end_time="2025-11-20T15:00:00Z"
        )
        print(f"Created: {result['event']['id']}")
        
    finally:
        await agent.close()

asyncio.run(main())
```

### Integrate with Azure Realtime Audio

1. Initialize `CalendarAgentHost` in your agent setup
2. Register calendar tools with your agent
3. Add system instructions from `docs/AGENT_SYSTEM_INSTRUCTIONS.md`
4. Handle tool calls by routing to the MCP server

## Troubleshooting

### "Invalid credentials"
- Double-check your Client ID and Secret
- Make sure you copied them correctly to `.env`

### "Refresh token invalid"
- Run `node scripts/get-refresh-token.js` again
- Make sure you complete the full OAuth flow

### "Connection refused"
- Verify Node.js dependencies are installed: `cd mcp-server && npm install`
- Check that Node.js 18+ is installed: `node --version`

### No events found
- Your calendar might be empty
- Try creating a test event in Google Calendar first
- Adjust the time range in your queries

## Need More Help?

- 📖 [Full Setup Guide](docs/GOOGLE_CALENDAR_SETUP.md)
- 📚 [Examples Documentation](examples/README.md)
- 🤖 [System Instructions](docs/AGENT_SYSTEM_INSTRUCTIONS.md)
- 🔧 [Scripts Documentation](scripts/README.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

## Common Tasks

### Check today's schedule
```python
from datetime import datetime
now = datetime.utcnow()
events = await agent.list_events(
    time_min=now.isoformat() + "Z",
    max_results=10
)
```

### Create a meeting
```python
result = await agent.create_event(
    summary="Team Sync",
    start_time="2025-11-20T14:00:00Z",
    end_time="2025-11-20T15:00:00Z",
    attendees=["colleague@example.com"]
)
```

### Find free time
```python
freebusy = await agent.get_free_busy(
    time_min="2025-11-20T00:00:00Z",
    time_max="2025-11-27T00:00:00Z"
)
```

---

Happy coding! 🎉 If you run into issues, check the documentation or open an issue on GitHub.
