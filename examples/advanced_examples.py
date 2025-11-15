#!/usr/bin/env python3
"""
Advanced examples for Google Calendar MCP integration.

This script demonstrates various calendar scenarios:
- Checking today's schedule
- Finding free time slots
- Scheduling recurring meetings
- Managing attendees
- Searching for specific events
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_host import CalendarAgentHost


async def example_check_todays_schedule(agent):
    """Example: Check what's on the calendar today."""
    print("\n" + "=" * 60)
    print("Example 1: Check Today's Schedule")
    print("=" * 60)

    now = datetime.utcnow()
    end_of_day = now.replace(hour=23, minute=59, second=59)

    result = await agent.list_events(
        time_min=now.isoformat() + "Z", time_max=end_of_day.isoformat() + "Z"
    )

    events = result.get("events", [])
    print(f"\nYou have {len(events)} event(s) today:")

    if events:
        for event in events:
            start = event.get("start", {}).get("dateTime", "No time")
            summary = event.get("summary", "No title")
            print(f"  • {start}: {summary}")
    else:
        print("  Your calendar is clear today!")


async def example_find_free_time(agent):
    """Example: Find free time slots this week."""
    print("\n" + "=" * 60)
    print("Example 2: Find Free Time Slots")
    print("=" * 60)

    now = datetime.utcnow()
    week_later = now + timedelta(days=7)

    freebusy = await agent.get_free_busy(
        time_min=now.isoformat() + "Z", time_max=week_later.isoformat() + "Z"
    )

    busy_periods = freebusy.get("freeBusy", {}).get("busy", [])
    print(f"\nYou have {len(busy_periods)} busy period(s) this week")

    if busy_periods:
        for period in busy_periods[:5]:  # Show first 5
            start = period.get("start", "Unknown")
            end = period.get("end", "Unknown")
            print(f"  • Busy: {start} to {end}")
    else:
        print("  You're completely free this week!")


async def example_search_events(agent):
    """Example: Search for events by keyword."""
    print("\n" + "=" * 60)
    print("Example 3: Search Events by Keyword")
    print("=" * 60)

    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    week_later = now + timedelta(days=7)

    # Search for meetings
    result = await agent.list_events(
        time_min=month_ago.isoformat() + "Z",
        time_max=week_later.isoformat() + "Z",
        query="meeting",
        max_results=5,
    )

    events = result.get("events", [])
    print(f'\nFound {len(events)} event(s) matching "meeting":')

    for event in events:
        start = event.get("start", {}).get("dateTime", "No time")
        summary = event.get("summary", "No title")
        print(f"  • {start}: {summary}")


async def example_create_quick_event(agent):
    """Example: Create a quick event."""
    print("\n" + "=" * 60)
    print("Example 4: Create a Quick Event")
    print("=" * 60)

    # Create an event tomorrow at 2pm
    tomorrow = datetime.utcnow() + timedelta(days=1)
    start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)

    result = await agent.create_event(
        summary="Coffee Break",
        start_time=start_time.isoformat() + "Z",
        end_time=end_time.isoformat() + "Z",
        description="Time for a quick coffee",
    )

    if "event" in result:
        event_id = result["event"]["id"]
        print(f'\n✓ Created event: {result["event"]["summary"]}')
        print(f"  Event ID: {event_id}")
        return event_id
    else:
        print(f"\n✗ Failed to create event: {result}")
        return None


async def example_update_event(agent, event_id):
    """Example: Update an existing event."""
    print("\n" + "=" * 60)
    print("Example 5: Update Event Details")
    print("=" * 60)

    if not event_id:
        print("No event ID provided, skipping...")
        return

    # Update the event
    result = await agent.update_event(
        event_id=event_id,
        summary="Updated: Coffee Break",
        description="Extended coffee break - bring snacks!",
    )

    if "event" in result:
        print(f'\n✓ Updated event: {result["event"]["summary"]}')
        print(f'  New description: {result["event"].get("description", "N/A")}')
    else:
        print(f"\n✗ Failed to update event: {result}")


async def example_list_upcoming_week(agent):
    """Example: List all events for the upcoming week."""
    print("\n" + "=" * 60)
    print("Example 6: Upcoming Week Schedule")
    print("=" * 60)

    now = datetime.utcnow()
    week_later = now + timedelta(days=7)

    result = await agent.list_events(
        time_min=now.isoformat() + "Z",
        time_max=week_later.isoformat() + "Z",
        max_results=20,
    )

    events = result.get("events", [])
    print(f"\nYou have {len(events)} event(s) in the next 7 days:")

    # Group events by day
    events_by_day = {}
    for event in events:
        start_str = event.get("start", {}).get("dateTime")
        if start_str:
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            day_key = start.strftime("%A, %B %d")
            if day_key not in events_by_day:
                events_by_day[day_key] = []
            events_by_day[day_key].append(event)

    for day, day_events in events_by_day.items():
        print(f"\n  {day}:")
        for event in day_events:
            start = event.get("start", {}).get("dateTime", "No time")
            summary = event.get("summary", "No title")
            time_str = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime("%I:%M %p")
            print(f"    • {time_str}: {summary}")


async def cleanup_event(agent, event_id):
    """Clean up test event."""
    if event_id:
        print("\n" + "=" * 60)
        print("Cleanup")
        print("=" * 60)

        result = await agent.delete_event(event_id)
        if result.get("success"):
            print("\n✓ Cleaned up test event")
        else:
            print(f"\n✗ Failed to clean up: {result}")
            print(f"  Please manually delete event ID: {event_id}")


async def main():
    """Run all examples."""
    agent = CalendarAgentHost()
    created_event_id = None

    try:
        print("=" * 60)
        print("Google Calendar MCP Integration - Advanced Examples")
        print("=" * 60)

        # Connect to MCP server
        print("\nConnecting to Google Calendar MCP server...")
        await agent.connect_to_mcp_server()
        print("✓ Connected")

        # Run examples
        await example_check_todays_schedule(agent)
        await example_find_free_time(agent)
        await example_search_events(agent)

        created_event_id = await example_create_quick_event(agent)
        if created_event_id:
            await example_update_event(agent, created_event_id)

        await example_list_upcoming_week(agent)

        # Clean up
        if created_event_id:
            await cleanup_event(agent, created_event_id)

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()

        # Try to clean up
        if created_event_id:
            try:
                await agent.delete_event(created_event_id)
                print(f"\n✓ Cleaned up test event: {created_event_id}")
            except Exception:
                print(f"\nPlease manually delete event ID: {created_event_id}")

        return False
    finally:
        await agent.close()

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
