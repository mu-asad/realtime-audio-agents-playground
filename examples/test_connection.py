#!/usr/bin/env python3
"""
Minimal test to verify MCP server connection.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_host import CalendarAgentHost


async def test_connection():
    """Test basic connection to MCP server."""
    agent = CalendarAgentHost()

    try:
        print("Testing MCP server connection...")
        await agent.connect_to_mcp_server()
        print("✓ Connection successful!")

        tools = await agent.list_tools()
        print(f"✓ Found {len(tools)} tools")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await agent.close()


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

