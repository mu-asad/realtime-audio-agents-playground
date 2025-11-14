"""
WebSocket server stub for audio streaming.

This server provides a simple WebSocket endpoint that can:
- Accept WebSocket connections from clients
- Receive audio data from clients
- Echo responses back to clients (placeholder for Azure Realtime integration)
- Load configuration from environment variables

Future: Will integrate with Azure OpenAI Realtime API for audio processing.
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


class AudioServerConfig:
    """Configuration loaded from environment variables."""
    
    def __init__(self):
        # Load environment variables from .env.local
        load_dotenv('.env.local')
        
        # Server configuration
        self.host = os.getenv('SERVER_HOST', 'localhost')
        self.port = int(os.getenv('SERVER_PORT', '8765'))
        
        # Azure OpenAI configuration (not used yet, but validated)
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        self.azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-01-preview')
        
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        if not self.azure_endpoint:
            logger.warning("AZURE_OPENAI_ENDPOINT not set in .env.local")
        if not self.azure_api_key:
            logger.warning("AZURE_OPENAI_API_KEY not set in .env.local")
        if not self.azure_deployment:
            logger.warning("AZURE_OPENAI_DEPLOYMENT not set in .env.local")
        
        # For now, just warn - we're not actually calling Azure yet
        return True
    
    def __str__(self):
        """String representation (hiding sensitive data)."""
        return (
            f"AudioServerConfig(host={self.host}, port={self.port}, "
            f"azure_endpoint={'***' if self.azure_endpoint else 'NOT_SET'}, "
            f"azure_api_key={'***' if self.azure_api_key else 'NOT_SET'}, "
            f"azure_deployment={self.azure_deployment or 'NOT_SET'})"
        )


class AudioServer:
    """Simple WebSocket server for audio streaming."""
    
    def __init__(self, config: AudioServerConfig):
        self.config = config
        self.active_connections = set()
        
    async def handle_client(self, websocket):
        """Handle a single client connection."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_id}")
        self.active_connections.add(websocket)
        
        try:
            async for message in websocket:
                # Handle incoming messages
                if isinstance(message, bytes):
                    # Binary message (audio data)
                    logger.debug(f"Received {len(message)} bytes of audio data from {client_id}")
                    
                    # TODO: Forward to Azure Realtime API
                    # For now, just echo back a simple response
                    response = {
                        "type": "audio_received",
                        "size": len(message),
                        "status": "stub_mode"
                    }
                    await websocket.send(str(response))
                    
                elif isinstance(message, str):
                    # Text message (control/metadata)
                    logger.info(f"Received text message from {client_id}: {message}")
                    
                    # TODO: Handle control messages
                    response = {
                        "type": "text_received",
                        "echo": message,
                        "status": "stub_mode"
                    }
                    await websocket.send(str(response))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}", exc_info=True)
        finally:
            self.active_connections.discard(websocket)
            logger.info(f"Connection closed for {client_id}. Active connections: {len(self.active_connections)}")
    
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting audio server on {self.config.host}:{self.config.port}")
        logger.info(f"Configuration: {self.config}")
        
        async with websockets.serve(
            self.handle_client,
            self.config.host,
            self.config.port
        ):
            logger.info(f"Server listening on ws://{self.config.host}:{self.config.port}")
            logger.info("Press Ctrl+C to stop the server")
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point."""
    # Load and validate configuration
    config = AudioServerConfig()
    if not config.validate():
        logger.error("Configuration validation failed")
        return
    
    # Create and start server
    server = AudioServer(config)
    await server.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
