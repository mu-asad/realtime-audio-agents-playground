# azure-realtime-audio-playground

A sandbox for experimenting with live audio (mic → Azure Realtime → audio/text back), with minimal assumptions about tech stack.

## Features

- **Azure Realtime Audio Integration**: Connect live audio streams to Azure's realtime services
- **Google Calendar MCP Integration**: Manage calendar events through the Model Context Protocol (MCP)
- **Spotify MCP Integration**: Control Spotify playback with natural language commands
- **Personal Assistant Agent**: AI-powered assistant with calendar and music control capabilities

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Google Cloud Platform account (for calendar integration, optional)
- Spotify Premium account (for music playback control, optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mu-asad/azure-realtime-audio-playground.git
   cd azure-realtime-audio-playground
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies for the MCP servers:
   ```bash
   # Google Calendar MCP server
   cd google-calendar-mcp-server
   npm install
   cd ..
   
   # Spotify MCP server
   cd spotify-mcp-server
   npm install
   cd ..
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

### Google Calendar Integration

The project includes a fully functional Google Calendar integration using the Model Context Protocol (MCP). The agent can:

- ✅ List calendar events for any date range
- ✅ Get details of specific events
- ✅ Create new calendar events with attendees
- ✅ Update existing events (title, time, description, etc.)
- ✅ Delete/cancel events
- ✅ Check free/busy availability

#### Setup

See [docs/GOOGLE_CALENDAR_SETUP.md](docs/GOOGLE_CALENDAR_SETUP.md) for detailed setup instructions, including:
- Setting up Google Calendar API credentials
- Configuring OAuth authentication
- Getting a refresh token
- Running the test scripts

#### Quick Test

```bash
# Run the comprehensive test suite
python examples/test_calendar.py
```

#### Disabling Calendar Integration

If you don't need calendar functionality:
1. Simply don't run the calendar agent
2. Skip the Google Calendar setup steps
3. The project will work without it

### Spotify Integration

The project includes Spotify playback control using the Model Context Protocol (MCP). The agent can:

- ✅ List and select playback devices
- ✅ Play music by search query or URI
- ✅ Control playback (play, pause, resume)
- ✅ Navigate tracks (next, previous)
- ✅ Search for tracks on Spotify
- ✅ Get current playback state

#### Setup

See [docs/SPOTIFY_SETUP.md](docs/SPOTIFY_SETUP.md) for detailed setup instructions, including:
- Creating a Spotify app
- Configuring OAuth credentials
- Getting a refresh token
- Running the test scripts

#### Quick Test

```bash
# Run the Spotify integration test
python examples/test_spotify.py
```

#### Disabling Spotify Integration

If you don't need Spotify functionality:
1. Simply don't run the Spotify agent
2. Skip the Spotify setup steps
3. The project will work without it

## Project Structure

```
azure-realtime-audio-playground/
├── docs/                          # Documentation
│   ├── GOOGLE_CALENDAR_SETUP.md  # Calendar integration guide
│   └── SPOTIFY_SETUP.md          # Spotify integration guide
├── examples/                      # Example scripts
│   ├── test_calendar.py          # Calendar integration tests
│   └── test_spotify.py           # Spotify integration tests
├── google-calendar-mcp-server/    # Google Calendar MCP server
│   ├── server.js                 # MCP server implementation
│   ├── get-refresh-token.js      # Token generation helper
│   └── package.json              # Node.js dependencies
├── spotify-mcp-server/            # Spotify MCP server
│   ├── server.js                 # Spotify MCP implementation
│   ├── get-refresh-token.js      # Token generation helper
│   └── package.json              # Node.js dependencies
├── src/                          # Source code
│   └── agent_host/               # Agent host implementation
│       ├── calendar_agent.py     # Calendar agent host
│       ├── spotify_agent.py      # Spotify agent host
│       └── __init__.py
├── .env.example                  # Environment variables template
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Available Calendar Tools

The Calendar MCP server exposes these tools to the agent:

| Tool | Description |
|------|-------------|
| `list_events` | List calendar events within a time range |
| `get_event` | Get details of a specific event |
| `create_event` | Create a new calendar event |
| `update_event` | Update an existing event |
| `delete_event` | Delete/cancel an event |
| `get_free_busy` | Get free/busy information |

## Available Spotify Tools

The Spotify MCP server exposes these tools to the agent:

| Tool | Description |
|------|-------------|
| `spotify_get_devices` | List available playback devices |
| `spotify_transfer_playback` | Transfer playback to a device |
| `spotify_play` | Play music by URI or search |
| `spotify_pause` | Pause current playback |
| `spotify_resume` | Resume playback |
| `spotify_next_track` | Skip to next track |
| `spotify_previous_track` | Go to previous track |
| `spotify_search_tracks` | Search for tracks |
| `spotify_get_current_playback` | Get playback state |

## Usage Examples

### Calendar Agent

```python
import asyncio
from src.agent_host.calendar_agent import CalendarAgentHost

async def main():
    agent = CalendarAgentHost()
    
    try:
        await agent.connect_to_mcp_server()
        
        # List today's events
        events = await agent.list_events(max_results=10)
        print(f"Found {len(events['events'])} events")
        
        # Create a new event
        new_event = await agent.create_event(
            summary="Team Meeting",
            start_time="2025-11-20T14:00:00Z",
            end_time="2025-11-20T15:00:00Z"
        )
        
    finally:
        await agent.close()

asyncio.run(main())
```

### Spotify Agent

```python
import asyncio
from src.agent_host.spotify_agent import SpotifyAgentHost

async def main():
    agent = SpotifyAgentHost()
    
    try:
        await agent.connect_to_mcp_server()
        
        # Get available devices
        devices = await agent.get_devices()
        print(f"Found {len(devices['devices'])} devices")
        
        # Play some music
        await agent.play(search_query="lofi hip hop")
        
        # Get current playback
        playback = await agent.get_current_playback()
        if playback.get('playing'):
            print(f"Now playing: {playback['track']['name']}")
        
    finally:
        await agent.close()

asyncio.run(main())
```

## Architecture

The project uses the Model Context Protocol (MCP) to separate concerns:

- **Agent Hosts (Python)**: Manage AI agents and orchestrate tool calls
- **MCP Servers (Node.js)**: Handle external API interactions (Google Calendar, Spotify)
- **MCP Protocol**: Standardized communication between agents and services

This architecture allows for:
- Easy testing of individual components
- Swapping out different service providers
- Adding additional MCP servers for other services
- Clear separation of concerns

## Development

### Running Tests

```bash
# Test calendar integration
python examples/test_calendar.py

# Add more tests as the project grows
```

### Linting

```bash
# Python code
black src/ examples/
ruff check src/ examples/

# Node.js code (if needed)
cd google-calendar-mcp-server && npm run lint
```

## Contributing

Contributions are welcome! This is a playground project for experimenting with Azure Realtime Audio and MCP integrations.

## License

See [LICENSE](LICENSE) file for details.

## Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
