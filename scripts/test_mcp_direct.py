#!/usr/bin/env python3
"""
Minimal MCP connection test using the MCP SDK directly.
"""

import asyncio
import sys
from pathlib import Path

# Add MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_direct():
    """Test MCP connection directly without the CalendarAgentHost wrapper."""

    # Get server path
    repo_root = Path(__file__).parent.parent
    server_script = repo_root / "google-calendar-mcp-server" / "server.js"

    print(f"Server script: {server_script}")
    print(f"Exists: {server_script.exists()}")

    if not server_script.exists():
        print("❌ Server script not found!")
        return False

    # Create server parameters
    server_params = StdioServerParameters(
        command="node",
        args=[str(server_script)],
    )

    print("\n1. Creating stdio_client...")
    stdio_cm = stdio_client(server_params)

    try:
        print("2. Entering stdio context manager...")
        read_stream, write_stream = await stdio_cm.__aenter__()
        print("✓ Got read/write streams")

        print("\n3. Creating ClientSession...")
        session = ClientSession(read_stream, write_stream)
        print("✓ ClientSession created")

        print("\n4. Entering session context...")
        await session.__aenter__()
        print("✓ Session context entered")

        print("\n5. Initializing session...")
        result = await asyncio.wait_for(session.initialize(), timeout=10.0)
        print(f"✓ Session initialized: {result}")

        print("\n6. Listing tools...")
        tools_result = await session.list_tools()
        print(f"✓ Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}")

        print("\n✅ All steps completed successfully!")

        # Cleanup
        print("\n7. Cleaning up...")
        await session.__aexit__(None, None, None)
        await stdio_cm.__aexit__(None, None, None)
        print("✓ Cleanup complete")

        return True

    except asyncio.TimeoutError as e:
        print(f"\n❌ Timeout during initialization")
        print("The MCP server is not responding to the initialize request.")
        print("\nPossible causes:")
        print("1. MCP server dependencies not installed (run: cd google-calendar-mcp-server && npm install)")
        print("2. Wrong MCP SDK version compatibility")
        print("3. Server crashed on startup (check for stderr output above)")
        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Direct MCP Connection Test")
    print("=" * 60)
    print()

    success = asyncio.run(test_mcp_direct())
    sys.exit(0 if success else 1)

