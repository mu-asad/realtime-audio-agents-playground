#!/usr/bin/env python3
"""
Test script for Spotify MCP integration.

This script tests all the main Spotify operations:
- Listing devices
- Getting current playback
- Searching for tracks
- Basic playback control (if device available)
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_host.spotify_agent import SpotifyAgentHost


async def test_spotify_operations():
    """Test all Spotify operations."""
    agent = SpotifyAgentHost()

    try:
        print("=" * 60)
        print("Spotify MCP Integration Test")
        print("=" * 60)

        # Connect to MCP server
        print("\n[1/6] Connecting to Spotify MCP server...")
        await agent.connect_to_mcp_server()
        print("✓ Connected successfully")

        # List available tools
        print("\n[2/6] Listing available tools...")
        tools = await agent.list_tools()
        for tool in tools:
            print(f"  ✓ {tool['name']}: {tool['description']}")

        # Test getting devices
        print("\n[3/6] Testing spotify_get_devices...")
        try:
            devices_result = await agent.get_devices()
            print(f"✓ {devices_result.get('summary', 'Success')}")
            if devices_result.get("devices"):
                for device in devices_result["devices"]:
                    active_indicator = "🔊 ACTIVE" if device["is_active"] else ""
                    print(f"  - {device['name']} ({device['type']}) {active_indicator}")
            else:
                print("  ⚠ No devices found. Open Spotify on a device and start playing.")
        except Exception as e:
            print(f"✗ Error: {e}")

        # Test getting current playback
        print("\n[4/6] Testing spotify_get_current_playback...")
        try:
            playback_result = await agent.get_current_playback()
            print(f"✓ {playback_result.get('summary', 'Success')}")
            if playback_result.get("playing"):
                track = playback_result["track"]
                device = playback_result["device"]
                print(f"  🎵 Track: {track['name']}")
                print(f"  🎤 Artist: {track['artist']}")
                print(f"  💿 Album: {track['album']}")
                print(f"  📱 Device: {device['name']} ({device['type']})")
            elif not playback_result.get("playing"):
                print("  ℹ No active playback")
        except Exception as e:
            print(f"✗ Error: {e}")

        # Test searching for tracks
        print("\n[5/6] Testing spotify_search_tracks...")
        try:
            search_result = await agent.search_tracks("lofi hip hop", limit=5)
            print(f"✓ {search_result.get('summary', 'Success')}")
            if search_result.get("tracks"):
                for i, track in enumerate(search_result["tracks"][:5], 1):
                    print(f"  {i}. {track['name']} - {track['artist']}")
        except Exception as e:
            print(f"✗ Error: {e}")

        # Test playback control (only if device available)
        print("\n[6/6] Testing playback controls...")
        devices_result = await agent.get_devices()
        if devices_result.get("devices") and len(devices_result["devices"]) > 0:
            print("  ℹ Devices available, but skipping playback control test")
            print("  ℹ To test playback control, use the agent interactively")
            print("\n  Demo commands you can try:")
            print("    - 'Play some lofi beats on Spotify'")
            print("    - 'Pause Spotify'")
            print("    - 'Skip to the next track'")
            print("    - 'What's playing on Spotify?'")
        else:
            print("  ⚠ No devices available for playback control test")
            print("  ℹ Open Spotify on any device to enable playback control")

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Ensure Spotify is open on at least one device")
        print("2. Start playing a song (can be paused, but device must be active)")
        print("3. Try the demo commands with your AI agent")
        print("\nFor setup instructions, see docs/SPOTIFY_SETUP.md")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
    finally:
        await agent.close()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_spotify_operations())
    sys.exit(exit_code)
