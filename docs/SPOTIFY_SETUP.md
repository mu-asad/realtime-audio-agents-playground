# Spotify Integration Setup Guide

This guide will walk you through setting up the Spotify MCP integration for the Azure Realtime Audio Playground project.

## Overview

The Spotify MCP server enables your AI agent to control Spotify playback through natural language commands. The agent can:
- List and select playback devices
- Play music by search query or URI
- Control playback (play, pause, resume)
- Navigate tracks (next, previous)
- Search for tracks
- Get current playback state

## Prerequisites

- **Node.js**: Version 18 or higher
- **Python**: Version 3.10 or higher
- **Spotify Account**: Premium account required for playback control
- **Active Spotify Device**: You need at least one active Spotify device (desktop app, mobile app, or web player)

## Step 1: Create a Spotify App

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create App"**
4. Fill in the app details:
   - **App Name**: "Azure Realtime Audio Assistant" (or any name you prefer)
   - **App Description**: "Personal assistant with Spotify playback control"
   - **Redirect URI**: `http://localhost:8888/callback`
   - **APIs Used**: Select "Web API"
5. Accept the terms and click **"Create"**
6. On the app page, click **"Settings"**
7. Note down:
   - **Client ID**
   - **Client Secret** (click "View client secret")

## Step 2: Configure Environment Variables

1. Copy the `.env.example` file to `.env` if you haven't already:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your Spotify credentials:
   ```bash
   SPOTIFY_CLIENT_ID=your-spotify-client-id-here
   SPOTIFY_CLIENT_SECRET=your-spotify-client-secret-here
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   ```

## Step 3: Install Dependencies

1. Install Node.js dependencies for the Spotify MCP server:
   ```bash
   cd spotify-mcp-server
   npm install
   cd ..
   ```

2. Python dependencies should already be installed from the main requirements.txt

## Step 4: Get Spotify Refresh Token

To get a refresh token, we'll use a helper script:

1. Create a file `spotify-mcp-server/get-refresh-token.js`:
   ```javascript
   // This script will be created in the next step
   ```

2. Run the token generation script:
   ```bash
   cd spotify-mcp-server
   node get-refresh-token.js
   ```

3. The script will:
   - Open your browser
   - Ask you to authorize the app
   - Display the refresh token

4. Copy the refresh token and add it to your `.env` file:
   ```bash
   SPOTIFY_REFRESH_TOKEN=your-refresh-token-here
   ```

## Step 5: Required Spotify Scopes

The Spotify MCP server requires the following OAuth scopes:
- `user-read-playback-state` - Read access to a user's player state
- `user-modify-playback-state` - Write access to a user's playback state
- `user-read-currently-playing` - Read access to a user's currently playing content
- `streaming` - Control playback on Spotify clients and SDKs

These scopes are automatically requested by the refresh token script.

## Step 6: Test the Integration

Test the Spotify integration:

```bash
# Run the test script
python examples/test_spotify.py
```

The test script will:
1. Connect to the Spotify MCP server
2. List available playback devices
3. Get current playback state
4. Test basic playback controls

## Troubleshooting

### "No active device found"

**Problem**: The Spotify API requires an active playback device.

**Solution**: 
1. Open Spotify on any device (desktop, mobile, web player)
2. Start playing any song
3. You can pause it, but the device must remain active
4. Alternatively, open the Spotify web player: https://open.spotify.com

### "Invalid client credentials"

**Problem**: Your client ID or secret is incorrect.

**Solution**:
1. Double-check your credentials in the Spotify Developer Dashboard
2. Ensure there are no extra spaces in your `.env` file
3. The client secret should be revealed by clicking "View client secret"

### "Invalid refresh token"

**Problem**: The refresh token is expired or invalid.

**Solution**:
1. Re-run the `get-refresh-token.js` script
2. Update the `SPOTIFY_REFRESH_TOKEN` in your `.env` file
3. Ensure you're using the same client ID and secret that generated the token

### "403 Forbidden" errors

**Problem**: You're trying to control playback without a Premium account.

**Solution**: 
- Spotify's Web API requires a Premium subscription for playback control
- You can still use search functionality with a free account

## Demo Scenarios

Once setup is complete, try these natural language commands with your agent:

### Device Selection
- "Show me my Spotify devices"
- "Switch to my laptop for Spotify"
- "Play music on my phone"

### Playback Control
- "Play some lofi beats on Spotify"
- "Pause Spotify"
- "Resume my music"
- "Play Bohemian Rhapsody"

### Navigation
- "Skip this song"
- "Play the previous track"
- "Next song please"

### Search
- "Search for songs by Taylor Swift"
- "Find some jazz music"

### Status
- "What's playing on Spotify?"
- "What song is this?"

## Architecture

The Spotify integration follows the same MCP architecture as the calendar integration:

```
┌─────────────────┐      MCP Protocol      ┌──────────────────────┐
│  Python Agent   │ ◄──────────────────► │  Spotify MCP Server  │
│  (spotify_agent)│      stdio/JSON       │     (Node.js)        │
└─────────────────┘                       └──────────────────────┘
                                                      │
                                                      ▼
                                           ┌─────────────────────┐
                                           │  Spotify Web API    │
                                           └─────────────────────┘
```

### Components

1. **Spotify MCP Server** (`spotify-mcp-server/server.js`)
   - Handles Spotify Web API authentication
   - Implements MCP protocol
   - Exposes playback control tools

2. **Spotify Agent Host** (`src/agent_host/spotify_agent.py`)
   - Python client for the MCP server
   - Provides clean async API
   - Manages server lifecycle

3. **Test Scripts** (`examples/test_spotify.py`)
   - Integration tests
   - Usage examples
   - Troubleshooting tools

## Available Tools

The Spotify MCP server exposes these tools:

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

## Security Notes

- Never commit your `.env` file to version control
- Keep your client secret confidential
- Refresh tokens should be stored securely
- The redirect URI must match exactly in Spotify settings
- Tokens can be revoked from the Spotify dashboard if compromised

## Next Steps

- Integrate with Azure Realtime Audio for voice-controlled music
- Combine with calendar agent for contextual music selection
- Add playlist management capabilities
- Implement volume control
- Add queue management

## Resources

- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Spotify OAuth Guide](https://developer.spotify.com/documentation/general/guides/authorization-guide/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
