#!/usr/bin/env node

/**
 * Helper script to obtain Google OAuth refresh token
 * 
 * Usage:
 *   1. Set your CLIENT_ID and CLIENT_SECRET in .env
 *   2. Run: node scripts/get-refresh-token.js
 *   3. Follow the authorization URL
 *   4. Paste the authorization code when prompted
 *   5. Copy the refresh token to your .env file
 */

import { google } from 'googleapis';
import readline from 'readline';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Load environment variables
const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, '..', '.env') });

const CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error('Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env file');
  console.error('\nPlease:');
  console.error('1. Copy .env.example to .env');
  console.error('2. Fill in your Google OAuth credentials');
  console.error('3. Run this script again');
  process.exit(1);
}

// Create OAuth2 client
const oauth2Client = new google.auth.OAuth2(
  CLIENT_ID,
  CLIENT_SECRET,
  'urn:ietf:wg:oauth:2.0:oob'
);

// Define the scopes we need
const scopes = [
  'https://www.googleapis.com/auth/calendar',
  'https://www.googleapis.com/auth/calendar.events',
];

// Generate the authorization URL
const authUrl = oauth2Client.generateAuthUrl({
  access_type: 'offline',
  scope: scopes,
  prompt: 'consent', // Force to show consent screen to get refresh token
});

console.log('='.repeat(80));
console.log('Google Calendar OAuth Setup');
console.log('='.repeat(80));
console.log('\nStep 1: Authorize this application');
console.log('\nVisit this URL in your browser:\n');
console.log(authUrl);
console.log('\n' + '='.repeat(80));

// Create readline interface to get the authorization code
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question('\nStep 2: Enter the authorization code from the browser: ', async (code) => {
  try {
    console.log('\nExchanging authorization code for tokens...');
    
    const { tokens } = await oauth2Client.getToken(code);
    
    console.log('\n' + '='.repeat(80));
    console.log('SUCCESS! Your refresh token is:');
    console.log('='.repeat(80));
    console.log('\n' + tokens.refresh_token + '\n');
    console.log('='.repeat(80));
    console.log('\nNext steps:');
    console.log('1. Copy the refresh token above');
    console.log('2. Add it to your .env file as GOOGLE_REFRESH_TOKEN');
    console.log('3. Save the .env file');
    console.log('4. You can now use the calendar integration!');
    console.log('\nExample .env entry:');
    console.log(`GOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`);
    console.log('\n' + '='.repeat(80));
    
    // Also show other tokens for reference
    if (tokens.access_token) {
      console.log('\n[Optional] Access Token (expires in 1 hour):');
      console.log(tokens.access_token);
    }
    if (tokens.expiry_date) {
      console.log(`\nAccess Token expires: ${new Date(tokens.expiry_date).toISOString()}`);
    }
    
  } catch (error) {
    console.error('\nError getting tokens:', error.message);
    console.error('\nPlease make sure:');
    console.error('- The authorization code is correct');
    console.error('- Your CLIENT_ID and CLIENT_SECRET are correct');
    console.error('- You copied the entire code without extra spaces');
  } finally {
    rl.close();
  }
});
