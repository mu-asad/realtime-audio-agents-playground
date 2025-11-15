# Spotify MCP Server

A Model Context Protocol (MCP) server for controlling Spotify playback via the Spotify Web API.

## Features

- **Device Management**: List and select playback devices
- **Playback Control**: Play, pause, resume music
- **Track Navigation**: Skip to next/previous tracks
- **Search**: Find tracks on Spotify
- **Status**: Get current playback information

## Installation

Install dependencies:

```bash
npm install
```

## Configuration

Create a `.env` file in the repository root with:

```bash
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_REFRESH_TOKEN=your-refresh-token
```

## Getting a Refresh Token

Run the included script to obtain a refresh token:

```bash
node get-refresh-token.js
```

This will:
1. Open your browser for Spotify authorization
2. Display the refresh token
3. Guide you to add it to your `.env` file

## Usage

The MCP server is designed to be used via the Python agent host:

```python
from src.agent_host.spotify_agent import SpotifyAgentHost

async def main():
    agent = SpotifyAgentHost()
    await agent.connect_to_mcp_server()
    
    # Get devices
    devices = await agent.get_devices()
    
    # Play music
    await agent.play(search_query="lofi beats")
    
    # Control playback
    await agent.pause()
    await agent.next_track()
    
    await agent.close()
```

## Available Tools

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

## Testing

Run standalone (requires active Spotify session):

```bash
# Test the server directly
node server.js
```

Or use the Python test script:

```bash
python examples/test_spotify.py
```

## Requirements

- Node.js 18 or higher
- Spotify Premium account (required for playback control)
- Active Spotify device (desktop, mobile, or web player)

## Architecture

The server implements the Model Context Protocol (MCP) and communicates via stdio:

```
Python Client → stdio → MCP Server → Spotify Web API
```

## Troubleshooting

### No devices found
- Open Spotify on any device
- Start playing a song (can be paused)
- The device must remain active

### 403 Forbidden
- Playback control requires Spotify Premium
- Search functionality works with free accounts

### Token expired
- Re-run `get-refresh-token.js`
- Update `SPOTIFY_REFRESH_TOKEN` in `.env`

## Documentation

See [docs/SPOTIFY_SETUP.md](../docs/SPOTIFY_SETUP.md) for detailed setup instructions.

## License

See repository LICENSE file.
