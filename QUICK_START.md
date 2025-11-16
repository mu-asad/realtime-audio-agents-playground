# Quick Reference: OpenAI Agent Integration

## Start the Agent

```bash
python openai-agent-integrated.py
```

## Voice Commands

### Calendar
```
"What's on my calendar today?"
"Schedule a meeting tomorrow at 2 PM"
"Do I have any events this week?"
"Create an event called Team Sync on Friday at 3 PM"
```

### Spotify
```
"Play Bohemian Rhapsody"
"Play some jazz music"
"Pause the music"
"Skip this song"
"What's playing?"
"Show me my devices"
```

## CLI Options (using run_agent.py)

```bash
# Choose voice
python run_agent.py --voice coral

# Adjust speed
python run_agent.py --speed 1.2

# Disable integrations
python run_agent.py --no-calendar
python run_agent.py --no-spotify

# Debug mode
python run_agent.py --debug
```

## Available Tools

**Calendar (3):**
- list_calendar_events
- create_calendar_event
- get_calendar_event

**Spotify (6):**
- spotify_play
- spotify_pause
- spotify_next
- spotify_previous
- spotify_get_devices
- spotify_get_current_track

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Calendar not connecting | Run `npm install` in `google-calendar-mcp-server/` |
| Spotify not connecting | Run `npm install` in `spotify-mcp-server/` |
| No audio | Check microphone permissions |
| Tool calls fail | Verify .env credentials |

## Files

- `openai-agent-integrated.py` - Main integration
- `run_agent.py` - Quick start CLI
- `src/agent_host/calendar_agent.py` - Calendar MCP
- `src/agent_host/spotify_agent.py` - Spotify MCP

## Configuration (.env)

Required:
```env
OPENAI_API_KEY=your_key
```

Optional (for integrations):
```env
# Calendar
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REFRESH_TOKEN=...

# Spotify
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REFRESH_TOKEN=...
```

## Extending

Add new agent:
1. Create `src/agent_host/your_agent.py`
2. Add `create_your_tools()` function
3. Add to `handle_tool_call()`
4. Initialize in `main()`

---
Ready to go! Just run: `python openai-agent-integrated.py`

