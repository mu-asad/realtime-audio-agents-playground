# Google Calendar MCP Integration

This document explains how to set up and use the Google Calendar integration with the Azure Realtime Audio playground.

## Overview

The Google Calendar integration uses the Model Context Protocol (MCP) to provide calendar management capabilities to the personal assistant agent. Instead of calling the Google Calendar API directly, the agent communicates with an MCP server that handles all calendar operations.

## Architecture

```
┌─────────────────────┐
│  Agent Host         │
│  (Python)           │
│                     │
│  CalendarAgentHost  │
└──────────┬──────────┘
           │
           │ MCP Protocol
           │ (stdio)
           │
┌──────────▼──────────┐
│  MCP Server         │
│  (Node.js)          │
│                     │
│  Google Calendar    │
│  API Integration    │
└──────────┬──────────┘
           │
           │ Google Calendar API
           │
┌──────────▼──────────┐
│  Google Calendar    │
│  (Cloud)            │
└─────────────────────┘
```

## Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- A Google Cloud Platform account
- Google Calendar API enabled

### 1. Set up Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials JSON file

5. Get a refresh token:
   ```bash
   # Use the OAuth playground or run the setup script
   # You'll need: client_id, client_secret
   # You'll get: refresh_token
   ```

   Or use this Node.js script to get a refresh token:
   ```javascript
   // get-refresh-token.js
   const { google } = require('googleapis');
   const readline = require('readline');

   const oauth2Client = new google.auth.OAuth2(
     'YOUR_CLIENT_ID',
     'YOUR_CLIENT_SECRET',
     'urn:ietf:wg:oauth:2.0:oob'
   );

   const scopes = ['https://www.googleapis.com/auth/calendar'];
   const url = oauth2Client.generateAuthUrl({ access_type: 'offline', scope: scopes });

   console.log('Authorize this app by visiting:', url);
   
   const rl = readline.createInterface({
     input: process.stdin,
     output: process.stdout,
   });

   rl.question('Enter the code: ', async (code) => {
     const { tokens } = await oauth2Client.getToken(code);
     console.log('Refresh token:', tokens.refresh_token);
     rl.close();
   });
   ```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# Google Calendar Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
GOOGLE_CALENDAR_ID=primary  # or a specific calendar ID
```

### 3. Install Dependencies

#### Python Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Node.js Dependencies

```bash
cd google-calendar-mcp-server
npm install
cd ..
```

### 4. Verify Installation

Run the test script to verify everything is set up correctly:

```bash
python examples/test_calendar.py
```

## Available Tools

The MCP server exposes the following calendar tools:

### 1. `list_events`

List calendar events within a time range.

**Parameters:**
- `timeMin` (string, optional): Start time in ISO 8601 format. Defaults to now.
- `timeMax` (string, optional): End time in ISO 8601 format.
- `maxResults` (number, optional): Maximum number of events to return. Default 10.
- `query` (string, optional): Free text search query to filter events.
- `calendarId` (string, optional): Calendar ID. Defaults to 'primary'.

**Example:**
```python
result = await agent.list_events(
    time_min="2025-11-15T00:00:00Z",
    time_max="2025-11-22T00:00:00Z",
    max_results=5
)
```

### 2. `get_event`

Get details of a specific calendar event.

**Parameters:**
- `eventId` (string, required): The event ID to retrieve.
- `calendarId` (string, optional): Calendar ID. Defaults to 'primary'.

**Example:**
```python
result = await agent.get_event(event_id="abc123xyz")
```

### 3. `create_event`

Create a new calendar event.

**Parameters:**
- `summary` (string, required): Event title/summary.
- `startTime` (string, required): Event start time in ISO 8601 format.
- `endTime` (string, optional): Event end time. Defaults to 1 hour after start.
- `description` (string, optional): Event description.
- `location` (string, optional): Event location.
- `attendees` (array or string, optional): Attendee email addresses.
- `calendarId` (string, optional): Calendar ID. Defaults to 'primary'.

**Example:**
```python
result = await agent.create_event(
    summary="Team Meeting",
    start_time="2025-11-20T14:00:00Z",
    end_time="2025-11-20T15:00:00Z",
    description="Weekly sync",
    attendees=["colleague@example.com"]
)
```

### 4. `update_event`

Update an existing calendar event.

**Parameters:**
- `eventId` (string, required): The event ID to update.
- `summary` (string, optional): New event title.
- `startTime` (string, optional): New start time.
- `endTime` (string, optional): New end time.
- `description` (string, optional): New description.
- `location` (string, optional): New location.
- `attendees` (array or string, optional): New attendee list.
- `calendarId` (string, optional): Calendar ID. Defaults to 'primary'.

**Example:**
```python
result = await agent.update_event(
    event_id="abc123xyz",
    summary="UPDATED: Team Meeting",
    start_time="2025-11-20T15:00:00Z"
)
```

### 5. `delete_event`

Delete/cancel a calendar event.

**Parameters:**
- `eventId` (string, required): The event ID to delete.
- `calendarId` (string, optional): Calendar ID. Defaults to 'primary'.

**Example:**
```python
result = await agent.delete_event(event_id="abc123xyz")
```

### 6. `get_free_busy`

Get free/busy information for a calendar.

**Parameters:**
- `timeMin` (string, optional): Start time. Defaults to now.
- `timeMax` (string, optional): End time. Defaults to 7 days from now.
- `calendarId` (string, optional): Calendar ID. Defaults to 'primary'.

**Example:**
```python
result = await agent.get_free_busy(
    time_min="2025-11-15T00:00:00Z",
    time_max="2025-11-22T00:00:00Z"
)
```

## Usage Examples

### Basic Usage

```python
import asyncio
from src.agent_host import CalendarAgentHost

async def main():
    agent = CalendarAgentHost()
    
    try:
        # Connect to the MCP server
        await agent.connect_to_mcp_server()
        
        # List today's events
        events = await agent.list_events(max_results=10)
        print(f"Found {len(events['events'])} events")
        
        # Create a new event
        new_event = await agent.create_event(
            summary="Coffee with friend",
            start_time="2025-11-20T10:00:00Z",
            end_time="2025-11-20T11:00:00Z"
        )
        print(f"Created event: {new_event['event']['id']}")
        
    finally:
        await agent.close()

asyncio.run(main())
```

### Integration with Azure Realtime Audio

When integrating with an Azure Realtime Audio agent, you would:

1. Initialize the `CalendarAgentHost` in your agent setup
2. Register the calendar tools with your agent's tool registry
3. Add system instructions about calendar capabilities
4. Handle tool calls from the agent by routing them to the MCP server

Example system instruction:
```
You are a personal assistant with access to Google Calendar. You can:
- Check the user's schedule and availability
- Create, update, and cancel calendar events
- Search for events by date or text
- Check free/busy times for scheduling

When the user asks about their calendar or scheduling, use the available calendar tools.
```

## Disabling Calendar Integration

To disable the Google Calendar integration:

1. Don't load the calendar tools in your agent
2. Remove the calendar-related system instructions
3. Set `GOOGLE_CALENDAR_ENABLED=false` in your `.env` file (optional)

## Troubleshooting

### "Invalid credentials" error

- Verify your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Make sure your refresh token is valid and hasn't been revoked
- Check that the Google Calendar API is enabled in your project

### "Node not found" error

- Make sure Node.js 18+ is installed: `node --version`
- Check that the MCP server dependencies are installed: `cd google-calendar-mcp-server && npm install`

### "Connection refused" error

- Ensure the MCP server script path is correct
- Check that the server.js file is executable
- Verify that all environment variables are properly set

### Events not appearing

- Check that you're using the correct calendar ID
- Verify the time range includes existing events
- Make sure the calendar is not empty

## Security Considerations

1. **Never commit credentials**: Keep `.env` in `.gitignore`
2. **Use refresh tokens**: Don't use access tokens directly
3. **Limit scopes**: Only request necessary calendar permissions
4. **Rotate credentials**: Periodically rotate your OAuth credentials
5. **Secure storage**: Store credentials securely in production environments

## Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

## License

This integration is part of the Azure Realtime Audio Playground project and follows the same license terms.
