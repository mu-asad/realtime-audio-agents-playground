#!/usr/bin/env python3
"""
Test script to verify that all calendar and spotify tools are properly exposed.
"""

import asyncio
from src.agent_host.calendar_agent import CalendarAgentHost
from src.agent_host.spotify_agent import SpotifyAgentHost
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama for colored output
init()


async def test_calendar_tools():
    """Test that all calendar tools are properly exposed."""
    print(f"\n{Fore.CYAN}=== Testing Calendar Tools ==={Style.RESET_ALL}")

    calendar_agent = CalendarAgentHost()

    try:
        await calendar_agent.connect_to_mcp_server()
        print(f"{Fore.GREEN}✓ Calendar agent connected{Style.RESET_ALL}")

        # Get all tools
        tools = calendar_agent.get_all_tools()
        print(f"\n{Fore.YELLOW}Total Calendar Tools: {len(tools)}{Style.RESET_ALL}")

        for i, tool in enumerate(tools, 1):
            tool_name = tool.__name__ if hasattr(tool, '__name__') else str(tool)
            tool_doc = tool.__doc__ if hasattr(tool, '__doc__') else "No description"
            # Extract first line of docstring
            first_line = tool_doc.split('\n')[0] if tool_doc else "No description"
            print(f"{Fore.GREEN}  {i}. {tool_name}: {first_line}{Style.RESET_ALL}")

        # List individual tool getters
        print(f"\n{Fore.YELLOW}Individual Tool Methods:{Style.RESET_ALL}")
        tool_methods = [
            "get_list_events_tool",
            "get_create_event_tool",
            "get_update_event_tool",
            "get_delete_event_tool",
            "get_event_tool",
            "get_free_busy_tool"
        ]

        for method in tool_methods:
            if hasattr(calendar_agent, method):
                print(f"{Fore.GREEN}  ✓ {method}(){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ✗ {method}() - MISSING{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}✗ Error testing calendar tools: {e}{Style.RESET_ALL}")
    finally:
        await calendar_agent.close()


async def test_spotify_tools():
    """Test that all spotify tools are properly exposed."""
    print(f"\n{Fore.CYAN}=== Testing Spotify Tools ==={Style.RESET_ALL}")

    spotify_agent = SpotifyAgentHost()

    try:
        await spotify_agent.connect_to_mcp_server()
        print(f"{Fore.GREEN}✓ Spotify agent connected{Style.RESET_ALL}")

        # Get all tools
        tools = spotify_agent.get_all_tools()
        print(f"\n{Fore.YELLOW}Total Spotify Tools: {len(tools)}{Style.RESET_ALL}")

        for i, tool in enumerate(tools, 1):
            tool_name = tool.__name__ if hasattr(tool, '__name__') else str(tool)
            tool_doc = tool.__doc__ if hasattr(tool, '__doc__') else "No description"
            # Extract first line of docstring
            first_line = tool_doc.split('\n')[0] if tool_doc else "No description"
            print(f"{Fore.GREEN}  {i}. {tool_name}: {first_line}{Style.RESET_ALL}")

        # List individual tool getters
        print(f"\n{Fore.YELLOW}Individual Tool Methods:{Style.RESET_ALL}")
        tool_methods = [
            "get_devices_tool",
            "get_transfer_playback_tool",
            "get_play_tool",
            "get_pause_tool",
            "get_resume_tool",
            "get_next_track_tool",
            "get_previous_track_tool",
            "get_search_tracks_tool",
            "get_current_playback_tool"
        ]

        for method in tool_methods:
            if hasattr(spotify_agent, method):
                print(f"{Fore.GREEN}  ✓ {method}(){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}  ✗ {method}() - MISSING{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}✗ Error testing Spotify tools: {e}{Style.RESET_ALL}")
    finally:
        await spotify_agent.close()


async def main():
    """Run all tests."""
    load_dotenv()

    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  Tool Exposure Test Suite{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

    await test_calendar_tools()
    await test_spotify_tools()

    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  All tests completed!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    asyncio.run(main())

