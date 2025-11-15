# azure-realtime-audio-playground

A sandbox for experimenting with live audio (mic → Azure Realtime → audio/text back), with minimal assumptions about tech stack.

## Features

- **Azure Realtime Audio Integration**: Connect live audio streams to Azure's realtime services
- **Google Calendar MCP Integration**: Manage calendar events through the Model Context Protocol (MCP)
- **Personal Assistant Agent**: AI-powered assistant with calendar management capabilities

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Google Cloud Platform account (for calendar integration)

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

3. Install Node.js dependencies for the MCP server:
   ```bash
   cd mcp-server
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

## Project Structure

```
azure-realtime-audio-playground/
├── docs/                          # Documentation
│   └── GOOGLE_CALENDAR_SETUP.md  # Calendar integration guide
├── examples/                      # Example scripts
│   └── test_calendar.py          # Calendar integration tests
├── mcp-server/                    # Google Calendar MCP server
│   ├── server.js                 # MCP server implementation
│   └── package.json              # Node.js dependencies
├── src/                          # Source code
│   └── agent_host/               # Agent host implementation
│       ├── calendar_agent.py     # Calendar agent host
│       └── __init__.py
├── .env.example                  # Environment variables template
├── pyproject.toml               # Python project configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Available Calendar Tools

The MCP server exposes these tools to the agent:

| Tool | Description |
|------|-------------|
| `list_events` | List calendar events within a time range |
| `get_event` | Get details of a specific event |
| `create_event` | Create a new calendar event |
| `update_event` | Update an existing event |
| `delete_event` | Delete/cancel an event |
| `get_free_busy` | Get free/busy information |

## Usage Example

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

## Architecture

The project uses the Model Context Protocol (MCP) to separate concerns:

- **Agent Host (Python)**: Manages the AI agent and orchestrates tool calls
- **MCP Server (Node.js)**: Handles Google Calendar API interactions
- **MCP Protocol**: Standardized communication between agent and calendar server

This architecture allows for:
- Easy testing of individual components
- Swapping out different calendar providers
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
cd mcp-server && npm run lint
```

## Contributing

Contributions are welcome! This is a playground project for experimenting with Azure Realtime Audio and MCP integrations.

## License

See [LICENSE](LICENSE) file for details.

## Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
