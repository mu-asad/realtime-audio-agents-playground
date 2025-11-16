#!/usr/bin/env python3
"""
Example: Using Calendar and Spotify Tools with RealtimeAgent

This example demonstrates how to use all the exposed calendar and Spotify tools
with the Azure Realtime Agent.
"""

import asyncio
from dotenv import load_dotenv
from agents.realtime import RealtimeAgent
from src.agent_host.calendar_agent import CalendarAgentHost
from src.agent_host.spotify_agent import SpotifyAgentHost

async def main():
    """Main function demonstrating tool usage."""
    load_dotenv()

    # Initialize agents
    calendar_agent = CalendarAgentHost()
    spotify_agent = SpotifyAgentHost()

    try:
        # Connect to MCP servers
        print("Connecting to MCP servers...")
        await calendar_agent.connect_to_mcp_server()
        await spotify_agent.connect_to_mcp_server()
        print("Connected!\n")

        # Get all tools
        calendar_tools = calendar_agent.get_all_tools()
        spotify_tools = spotify_agent.get_all_tools()
        all_tools = calendar_tools + spotify_tools

        print(f"Loaded {len(calendar_tools)} calendar tools")
        print(f"Loaded {len(spotify_tools)} Spotify tools")
        print(f"Total: {len(all_tools)} tools\n")

        # Create a realtime agent with all tools
        agent = RealtimeAgent(
            tools=all_tools,
            name="VoiceAssistant",
            instructions="""You are a helpful voice assistant with access to:
            
            Calendar Management:
            - List, create, update, and delete calendar events
            - Check free/busy times
            - Get event details
            
            Music Control:
            - Play, pause, resume music on Spotify
            - Skip tracks (next/previous)
            - Search for songs
            - Check what's currently playing
            - Get available devices
            - Transfer playback between devices
            
            Keep responses brief and conversational.
            Always confirm before creating, updating, or deleting events.
            """,
        )

        print("RealtimeAgent created successfully!")
        print(f"Agent name: {agent.name}")
        print(f"Number of tools: {len(all_tools)}")

        # Example: Access individual tools
        print("\n--- Example: Individual Tool Access ---")

        # Calendar tools
        print("\nCalendar tool methods:")
        print("  - calendar_agent.get_list_events_tool()")
        print("  - calendar_agent.get_create_event_tool()")
        print("  - calendar_agent.get_update_event_tool()")
        print("  - calendar_agent.get_delete_event_tool()")
        print("  - calendar_agent.get_event_tool()")
        print("  - calendar_agent.get_free_busy_tool()")

        # Spotify tools
        print("\nSpotify tool methods:")
        print("  - spotify_agent.get_devices_tool()")
        print("  - spotify_agent.get_transfer_playback_tool()")
        print("  - spotify_agent.get_play_tool()")
        print("  - spotify_agent.get_pause_tool()")
        print("  - spotify_agent.get_resume_tool()")
        print("  - spotify_agent.get_next_track_tool()")
        print("  - spotify_agent.get_previous_track_tool()")
        print("  - spotify_agent.get_search_tracks_tool()")
        print("  - spotify_agent.get_current_playback_tool()")

        # You can also call the underlying methods directly if needed
        print("\n--- Example: Direct Method Calls ---")

        # List calendar events
        print("\nListing calendar events...")
        events = await calendar_agent.list_events(max_results=5)
        print(f"Found {len(events.get('items', []))} events")

        # Get Spotify devices
        print("\nGetting Spotify devices...")
        devices = await spotify_agent.get_devices()
        print(f"Found {len(devices.get('devices', []))} devices")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        await calendar_agent.close()
        await spotify_agent.close()
        print("\nClosed all connections")


if __name__ == "__main__":
    asyncio.run(main())

