"""
Agent Host for Azure Realtime Audio with Google Calendar MCP Integration

This module provides the main agent host that connects to the Google Calendar MCP server
and exposes calendar tools for use by the AI assistant.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()


class CalendarAgentHost:
    """
    Agent host that integrates with Google Calendar via MCP.

    This class manages the connection to the Google Calendar MCP server
    and provides a clean interface for calendar operations.
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []

    async def connect_to_mcp_server(self):
        """Connect to the Google Calendar MCP server."""
        # Define server parameters
        server_params = StdioServerParameters(
            command="node",
            args=["mcp-server/server.js"],
            env={
                **os.environ,
                "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
                "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN", ""),
                "GOOGLE_CALENDAR_ID": os.getenv("GOOGLE_CALENDAR_ID", "primary"),
            },
        )

        # Connect to the server
        stdio_transport = await stdio_client(server_params)
        self.read, self.write = stdio_transport
        self.session = ClientSession(self.read, self.write)

        # Initialize the session
        await self.session.initialize()

        # List available tools
        tools_result = await self.session.list_tools()
        self.available_tools = tools_result.tools

        print("Connected to Google Calendar MCP server")
        print(f"Available tools: {[tool.name for tool in self.available_tools]}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available calendar tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in self.available_tools
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a calendar tool with the given arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool

        Returns:
            Result from the tool execution
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server. Call connect_to_mcp_server() first.")

        result = await self.session.call_tool(tool_name, arguments)

        # Parse the result
        if result.content:
            content = result.content[0]
            if hasattr(content, "text"):
                return json.loads(content.text)

        return {"error": "No result returned"}

    async def list_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10,
        query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List calendar events."""
        args = {"maxResults": max_results}
        if time_min:
            args["timeMin"] = time_min
        if time_max:
            args["timeMax"] = time_max
        if query:
            args["query"] = query

        return await self.call_tool("list_events", args)

    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get a specific event by ID."""
        return await self.call_tool("get_event", {"eventId": event_id})

    async def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new calendar event."""
        args = {
            "summary": summary,
            "startTime": start_time,
        }
        if end_time:
            args["endTime"] = end_time
        if description:
            args["description"] = description
        if location:
            args["location"] = location
        if attendees:
            args["attendees"] = attendees

        return await self.call_tool("create_event", args)

    async def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing event."""
        args = {"eventId": event_id}
        if summary:
            args["summary"] = summary
        if start_time:
            args["startTime"] = start_time
        if end_time:
            args["endTime"] = end_time
        if description:
            args["description"] = description
        if location:
            args["location"] = location
        if attendees:
            args["attendees"] = attendees

        return await self.call_tool("update_event", args)

    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete an event."""
        return await self.call_tool("delete_event", {"eventId": event_id})

    async def get_free_busy(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get free/busy information."""
        args = {}
        if time_min:
            args["timeMin"] = time_min
        if time_max:
            args["timeMax"] = time_max

        return await self.call_tool("get_free_busy", args)

    async def close(self):
        """Close the connection to the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)


async def main():
    """Example usage of the Calendar Agent Host."""
    agent = CalendarAgentHost()

    try:
        # Connect to the MCP server
        await agent.connect_to_mcp_server()

        # List available tools
        tools = await agent.list_tools()
        print("\nAvailable Calendar Tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # Example: List upcoming events
        print("\n--- Listing upcoming events ---")
        events_result = await agent.list_events(max_results=5)
        print(json.dumps(events_result, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
