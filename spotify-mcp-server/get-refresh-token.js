#!/usr/bin/env node

/**
 * Spotify Refresh Token Generator
 * 
 * This script helps you obtain a refresh token for Spotify API access.
 * It will open your browser to authorize the app and then display the refresh token.
 */

import SpotifyWebApi from "spotify-web-api-node";
import dotenv from "dotenv";
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import http from 'http';
import { exec } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
dotenv.config({ path: join(__dirname, "../.env") });

// Check required environment variables
if (!process.env.SPOTIFY_CLIENT_ID || !process.env.SPOTIFY_CLIENT_SECRET) {
  console.error("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file");
  process.exit(1);
}

const redirectUri = process.env.SPOTIFY_REDIRECT_URI || "http://localhost:8888/callback";
const port = 8888;

// Initialize Spotify API
const spotifyApi = new SpotifyWebApi({
  clientId: process.env.SPOTIFY_CLIENT_ID,
  clientSecret: process.env.SPOTIFY_CLIENT_SECRET,
  redirectUri: redirectUri,
});

// Required scopes
const scopes = [
  "user-read-playback-state",
  "user-modify-playback-state",
  "user-read-currently-playing",
  "streaming",
];

console.log("\n=== Spotify Refresh Token Generator ===\n");
console.log("This script will help you obtain a refresh token for Spotify API access.\n");

// Create authorization URL
const authorizeURL = spotifyApi.createAuthorizeURL(scopes, "state");

console.log("Step 1: Opening browser for authorization...");
console.log(`If the browser doesn't open, visit this URL:\n${authorizeURL}\n`);

// Open browser
const openCommand = process.platform === 'win32' ? 'start' : 
                    process.platform === 'darwin' ? 'open' : 'xdg-open';
exec(`${openCommand} "${authorizeURL}"`);

// Create HTTP server to handle callback
const server = http.createServer(async (req, res) => {
  // Parse URL
  const url = new URL(req.url, `http://localhost:${port}`);
  
  if (url.pathname === "/callback") {
    const code = url.searchParams.get("code");
    const error = url.searchParams.get("error");

    if (error) {
      console.error(`\nError: ${error}`);
      res.writeHead(400, { "Content-Type": "text/html" });
      res.end("<h1>Authorization Failed</h1><p>You can close this window.</p>");
      server.close();
      process.exit(1);
    }

    if (!code) {
      console.error("\nError: No authorization code received");
      res.writeHead(400, { "Content-Type": "text/html" });
      res.end("<h1>Authorization Failed</h1><p>No code received. You can close this window.</p>");
      server.close();
      process.exit(1);
    }

    try {
      console.log("\nStep 2: Exchanging authorization code for tokens...");
      
      // Exchange code for tokens
      const data = await spotifyApi.authorizationCodeGrant(code);
      
      const accessToken = data.body.access_token;
      const refreshToken = data.body.refresh_token;
      
      console.log("\n✓ Authorization successful!\n");
      console.log("=".repeat(60));
      console.log("Add this to your .env file:");
      console.log("=".repeat(60));
      console.log(`SPOTIFY_REFRESH_TOKEN=${refreshToken}`);
      console.log("=".repeat(60));
      console.log("\nThis token will not expire, but it can be revoked from your");
      console.log("Spotify account settings if needed.\n");
      
      // Send success response
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(`
        <html>
          <head>
            <title>Authorization Successful</title>
            <style>
              body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
              }
              .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 500px;
              }
              h1 { color: #1DB954; margin-top: 0; }
              .success-icon { font-size: 48px; margin-bottom: 20px; }
              .token { 
                background: #f5f5f5; 
                padding: 15px; 
                border-radius: 5px; 
                word-break: break-all; 
                font-family: monospace;
                font-size: 12px;
                margin: 20px 0;
              }
              .instructions { 
                text-align: left; 
                margin-top: 20px; 
                color: #666;
              }
            </style>
          </head>
          <body>
            <div class="container">
              <div class="success-icon">✓</div>
              <h1>Authorization Successful!</h1>
              <p>Your refresh token has been generated.</p>
              <div class="token">${refreshToken}</div>
              <div class="instructions">
                <strong>Next steps:</strong>
                <ol>
                  <li>Copy the token above</li>
                  <li>Add it to your <code>.env</code> file as <code>SPOTIFY_REFRESH_TOKEN</code></li>
                  <li>You can close this window</li>
                </ol>
              </div>
            </div>
          </body>
        </html>
      `);
      
      // Close server after a delay
      setTimeout(() => {
        server.close();
      }, 1000);
      
    } catch (error) {
      console.error(`\nError getting tokens: ${error.message}`);
      res.writeHead(500, { "Content-Type": "text/html" });
      res.end("<h1>Error</h1><p>Failed to get tokens. Check console for details.</p>");
      server.close();
      process.exit(1);
    }
  } else {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not Found");
  }
});

// Start server
server.listen(port, () => {
  console.log(`Step 2: Waiting for authorization callback on port ${port}...\n`);
});

// Handle server errors
server.on("error", (error) => {
  if (error.code === "EADDRINUSE") {
    console.error(`\nError: Port ${port} is already in use.`);
    console.error("Please close any other applications using this port and try again.\n");
  } else {
    console.error(`\nServer error: ${error.message}\n`);
  }
  process.exit(1);
});
