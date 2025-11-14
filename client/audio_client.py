"""
Client placeholder for connecting to the audio server.

This client provides a simple WebSocket client that can:
- Connect to the local WebSocket server
- Send audio data (placeholder - not capturing audio yet)
- Receive responses from the server
- Load configuration from environment variables

Future: Will capture microphone audio and stream to the server.
"""

import asyncio
import os
import logging
from typing import Optional

import websockets
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AudioClientConfig:
    """Configuration loaded from environment variables."""
    
    def __init__(self):
        # Load environment variables from .env.local
        load_dotenv('.env.local')
        
        # Server configuration
        self.host = os.getenv('SERVER_HOST', 'localhost')
        self.port = int(os.getenv('SERVER_PORT', '8765'))
        
    @property
    def server_url(self) -> str:
        """Get the WebSocket server URL."""
        return f"ws://{self.host}:{self.port}"
    
    def __str__(self):
        """String representation."""
        return f"AudioClientConfig(server_url={self.server_url})"


class AudioClient:
    """Simple WebSocket client for audio streaming."""
    
    def __init__(self, config: AudioClientConfig):
        self.config = config
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        
    async def connect(self):
        """Connect to the WebSocket server."""
        logger.info(f"Connecting to {self.config.server_url}")
        self.websocket = await websockets.connect(self.config.server_url)
        self.running = True
        logger.info("Connected to server")
        
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from server")
            
    async def send_text(self, message: str):
        """Send a text message to the server."""
        if not self.websocket:
            logger.error("Not connected to server")
            return
            
        logger.info(f"Sending text: {message}")
        await self.websocket.send(message)
        
    async def send_audio(self, audio_data: bytes):
        """Send audio data to the server."""
        if not self.websocket:
            logger.error("Not connected to server")
            return
            
        logger.debug(f"Sending {len(audio_data)} bytes of audio")
        await self.websocket.send(audio_data)
        
    async def receive_messages(self):
        """Receive messages from the server."""
        if not self.websocket:
            logger.error("Not connected to server")
            return
            
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    logger.info(f"Received binary message: {len(message)} bytes")
                else:
                    logger.info(f"Received text message: {message}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
        except Exception as e:
            logger.error(f"Error receiving messages: {e}", exc_info=True)
            
    async def run_demo(self):
        """Run a simple demo that sends test messages."""
        await self.connect()
        
        try:
            # Start receiving messages in the background
            receive_task = asyncio.create_task(self.receive_messages())
            
            # Send some test messages
            await self.send_text("Hello from client!")
            await asyncio.sleep(1)
            
            # Send dummy audio data (just zeros for now)
            dummy_audio = b'\x00' * 1024
            await self.send_audio(dummy_audio)
            await asyncio.sleep(1)
            
            await self.send_text("Test complete")
            await asyncio.sleep(1)
            
            # Cancel the receive task
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
                
        finally:
            await self.disconnect()


async def main():
    """Main entry point."""
    # Load configuration
    config = AudioClientConfig()
    logger.info(f"Configuration: {config}")
    
    # Create and run client
    client = AudioClient(config)
    await client.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Client stopped by user")
