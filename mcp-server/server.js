#!/usr/bin/env node

/**
 * Google Calendar MCP Server
 * 
 * Provides MCP tools for interacting with Google Calendar API.
 * Supports: list_events, get_event, create_event, update_event, delete_event, get_free_busy
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import dotenv from "dotenv";

// Load environment variables
dotenv.config({ path: "../.env" });

// Initialize OAuth2 client
const oauth2Client = new google.auth.OAuth2(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  "urn:ietf:wg:oauth:2.0:oob"
);

// Set credentials from refresh token
if (process.env.GOOGLE_REFRESH_TOKEN) {
  oauth2Client.setCredentials({
    refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
  });
}

// Initialize Calendar API
const calendar = google.calendar({ version: "v3", auth: oauth2Client });

// Default calendar ID
const DEFAULT_CALENDAR_ID = process.env.GOOGLE_CALENDAR_ID || "primary";

/**
 * Parse ISO date string or return default
 */
function parseDate(dateStr, defaultValue) {
  if (!dateStr) return defaultValue;
  try {
    const date = new Date(dateStr);
    return date.toISOString();
  } catch (error) {
    return defaultValue;
  }
}

/**
 * List calendar events
 */
async function listEvents(args) {
  const {
    timeMin = new Date().toISOString(),
    timeMax,
    maxResults = 10,
    query,
    calendarId = DEFAULT_CALENDAR_ID,
  } = args;

  const params = {
    calendarId,
    timeMin,
    maxResults: parseInt(maxResults),
    singleEvents: true,
    orderBy: "startTime",
  };

  if (timeMax) params.timeMax = timeMax;
  if (query) params.q = query;

  const response = await calendar.events.list(params);
  return {
    events: response.data.items || [],
    summary: `Found ${response.data.items?.length || 0} events`,
  };
}

/**
 * Get a specific event
 */
async function getEvent(args) {
  const { eventId, calendarId = DEFAULT_CALENDAR_ID } = args;

  if (!eventId) {
    throw new Error("eventId is required");
  }

  const response = await calendar.events.get({
    calendarId,
    eventId,
  });

  return {
    event: response.data,
    summary: `Retrieved event: ${response.data.summary}`,
  };
}

/**
 * Create a new calendar event
 */
async function createEvent(args) {
  const {
    summary,
    description,
    startTime,
    endTime,
    attendees,
    location,
    calendarId = DEFAULT_CALENDAR_ID,
  } = args;

  if (!summary) {
    throw new Error("summary (title) is required");
  }
  if (!startTime) {
    throw new Error("startTime is required");
  }

  const event = {
    summary,
    description,
    location,
    start: {
      dateTime: startTime,
      timeZone: "UTC",
    },
    end: {
      dateTime: endTime || new Date(new Date(startTime).getTime() + 60 * 60 * 1000).toISOString(),
      timeZone: "UTC",
    },
  };

  // Add attendees if provided
  if (attendees && Array.isArray(attendees)) {
    event.attendees = attendees.map((email) => ({ email }));
  } else if (attendees && typeof attendees === "string") {
    event.attendees = attendees.split(",").map((email) => ({ email: email.trim() }));
  }

  const response = await calendar.events.insert({
    calendarId,
    requestBody: event,
    sendUpdates: "all",
  });

  return {
    event: response.data,
    summary: `Created event: ${response.data.summary} (${response.data.id})`,
  };
}

/**
 * Update an existing event
 */
async function updateEvent(args) {
  const {
    eventId,
    summary,
    description,
    startTime,
    endTime,
    attendees,
    location,
    calendarId = DEFAULT_CALENDAR_ID,
  } = args;

  if (!eventId) {
    throw new Error("eventId is required");
  }

  // First, get the existing event
  const existingEvent = await calendar.events.get({
    calendarId,
    eventId,
  });

  // Update only provided fields
  const updatedEvent = { ...existingEvent.data };
  if (summary) updatedEvent.summary = summary;
  if (description !== undefined) updatedEvent.description = description;
  if (location !== undefined) updatedEvent.location = location;
  if (startTime) {
    updatedEvent.start = {
      dateTime: startTime,
      timeZone: updatedEvent.start?.timeZone || "UTC",
    };
  }
  if (endTime) {
    updatedEvent.end = {
      dateTime: endTime,
      timeZone: updatedEvent.end?.timeZone || "UTC",
    };
  }
  if (attendees) {
    if (Array.isArray(attendees)) {
      updatedEvent.attendees = attendees.map((email) => ({ email }));
    } else if (typeof attendees === "string") {
      updatedEvent.attendees = attendees.split(",").map((email) => ({ email: email.trim() }));
    }
  }

  const response = await calendar.events.update({
    calendarId,
    eventId,
    requestBody: updatedEvent,
    sendUpdates: "all",
  });

  return {
    event: response.data,
    summary: `Updated event: ${response.data.summary}`,
  };
}

/**
 * Delete an event
 */
async function deleteEvent(args) {
  const { eventId, calendarId = DEFAULT_CALENDAR_ID } = args;

  if (!eventId) {
    throw new Error("eventId is required");
  }

  await calendar.events.delete({
    calendarId,
    eventId,
    sendUpdates: "all",
  });

  return {
    success: true,
    summary: `Deleted event: ${eventId}`,
  };
}

/**
 * Get free/busy information
 */
async function getFreeBusy(args) {
  const {
    timeMin = new Date().toISOString(),
    timeMax = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    calendarId = DEFAULT_CALENDAR_ID,
  } = args;

  const response = await calendar.freebusy.query({
    requestBody: {
      timeMin,
      timeMax,
      items: [{ id: calendarId }],
    },
  });

  return {
    freeBusy: response.data.calendars?.[calendarId] || {},
    summary: `Retrieved free/busy for ${calendarId}`,
  };
}

// Tool definitions
const TOOLS = [
  {
    name: "list_events",
    description: "List calendar events within a time range. Can filter by search query.",
    inputSchema: {
      type: "object",
      properties: {
        timeMin: {
          type: "string",
          description: "Start time (ISO 8601 format). Defaults to now.",
        },
        timeMax: {
          type: "string",
          description: "End time (ISO 8601 format). Optional.",
        },
        maxResults: {
          type: "number",
          description: "Maximum number of events to return. Default 10.",
        },
        query: {
          type: "string",
          description: "Free text search query to filter events.",
        },
        calendarId: {
          type: "string",
          description: "Calendar ID. Defaults to 'primary'.",
        },
      },
    },
  },
  {
    name: "get_event",
    description: "Get details of a specific calendar event by ID.",
    inputSchema: {
      type: "object",
      properties: {
        eventId: {
          type: "string",
          description: "The event ID to retrieve.",
        },
        calendarId: {
          type: "string",
          description: "Calendar ID. Defaults to 'primary'.",
        },
      },
      required: ["eventId"],
    },
  },
  {
    name: "create_event",
    description: "Create a new calendar event with title, time, and optional attendees.",
    inputSchema: {
      type: "object",
      properties: {
        summary: {
          type: "string",
          description: "Event title/summary.",
        },
        description: {
          type: "string",
          description: "Event description. Optional.",
        },
        startTime: {
          type: "string",
          description: "Event start time (ISO 8601 format).",
        },
        endTime: {
          type: "string",
          description: "Event end time (ISO 8601 format). Defaults to 1 hour after start.",
        },
        location: {
          type: "string",
          description: "Event location. Optional.",
        },
        attendees: {
          type: ["string", "array"],
          description: "Attendee email addresses. Can be comma-separated string or array.",
        },
        calendarId: {
          type: "string",
          description: "Calendar ID. Defaults to 'primary'.",
        },
      },
      required: ["summary", "startTime"],
    },
  },
  {
    name: "update_event",
    description: "Update an existing calendar event. Only provided fields will be updated.",
    inputSchema: {
      type: "object",
      properties: {
        eventId: {
          type: "string",
          description: "The event ID to update.",
        },
        summary: {
          type: "string",
          description: "New event title/summary. Optional.",
        },
        description: {
          type: "string",
          description: "New event description. Optional.",
        },
        startTime: {
          type: "string",
          description: "New start time (ISO 8601 format). Optional.",
        },
        endTime: {
          type: "string",
          description: "New end time (ISO 8601 format). Optional.",
        },
        location: {
          type: "string",
          description: "New location. Optional.",
        },
        attendees: {
          type: ["string", "array"],
          description: "New attendee list. Optional.",
        },
        calendarId: {
          type: "string",
          description: "Calendar ID. Defaults to 'primary'.",
        },
      },
      required: ["eventId"],
    },
  },
  {
    name: "delete_event",
    description: "Delete/cancel a calendar event.",
    inputSchema: {
      type: "object",
      properties: {
        eventId: {
          type: "string",
          description: "The event ID to delete.",
        },
        calendarId: {
          type: "string",
          description: "Calendar ID. Defaults to 'primary'.",
        },
      },
      required: ["eventId"],
    },
  },
  {
    name: "get_free_busy",
    description: "Get free/busy information for a calendar within a time range.",
    inputSchema: {
      type: "object",
      properties: {
        timeMin: {
          type: "string",
          description: "Start time (ISO 8601 format). Defaults to now.",
        },
        timeMax: {
          type: "string",
          description: "End time (ISO 8601 format). Defaults to 7 days from now.",
        },
        calendarId: {
          type: "string",
          description: "Calendar ID. Defaults to 'primary'.",
        },
      },
    },
  },
];

// Map of tool names to handler functions
const TOOL_HANDLERS = {
  list_events: listEvents,
  get_event: getEvent,
  create_event: createEvent,
  update_event: updateEvent,
  delete_event: deleteEvent,
  get_free_busy: getFreeBusy,
};

/**
 * Main server initialization
 */
async function main() {
  const server = new Server(
    {
      name: "google-calendar-mcp-server",
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
    return {
      tools: TOOLS,
    };
  });

  // Handle tool execution
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
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
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("Google Calendar MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
