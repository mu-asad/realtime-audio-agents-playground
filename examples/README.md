# Examples

This directory contains example scripts demonstrating how to use the Google Calendar MCP integration.

## Available Examples

### 1. `test_calendar.py` - Basic Test Suite

Comprehensive test script that validates all calendar operations.

**Usage:**
```bash
python examples/test_calendar.py
```

**What it tests:**
- ✓ Connecting to MCP server
- ✓ Listing available tools
- ✓ Listing events for a date range
- ✓ Creating a new event
- ✓ Getting event details
- ✓ Updating an event
- ✓ Deleting an event
- ✓ Getting free/busy information

**When to use:**
- After initial setup to verify everything works
- After making changes to the code
- As a reference for basic operations

### 2. `advanced_examples.py` - Real-World Scenarios

Demonstrates practical calendar management scenarios.

**Usage:**
```bash
python examples/advanced_examples.py
```

**Scenarios covered:**
1. **Check Today's Schedule** - List all events for today
2. **Find Free Time** - Identify available time slots
3. **Search Events** - Find events by keyword
4. **Quick Event Creation** - Create a simple event
5. **Update Event Details** - Modify existing events
6. **Weekly Overview** - View upcoming week schedule

**When to use:**
- To learn practical usage patterns
- As templates for your own code
- To understand different API capabilities

## Running the Examples

### Prerequisites

1. **Install dependencies:**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node.js dependencies (for MCP server)
   cd google-calendar-mcp-server && npm install && cd ..
   ```

2. **Set up credentials:**
   ```bash
   # Copy example config
   cp .env.example .env
   
   # Add your Google Calendar credentials
   # See docs/GOOGLE_CALENDAR_SETUP.md for details
   ```

3. **Verify setup:**
   ```bash
   python scripts/verify_setup.py
   ```

### Running Tests

```bash
# Run basic tests
python examples/test_calendar.py

# Run advanced examples
python examples/advanced_examples.py
```

## Example Output

### Basic Test Suite

```
======================================================================
Google Calendar MCP Integration Test
======================================================================

[1/6] Connecting to Google Calendar MCP server...
✓ Connected successfully

[2/6] Listing available tools...
  ✓ list_events: List calendar events within a time range
  ✓ get_event: Get details of a specific calendar event by ID
  ✓ create_event: Create a new calendar event
  ...

[3/6] Testing list_events...
  ✓ Found 3 events
    - Team Standup: 2025-11-15T09:00:00Z
    - Client Meeting: 2025-11-15T14:00:00Z
    ...

======================================================================
All tests completed!
======================================================================
```

### Advanced Examples

```
======================================================================
Example 1: Check Today's Schedule
======================================================================

You have 3 event(s) today:
  • 2025-11-15T09:00:00Z: Team Standup
  • 2025-11-15T14:00:00Z: Client Meeting
  • 2025-11-15T16:30:00Z: Code Review

======================================================================
Example 2: Find Free Time Slots
======================================================================

You have 2 busy period(s) this week
  • Busy: 2025-11-15T09:00:00Z to 2025-11-15T10:00:00Z
  • Busy: 2025-11-15T14:00:00Z to 2025-11-15T15:00:00Z
```

## Creating Your Own Examples

To create a new example:

1. **Create a new Python file:**
   ```python
   #!/usr/bin/env python3
   import asyncio
   import sys
   from pathlib import Path
   
   sys.path.insert(0, str(Path(__file__).parent.parent))
   from src.agent_host import CalendarAgentHost
   
   async def main():
       agent = CalendarAgentHost()
       try:
           await agent.connect_to_mcp_server()
           # Your code here
       finally:
           await agent.close()
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

2. **Use the agent methods:**
   - `list_events()` - List events
   - `get_event()` - Get event details
   - `create_event()` - Create new event
   - `update_event()` - Update event
   - `delete_event()` - Delete event
   - `get_free_busy()` - Check availability

3. **Format and check your code:**
   ```bash
   black examples/your_example.py
   ruff check examples/your_example.py
   ```

## Common Patterns

### Listing Today's Events

```python
from datetime import datetime, timedelta

now = datetime.utcnow()
end_of_day = now.replace(hour=23, minute=59, second=59)

events = await agent.list_events(
    time_min=now.isoformat() + "Z",
    time_max=end_of_day.isoformat() + "Z"
)
```

### Creating an Event

```python
from datetime import datetime, timedelta

start = datetime.utcnow() + timedelta(days=1)
end = start + timedelta(hours=1)

result = await agent.create_event(
    summary="Team Meeting",
    start_time=start.isoformat() + "Z",
    end_time=end.isoformat() + "Z",
    description="Weekly sync",
    attendees=["colleague@example.com"]
)
```

### Finding Free Time

```python
from datetime import datetime, timedelta

now = datetime.utcnow()
week_later = now + timedelta(days=7)

freebusy = await agent.get_free_busy(
    time_min=now.isoformat() + "Z",
    time_max=week_later.isoformat() + "Z"
)

busy_periods = freebusy.get("freeBusy", {}).get("busy", [])
```

## Troubleshooting

### "Connection refused" error

Make sure the MCP server dependencies are installed:
```bash
cd mcp-server && npm install
```

### "Invalid credentials" error

Check your `.env` file:
- Verify `GOOGLE_CLIENT_ID` is correct
- Verify `GOOGLE_CLIENT_SECRET` is correct
- Verify `GOOGLE_REFRESH_TOKEN` is valid

Get a new refresh token if needed:
```bash
cd scripts && node get-refresh-token.js
```

### No events found

Your calendar might be empty or the time range might not include any events. Try:
- Creating a test event in Google Calendar
- Adjusting the time range
- Checking the calendar ID in `.env`

## Next Steps

After running the examples:
1. Review the code to understand the API
2. Modify the examples to fit your needs
3. Create your own scripts
4. Integrate with your Azure Realtime Audio agent

For more information, see:
- [Setup Guide](../docs/GOOGLE_CALENDAR_SETUP.md)
- [System Instructions](../docs/AGENT_SYSTEM_INSTRUCTIONS.md)
- [Main README](../README.md)
