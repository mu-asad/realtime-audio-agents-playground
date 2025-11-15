"""
Agent Host for Azure Realtime Audio with Google Calendar MCP Integration

This module provides the main agent host that connects to the Google Calendar MCP server
and exposes calendar tools for use by the AI assistant.
"""

import asyncio
import json
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
        # store the async context manager returned by stdio_client so we can exit it later
        self._stdio_cm = None

    async def connect_to_mcp_server(self):
        """Connect to the Google Calendar MCP server."""
        # Get the path to the MCP server directory
        import pathlib
        repo_root = pathlib.Path(__file__).parent.parent.parent
        mcp_server_dir = repo_root / "mcp-server"
        server_script = mcp_server_dir / "server.js"

        if not server_script.exists():
            raise FileNotFoundError(f"MCP server script not found: {server_script}")

        # Define server parameters
        # Note: Environment variables should already be loaded by the .env file
        server_params = StdioServerParameters(
            command="node",
            args=[str(server_script)],
        )

        # Use async context manager properly
        print("Starting MCP server process...")
        # Store the context manager so we can exit it in close()
        self._stdio_cm = stdio_client(server_params)

        # Enter the context manager to get the read/write streams
        try:
            read_stream, write_stream = await self._stdio_cm.__aenter__()
        except Exception as e:
            print(f"Error starting MCP server: {e}")
            raise

        self.read = read_stream
        self.write = write_stream
        print("MCP server process started")

        # Give the server a moment to initialize
        await asyncio.sleep(0.5)

        # Create the MCP client session using the obtained transport
        self.session = ClientSession(self.read, self.write)
        print("Client session created")

        # Enter the session context manager
        try:
            await self.session.__aenter__()
            print("Session context entered")
        except Exception as e:
            print(f"Error entering session context: {e}")
            raise

        # Initialize the session with timeout
        print("Initializing session...")
        try:
            init_result = await asyncio.wait_for(self.session.initialize(), timeout=30.0)
            print(f"Session initialized successfully: {init_result}")
        except asyncio.TimeoutError as e:
            print(f"Timeout error during initialization")
            raise RuntimeError(
                "Timeout while initializing MCP session. "
                "The MCP server may not be responding. Check that:\n"
                "1. Node.js is installed and accessible\n"
                "2. MCP server dependencies are installed (run 'npm install' in mcp-server/)\n"
                "3. Google credentials are valid in .env file"
            ) from e
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

        # List available tools
        print("Listing available tools...")
        try:
            tools_result = await asyncio.wait_for(self.session.list_tools(), timeout=5.0)
            self.available_tools = tools_result.tools
            print(f"Found {len(self.available_tools)} tools")
        except asyncio.TimeoutError:
            raise RuntimeError("Timeout while listing tools from MCP server")

        print("Connected to Google Calendar MCP server")
        print(f"Available tools: {[tool.name for tool in self.available_tools]}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available calendar tools."""
        tools_list: List[Dict[str, Any]] = []
        for tool in self.available_tools:
            # Support both object-like and dict-like tool representations
            if isinstance(tool, dict):
                name = tool.get("name") or tool.get("displayName")
                description = tool.get("description", "")
                input_schema = tool.get("inputSchema") or tool.get("input_schema")
            else:
                name = getattr(tool, "name", None) or getattr(tool, "displayName", None)
                description = getattr(tool, "description", "")
                input_schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None)

            tools_list.append({
                "name": name,
                "description": description,
                "input_schema": input_schema,
            })

        return tools_list

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
        """Close the connection to the MCP server and exit any context managers."""
        # If the session implements __aexit__ (i.e. is an async context manager), exit it.
        if self.session:
            if hasattr(self.session, "__aexit__"):
                try:
                    await self.session.__aexit__(None, None, None)
                except Exception:
                    # ignore errors during session exit
                    pass
            elif hasattr(self.session, "close"):
                try:
                    maybe = self.session.close()
                    if asyncio.iscoroutine(maybe):
                        await maybe
                except Exception:
                    pass

        # Exit the stdio client context manager if we entered it
        if hasattr(self, "_stdio_cm") and self._stdio_cm:
            try:
                await self._stdio_cm.__aexit__(None, None, None)
            except Exception:
                pass


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
