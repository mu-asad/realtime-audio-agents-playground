#!/usr/bin/env node

/**
 * Spotify MCP Server
 * 
 * Provides MCP tools for controlling Spotify playback via the Spotify Web API.
 * Supports: device management, playback control, search, and track navigation.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import SpotifyWebApi from "spotify-web-api-node";
import dotenv from "dotenv";
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables - try multiple locations
dotenv.config({ path: join(__dirname, "../.env") });
dotenv.config({ path: join(process.cwd(), ".env") });

console.error(`[DEBUG] Working directory: ${process.cwd()}`);
console.error(`[DEBUG] Server directory: ${__dirname}`);
console.error(`[DEBUG] SPOTIFY_CLIENT_ID set: ${!!process.env.SPOTIFY_CLIENT_ID}`);
console.error(`[DEBUG] SPOTIFY_REFRESH_TOKEN set: ${!!process.env.SPOTIFY_REFRESH_TOKEN}`);

// Initialize Spotify API client
const spotifyApi = new SpotifyWebApi({
  clientId: process.env.SPOTIFY_CLIENT_ID,
  clientSecret: process.env.SPOTIFY_CLIENT_SECRET,
  redirectUri: process.env.SPOTIFY_REDIRECT_URI || "http://localhost:8888/callback",
});

// Set credentials from refresh token
if (process.env.SPOTIFY_REFRESH_TOKEN) {
  spotifyApi.setRefreshToken(process.env.SPOTIFY_REFRESH_TOKEN);
  
  // Get initial access token
  try {
    const data = await spotifyApi.refreshAccessToken();
    spotifyApi.setAccessToken(data.body.access_token);
    console.error("[DEBUG] Successfully obtained access token");
  } catch (error) {
    console.error("[ERROR] Failed to refresh access token:", error.message);
  }
}

// Auto-refresh token before it expires
setInterval(async () => {
  try {
    const data = await spotifyApi.refreshAccessToken();
    spotifyApi.setAccessToken(data.body.access_token);
    console.error("[DEBUG] Access token refreshed");
  } catch (error) {
    console.error("[ERROR] Failed to refresh access token:", error.message);
  }
}, 50 * 60 * 1000); // Refresh every 50 minutes (tokens expire in 60 minutes)

/**
 * Get available playback devices
 */
async function getDevices() {
  try {
    const data = await spotifyApi.getMyDevices();
    const devices = data.body.devices.map(device => ({
      id: device.id,
      name: device.name,
      type: device.type,
      is_active: device.is_active,
      volume_percent: device.volume_percent,
    }));
    
    return {
      devices,
      summary: `Found ${devices.length} device(s)`,
    };
  } catch (error) {
    throw new Error(`Failed to get devices: ${error.message}`);
  }
}

/**
 * Transfer playback to a specific device
 */
async function transferPlayback(args) {
  const { device_id, play = true } = args;
  
  if (!device_id) {
    throw new Error("device_id is required");
  }
  
  try {
    await spotifyApi.transferMyPlayback([device_id], { play });
    return {
      success: true,
      summary: `Playback transferred to device ${device_id}`,
    };
  } catch (error) {
    throw new Error(`Failed to transfer playback: ${error.message}`);
  }
}

/**
 * Play music by URI or search query
 */
async function play(args) {
  const { uri, search_query, device_id } = args;
  
  try {
    let uris = [];
    
    // If search query provided, search for tracks
    if (search_query && !uri) {
      const searchResult = await spotifyApi.searchTracks(search_query, { limit: 1 });
      if (searchResult.body.tracks.items.length > 0) {
        uris = [searchResult.body.tracks.items[0].uri];
      } else {
        throw new Error(`No tracks found for query: ${search_query}`);
      }
    } else if (uri) {
      uris = [uri];
    }
    
    const options = {};
    if (device_id) {
      options.device_id = device_id;
    }
    
    if (uris.length > 0) {
      await spotifyApi.play({ ...options, uris });
      return {
        success: true,
        summary: `Now playing: ${search_query || uri}`,
      };
    } else {
      // Resume current playback
      await spotifyApi.play(options);
      return {
        success: true,
        summary: "Playback resumed",
      };
    }
  } catch (error) {
    throw new Error(`Failed to play: ${error.message}`);
  }
}

/**
 * Pause current playback
 */
async function pause(args) {
  const { device_id } = args || {};
  
  try {
    const options = device_id ? { device_id } : {};
    await spotifyApi.pause(options);
    return {
      success: true,
      summary: "Playback paused",
    };
  } catch (error) {
    throw new Error(`Failed to pause: ${error.message}`);
  }
}

/**
 * Resume current playback
 */
async function resume(args) {
  const { device_id } = args || {};
  
  try {
    const options = device_id ? { device_id } : {};
    await spotifyApi.play(options);
    return {
      success: true,
      summary: "Playback resumed",
    };
  } catch (error) {
    throw new Error(`Failed to resume: ${error.message}`);
  }
}

/**
 * Skip to next track
 */
async function nextTrack(args) {
  const { device_id } = args || {};
  
  try {
    const options = device_id ? { device_id } : {};
    await spotifyApi.skipToNext(options);
    return {
      success: true,
      summary: "Skipped to next track",
    };
  } catch (error) {
    throw new Error(`Failed to skip to next track: ${error.message}`);
  }
}

/**
 * Go to previous track
 */
async function previousTrack(args) {
  const { device_id } = args || {};
  
  try {
    const options = device_id ? { device_id } : {};
    await spotifyApi.skipToPrevious(options);
    return {
      success: true,
      summary: "Skipped to previous track",
    };
  } catch (error) {
    throw new Error(`Failed to skip to previous track: ${error.message}`);
  }
}

/**
 * Search for tracks
 */
async function searchTracks(args) {
  const { query, limit = 10 } = args;
  
  if (!query) {
    throw new Error("query is required");
  }
  
  try {
    const data = await spotifyApi.searchTracks(query, { limit });
    const tracks = data.body.tracks.items.map(track => ({
      name: track.name,
      artist: track.artists.map(a => a.name).join(", "),
      album: track.album.name,
      uri: track.uri,
      duration_ms: track.duration_ms,
    }));
    
    return {
      tracks,
      summary: `Found ${tracks.length} track(s) for query: ${query}`,
    };
  } catch (error) {
    throw new Error(`Failed to search tracks: ${error.message}`);
  }
}

/**
 * Get current playback state
 */
async function getCurrentPlayback() {
  try {
    const data = await spotifyApi.getMyCurrentPlaybackState();
    
    if (!data.body || !data.body.item) {
      return {
        playing: false,
        summary: "No active playback",
      };
    }
    
    return {
      playing: data.body.is_playing,
      track: {
        name: data.body.item.name,
        artist: data.body.item.artists.map(a => a.name).join(", "),
        album: data.body.item.album.name,
        uri: data.body.item.uri,
      },
      device: {
        name: data.body.device.name,
        type: data.body.device.type,
      },
      progress_ms: data.body.progress_ms,
      duration_ms: data.body.item.duration_ms,
      summary: `Currently playing: ${data.body.item.name} by ${data.body.item.artists.map(a => a.name).join(", ")}`,
    };
  } catch (error) {
    throw new Error(`Failed to get current playback: ${error.message}`);
  }
}

// Tool definitions
const TOOLS = [
  {
    name: "spotify_get_devices",
    description: "Get list of available Spotify playback devices.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "spotify_transfer_playback",
    description: "Transfer playback to a specific device.",
    inputSchema: {
      type: "object",
      properties: {
        device_id: {
          type: "string",
          description: "The ID of the device to transfer playback to.",
        },
        play: {
          type: "boolean",
          description: "Whether to start playing on the new device. Default is true.",
        },
      },
      required: ["device_id"],
    },
  },
  {
    name: "spotify_play",
    description: "Play music by URI or search query. If neither is provided, resumes current playback.",
    inputSchema: {
      type: "object",
      properties: {
        uri: {
          type: "string",
          description: "Spotify URI to play (e.g., spotify:track:xxx).",
        },
        search_query: {
          type: "string",
          description: "Search query to find and play a track.",
        },
        device_id: {
          type: "string",
          description: "Device ID to play on. Optional.",
        },
      },
    },
  },
  {
    name: "spotify_pause",
    description: "Pause current Spotify playback.",
    inputSchema: {
      type: "object",
      properties: {
        device_id: {
          type: "string",
          description: "Device ID to pause. Optional.",
        },
      },
    },
  },
  {
    name: "spotify_resume",
    description: "Resume Spotify playback.",
    inputSchema: {
      type: "object",
      properties: {
        device_id: {
          type: "string",
          description: "Device ID to resume playback on. Optional.",
        },
      },
    },
  },
  {
    name: "spotify_next_track",
    description: "Skip to the next track in the queue.",
    inputSchema: {
      type: "object",
      properties: {
        device_id: {
          type: "string",
          description: "Device ID to skip on. Optional.",
        },
      },
    },
  },
  {
    name: "spotify_previous_track",
    description: "Go back to the previous track.",
    inputSchema: {
      type: "object",
      properties: {
        device_id: {
          type: "string",
          description: "Device ID to go back on. Optional.",
        },
      },
    },
  },
  {
    name: "spotify_search_tracks",
    description: "Search for tracks on Spotify.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query for tracks.",
        },
        limit: {
          type: "number",
          description: "Maximum number of results. Default is 10.",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "spotify_get_current_playback",
    description: "Get information about the current playback state.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
];

// Map of tool names to handler functions
const TOOL_HANDLERS = {
  spotify_get_devices: getDevices,
  spotify_transfer_playback: transferPlayback,
  spotify_play: play,
  spotify_pause: pause,
  spotify_resume: resume,
  spotify_next_track: nextTrack,
  spotify_previous_track: previousTrack,
  spotify_search_tracks: searchTracks,
  spotify_get_current_playback: getCurrentPlayback,
};

/**
 * Main server initialization
 */
async function main() {
  const server = new Server(
    {
      name: "spotify-mcp-server",
      version: "1.0.0",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Handle list tools request
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    console.error("[DEBUG] Received list_tools request");
    return {
      tools: TOOLS,
    };
  });

  // Handle tool execution
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    console.error(`[DEBUG] Received call_tool request: ${request.params.name}`);
    const { name, arguments: args } = request.params;

    try {
      const handler = TOOL_HANDLERS[name];
      if (!handler) {
        throw new Error(`Unknown tool: ${name}`);
      }

      const result = await handler(args || {});
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              error: error.message,
              details: error.stack,
            }),
          },
        ],
        isError: true,
      };
    }
  });

  // Start server with stdio transport
  console.error("[DEBUG] Creating StdioServerTransport...");
  const transport = new StdioServerTransport();
  console.error("[DEBUG] Connecting server to transport...");
  await server.connect(transport);

  console.error("Spotify MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
