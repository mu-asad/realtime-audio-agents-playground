#!/usr/bin/env python3
"""
Test script for Google Calendar MCP integration.

This script tests all the main calendar operations:
- Listing events
- Creating events
- Getting event details
- Updating events
- Deleting events
- Getting free/busy information
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_host import CalendarAgentHost


async def test_calendar_operations():
    """Test all calendar operations."""
    agent = CalendarAgentHost()
    created_event_id = None

    try:
        print("=" * 60)
        print("Google Calendar MCP Integration Test")
        print("=" * 60)

        # Connect to MCP server
        print("\n[1/6] Connecting to Google Calendar MCP server...")
        await agent.connect_to_mcp_server()
        print("✓ Connected successfully")

        # List available tools
        print("\n[2/6] Listing available tools...")
        tools = await agent.list_tools()
        for tool in tools:
            print(f"  ✓ {tool['name']}: {tool['description']}")

        # Test listing events
        print("\n[3/6] Testing list_events...")
        now = datetime.utcnow()
        week_later = now + timedelta(days=7)
        
        events_result = await agent.list_events(
            time_min=now.isoformat() + "Z",
            time_max=week_later.isoformat() + "Z",
            max_results=5,
        )
        
        print(f"  ✓ Found {len(events_result.get('events', []))} events")
        if events_result.get("events"):
            for event in events_result["events"][:3]:
                print(f"    - {event.get('summary', 'No title')}: {event.get('start', {}).get('dateTime', 'No time')}")

        # Test creating an event
        print("\n[4/6] Testing create_event...")
        start_time = (now + timedelta(days=2)).replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        create_result = await agent.create_event(
            summary="MCP Integration Test Meeting",
            start_time=start_time.isoformat() + "Z",
            end_time=end_time.isoformat() + "Z",
            description="This is a test event created by the MCP integration test script.",
            location="Virtual Meeting Room",
        )
        
        if "event" in create_result:
            created_event_id = create_result["event"]["id"]
            print(f"  ✓ Created event: {create_result['event']['summary']}")
            print(f"    Event ID: {created_event_id}")
        else:
            print(f"  ✗ Failed to create event: {create_result}")

        # Test getting event details
        if created_event_id:
            print("\n[5/6] Testing get_event...")
            event_result = await agent.get_event(created_event_id)
            if "event" in event_result:
                print(f"  ✓ Retrieved event: {event_result['event']['summary']}")
                print(f"    Description: {event_result['event'].get('description', 'N/A')}")
            else:
                print(f"  ✗ Failed to get event: {event_result}")

            # Test updating the event
            print("\n[6/6] Testing update_event...")
            update_result = await agent.update_event(
                event_id=created_event_id,
                summary="UPDATED: MCP Integration Test Meeting",
                description="This event has been updated by the test script.",
            )
            
            if "event" in update_result:
                print(f"  ✓ Updated event: {update_result['event']['summary']}")
            else:
                print(f"  ✗ Failed to update event: {update_result}")

        # Test free/busy
        print("\n[Bonus] Testing get_free_busy...")
        freebusy_result = await agent.get_free_busy(
            time_min=now.isoformat() + "Z",
            time_max=week_later.isoformat() + "Z",
        )
        
        if "freeBusy" in freebusy_result:
            busy_periods = freebusy_result["freeBusy"].get("busy", [])
            print(f"  ✓ Found {len(busy_periods)} busy periods")
        else:
            print(f"  ✗ Failed to get free/busy: {freebusy_result}")

        # Clean up: delete the test event
        if created_event_id:
            print("\n[Cleanup] Deleting test event...")
            delete_result = await agent.delete_event(created_event_id)
            if delete_result.get("success"):
                print(f"  ✓ Successfully deleted test event")
            else:
                print(f"  ✗ Failed to delete event: {delete_result}")
                print(f"    Please manually delete event ID: {created_event_id}")

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to clean up if event was created
        if created_event_id:
            print(f"\nAttempting to clean up test event: {created_event_id}")
            try:
                await agent.delete_event(created_event_id)
                print("✓ Cleaned up test event")
            except Exception as cleanup_error:
                print(f"✗ Failed to clean up: {cleanup_error}")
                print(f"Please manually delete event ID: {created_event_id}")
        
        return False
    finally:
        await agent.close()

    return True


if __name__ == "__main__":
    success = asyncio.run(test_calendar_operations())
    sys.exit(0 if success else 1)
