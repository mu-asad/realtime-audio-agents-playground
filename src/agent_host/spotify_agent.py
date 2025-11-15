"""
Agent Host for Spotify MCP Integration

This module provides the agent host that connects to the Spotify MCP server
and exposes Spotify playback control tools for use by the AI assistant.
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


class SpotifyAgentHost:
    """
    Agent host that integrates with Spotify via MCP.

    This class manages the connection to the Spotify MCP server
    and provides a clean interface for music playback control.
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        # store the async context manager returned by stdio_client so we can exit it later
        self._stdio_cm = None

    async def connect_to_mcp_server(self):
        """Connect to the Spotify MCP server."""
        # Get the path to the MCP server directory
        import pathlib
        repo_root = pathlib.Path(__file__).parent.parent.parent
        mcp_server_dir = repo_root / "spotify-mcp-server"
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
        print("Starting Spotify MCP server process...")
        # Store the context manager so we can exit it in close()
        self._stdio_cm = stdio_client(server_params)

        # Enter the context manager to get the read/write streams
        try:
            read_stream, write_stream = await self._stdio_cm.__aenter__()
        except Exception as e:
            print(f"Error starting Spotify MCP server: {e}")
            raise

        self.read = read_stream
        self.write = write_stream
        print("Spotify MCP server process started")

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
                "2. MCP server dependencies are installed (run 'npm install' in spotify-mcp-server/)\n"
                "3. Spotify credentials are valid in .env file"
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

        print("Connected to Spotify MCP server")
        print(f"Available tools: {[tool.name for tool in self.available_tools]}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available Spotify tools."""
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
        Call a Spotify tool with the given arguments.

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

    async def get_devices(self) -> Dict[str, Any]:
        """Get list of available Spotify playback devices."""
        return await self.call_tool("spotify_get_devices", {})

    async def transfer_playback(
        self,
        device_id: str,
        play: bool = True,
    ) -> Dict[str, Any]:
        """Transfer playback to a specific device."""
        return await self.call_tool("spotify_transfer_playback", {
            "device_id": device_id,
            "play": play,
        })

    async def play(
        self,
        uri: Optional[str] = None,
        search_query: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Play music by URI or search query."""
        args = {}
        if uri:
            args["uri"] = uri
        if search_query:
            args["search_query"] = search_query
        if device_id:
            args["device_id"] = device_id

        return await self.call_tool("spotify_play", args)

    async def pause(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Pause current playback."""
        args = {}
        if device_id:
            args["device_id"] = device_id
        return await self.call_tool("spotify_pause", args)

    async def resume(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Resume playback."""
        args = {}
        if device_id:
            args["device_id"] = device_id
        return await self.call_tool("spotify_resume", args)

    async def next_track(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Skip to next track."""
        args = {}
        if device_id:
            args["device_id"] = device_id
        return await self.call_tool("spotify_next_track", args)

    async def previous_track(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Go to previous track."""
        args = {}
        if device_id:
            args["device_id"] = device_id
        return await self.call_tool("spotify_previous_track", args)

    async def search_tracks(
        self,
        query: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Search for tracks on Spotify."""
        return await self.call_tool("spotify_search_tracks", {
            "query": query,
            "limit": limit,
        })

    async def get_current_playback(self) -> Dict[str, Any]:
        """Get current playback state."""
        return await self.call_tool("spotify_get_current_playback", {})

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
    """Example usage of the Spotify Agent Host."""
    agent = SpotifyAgentHost()

    try:
        # Connect to the MCP server
        await agent.connect_to_mcp_server()

        # List available tools
        tools = await agent.list_tools()
        print("\nAvailable Spotify Tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # Example: Get available devices
        print("\n--- Getting available devices ---")
        devices_result = await agent.get_devices()
        print(json.dumps(devices_result, indent=2))

        # Example: Get current playback
        print("\n--- Getting current playback ---")
        playback_result = await agent.get_current_playback()
        print(json.dumps(playback_result, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
