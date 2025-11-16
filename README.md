# Realtime Audio Agents Playground

A playground for experimenting with realtime audio AI agents, integrating voice control with Google Calendar and Spotify through the Model Context Protocol (MCP).

## Features

- **OpenAI Realtime Voice Agent**: Voice-controlled AI assistant with natural language processing
- **Google Calendar Integration**: Manage calendar events through MCP - list, create, update, and delete events
- **Spotify Integration**: Control Spotify playback with voice commands - play music, control playback, search tracks
- **MCP Architecture**: Clean separation of concerns using the Model Context Protocol
- **Flexible Configuration**: Easy to enable/disable integrations as needed

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Google Cloud Platform account (for calendar integration, optional)
- Spotify Premium account (for music playback control, optional)
- Azure OpenAI or OpenAI API key (for voice agent, optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mu-asad/realtime-audio-agents-playground.git
   cd realtime-audio-agents-playground
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies for MCP servers:**
   ```bash
   # Google Calendar MCP server
   cd google-calendar-mcp-server && npm install && cd ..
   
   # Spotify MCP server
   cd spotify-mcp-server && npm install && cd ..
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (see setup guides below)
   ```

5. **Verify setup:**
   ```bash
   python scripts/check_env.py
   ```

### Google Calendar Integration

The project includes a Google Calendar integration using the Model Context Protocol (MCP).

**Capabilities:**
- List calendar events for any date range
- Get details of specific events
- Create new calendar events with attendees
- Update existing events (title, time, description, etc.)
- Delete/cancel events
- Check free/busy availability

**Setup:**

See [docs/GOOGLE_CALENDAR_SETUP.md](docs/GOOGLE_CALENDAR_SETUP.md) for detailed setup instructions.

**Quick test:**
```bash
python examples/test_calendar.py
```

**Disabling:** Simply skip the setup steps if you don't need calendar functionality.

### Spotify Integration

The project includes Spotify playback control using the Model Context Protocol (MCP).

**Capabilities:**
- List and select playback devices
- Play music by search query or URI
- Control playback (play, pause, resume)
- Navigate tracks (next, previous)
- Search for tracks on Spotify
- Get current playback state

**Setup:**

See [docs/SPOTIFY_SETUP.md](docs/SPOTIFY_SETUP.md) for detailed setup instructions.

**Quick test:**
```bash
python examples/test_spotify.py
```

**Disabling:** Simply skip the setup steps if you don't need Spotify functionality.

## Project Structure

```
realtime-audio-agents-playground/
├── docs/                           # Documentation
│   ├── GOOGLE_CALENDAR_SETUP.md   # Calendar integration setup guide
│   ├── SPOTIFY_SETUP.md           # Spotify integration setup guide
│   └── AGENT_SYSTEM_INSTRUCTIONS.md # AI agent instructions
├── examples/                       # Example scripts and tests
│   ├── test_calendar.py           # Calendar integration test suite
│   ├── test_spotify.py            # Spotify integration test suite
│   ├── test_connection.py         # MCP connection test
│   └── advanced_examples.py       # Advanced usage examples
├── google-calendar-mcp-server/     # Google Calendar MCP server
│   ├── server.js                  # MCP server implementation
│   ├── get-refresh-token.js       # OAuth token generation helper
│   └── package.json               # Node.js dependencies
├── spotify-mcp-server/             # Spotify MCP server
│   ├── server.js                  # Spotify MCP implementation
│   ├── get-refresh-token.js       # OAuth token generation helper
│   └── package.json               # Node.js dependencies
├── src/                           # Python source code
│   └── agent_host/                # Agent host implementations
│       ├── calendar_agent.py      # Calendar agent MCP host
│       └── spotify_agent.py       # Spotify agent MCP host
├── scripts/                       # Helper scripts
│   ├── check_env.py              # Environment variable checker
│   └── README.md                 # Scripts documentation
├── .env.example                   # Environment variables template
├── openai-agent.py                # Main voice agent with integrations
├── run_agent.py                  # Quick start CLI wrapper
├── pyproject.toml                # Python project configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Available Tools

### Calendar Tools

The Calendar MCP server exposes these tools to the agent:

| Tool | Description |
|------|-------------|
| `list_events` | List calendar events within a time range |
| `get_event` | Get details of a specific event |
| `create_event` | Create a new calendar event |
| `update_event` | Update an existing event |
| `delete_event` | Delete/cancel an event |
| `get_free_busy` | Get free/busy information |

### Spotify Tools

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

### Voice Agent with Integrations

Run the integrated voice agent:
```bash
python openai-agent.py
```

Or use the CLI wrapper with options:
```bash
# Choose voice
python run_agent.py --voice coral

# Adjust speed
python run_agent.py --speed 1.2

# Disable integrations
python run_agent.py --no-calendar --no-spotify

# Debug mode
python run_agent.py --debug
```

### Calendar Agent (Programmatic)

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

### Spotify Agent (Programmatic)

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

The project uses the **Model Context Protocol (MCP)** to separate concerns:

- **Agent Hosts (Python)**: Manage AI agents and orchestrate tool calls
- **MCP Servers (Node.js)**: Handle external API interactions (Google Calendar, Spotify)
- **MCP Protocol**: Standardized stdio-based communication between agents and services

**Benefits:**
- Easy testing of individual components
- Swappable service providers
- Clear separation of concerns
- Simple to add new MCP servers for other services

## Development

### Running Tests

```bash
# Test calendar integration
python examples/test_calendar.py

# Test Spotify integration
python examples/test_spotify.py

# Test MCP connections
python examples/test_connection.py

# Run advanced examples
python examples/advanced_examples.py
```

### Environment Verification

```bash
python scripts/check_env.py
```

### Code Quality

```bash
# Python code formatting and linting
black src/ examples/
ruff check src/ examples/

# Node.js linting (if applicable)
cd google-calendar-mcp-server && npm run lint
cd spotify-mcp-server && npm run lint
```

## Troubleshooting

### Connection Issues

**Problem:** MCP server connection fails

**Solution:**
1. Verify Node.js dependencies are installed:
   ```bash
   cd google-calendar-mcp-server && npm install
   cd spotify-mcp-server && npm install
   ```
2. Check that Node.js version is 18 or higher: `node --version`
3. Verify environment variables are set: `python scripts/check_env.py`

### Authentication Errors

**Problem:** "Invalid credentials" or "Unauthorized" errors

**Solution:**
1. Verify credentials in `.env` file are correct
2. Regenerate refresh tokens:
   ```bash
   # For Google Calendar
   cd google-calendar-mcp-server && node get-refresh-token.js
   
   # For Spotify
   cd spotify-mcp-server && node get-refresh-token.js
   ```
3. Ensure required APIs are enabled in respective consoles

### No Events/Devices Found

**Problem:** Calendar or Spotify returns empty results

**Solution:**
1. Check that you have events/devices in your actual Google Calendar or Spotify account
2. Verify the correct calendar ID is set (default: "primary")
3. For Spotify, ensure you have an active device (open Spotify on your phone/computer)

For more help, see:
- [Google Calendar Setup](docs/GOOGLE_CALENDAR_SETUP.md)
- [Spotify Setup](docs/SPOTIFY_SETUP.md)
- [Contributing Guide](CONTRIBUTING.md)

## Contributing

Contributions are welcome! This is a playground project for experimenting with realtime audio and MCP integrations.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

See [LICENSE](LICENSE) file for details.

## Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
