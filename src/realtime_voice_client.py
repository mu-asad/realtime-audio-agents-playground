"""
Realtime Voice Client for OpenAI Realtime API

This module provides a client for streaming audio to OpenAI Realtime API
and receiving audio and text responses.
"""

import asyncio
import base64
import json
import logging
from typing import Any, Callable, Dict, Optional

import pyaudio
import websockets
from colorama import init

# Initialize colorama for cross-platform color support
init()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeVoiceClient:
    """
    Client for OpenAI Realtime API with audio streaming support.

    Handles WebSocket connection, audio input/output, and event processing.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the voice client.

        Args:
            config: Configuration dictionary containing:
                - api_key: OpenAI API key
                - model: Model name (e.g., "gpt-4o-realtime-preview-2024-10-01")
                - sample_rate: Audio sample rate (default: 16000)
                - device_index: Optional audio device index
                - system_prompt: System prompt for the model
                - speech_speed: Speech speed multiplier (default: 1.0, range: 0.25 to 4.0)
        """
        self.api_key = config["api_key"]
        self.model = config.get("model", "gpt-4o-realtime-preview-2024-10-01")
        self.sample_rate = config.get("sample_rate", 16000)
        self.device_index = config.get("device_index")
        self.system_prompt = config.get("system_prompt", "You are a helpful assistant.")
        self.speech_speed = config.get("speech_speed", 1.0)

        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.audio: Optional[pyaudio.PyAudio] = None
        self.input_stream: Optional[Any] = None
        self.output_stream: Optional[Any] = None

        self.running = False
        self.transcript_callback: Optional[Callable[[str, str], None]] = None

        # Audio format settings
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1

        # Playback buffer
        self.playback_queue = asyncio.Queue()

    def set_transcript_callback(self, callback: Callable[[str, str], None]):
        """
        Set a callback for transcript updates.

        Args:
            callback: Function that takes (role, text) as arguments
        """
        self.transcript_callback = callback

    async def connect(self):
        """Establish WebSocket connection to OpenAI Realtime API."""
        # OpenAI Realtime API WebSocket URL
        ws_url = f"wss://api.openai.com/v1/realtime?model={self.model}"

        logger.info(f"Connecting to {ws_url}")

        # Connect with Bearer token authentication
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1",
        }

        try:
            self.ws = await websockets.connect(ws_url, additional_headers=headers)
            logger.info("WebSocket connection established")

            # Send session configuration
            await self._configure_session()

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    async def _configure_session(self):
        """Configure the session with system prompt and settings."""
        config_event = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self.system_prompt,
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500,
                },
                "rate": self.speech_speed,  # Speech speed: 0.25 to 4.0 (1.0 is normal speed)
            },
        }

        await self.ws.send(json.dumps(config_event))
        logger.info("Session configured")

    def _setup_audio(self):
        """Initialize PyAudio and audio streams."""
        self.audio = pyaudio.PyAudio()

        # Input stream (microphone)
        self.input_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size,
            stream_callback=None,  # We'll read manually
        )

        # Output stream (speakers)
        self.output_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.chunk_size,
        )

        logger.info("Audio streams initialized")

    def _cleanup_audio(self):
        """Clean up audio resources."""
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()

        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()

        if self.audio:
            self.audio.terminate()

        logger.info("Audio streams cleaned up")

    async def _send_audio(self):
        """Capture and send audio from microphone."""
        try:
            while self.running:
                if self.input_stream and self.input_stream.is_active():
                    # Read audio data
                    audio_data = self.input_stream.read(
                        self.chunk_size, exception_on_overflow=False
                    )

                    # Encode to base64
                    audio_b64 = base64.b64encode(audio_data).decode("utf-8")

                    # Send to API
                    event = {"type": "input_audio_buffer.append", "audio": audio_b64}

                    await self.ws.send(json.dumps(event))

                # Small delay to prevent busy-waiting
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error sending audio: {e}")

    async def _receive_events(self):
        """Receive and process events from the API."""
        try:
            async for message in self.ws:
                if not self.running:
                    break

                try:
                    event = json.loads(message)
                    await self._handle_event(event)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode message: {message[:100]}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error receiving events: {e}")

    async def _handle_event(self, event: Dict[str, Any]):
        """Handle incoming events from the API."""
        event_type = event.get("type")

        if event_type == "session.created":
            logger.info("Session created")

        elif event_type == "session.updated":
            logger.info("Session updated")

        elif event_type == "conversation.item.input_audio_transcription.completed":
            # User's speech transcription
            transcript = event.get("transcript", "")
            if transcript and self.transcript_callback:
                self.transcript_callback("user", transcript)

        elif event_type == "response.audio_transcript.delta":
            # Assistant's partial text response
            delta = event.get("delta", "")
            if delta:
                # We'll accumulate these and print on 'done'
                pass

        elif event_type == "response.audio_transcript.done":
            # Assistant's complete text response
            transcript = event.get("transcript", "")
            if transcript and self.transcript_callback:
                self.transcript_callback("assistant", transcript)

        elif event_type == "response.audio.delta":
            # Audio response chunk
            audio_b64 = event.get("delta", "")
            if audio_b64:
                audio_data = base64.b64decode(audio_b64)
                await self.playback_queue.put(audio_data)

        elif event_type == "response.audio.done":
            logger.debug("Audio response complete")

        elif event_type == "error":
            error = event.get("error", {})
            logger.error(f"API error: {error}")

    async def _play_audio(self):
        """Play audio from the playback queue."""
        try:
            while self.running:
                try:
                    # Wait for audio data with timeout
                    audio_data = await asyncio.wait_for(self.playback_queue.get(), timeout=0.1)

                    if self.output_stream and self.output_stream.is_active():
                        self.output_stream.write(audio_data)

                except asyncio.TimeoutError:
                    # No audio to play, continue
                    continue
        except Exception as e:
            logger.error(f"Error playing audio: {e}")

    async def start(self):
        """Start the voice client."""
        try:
            # Connect to API
            await self.connect()

            # Setup audio
            self._setup_audio()

            # Start processing
            self.running = True

            logger.info("Voice client started. Speak into your microphone...")

            # Run all tasks concurrently
            await asyncio.gather(
                self._send_audio(),
                self._receive_events(),
                self._play_audio(),
                return_exceptions=True,
            )

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Error in voice client: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the voice client and clean up resources."""
        logger.info("Stopping voice client...")
        self.running = False

        # Clean up audio
        self._cleanup_audio()

        # Close WebSocket
        if self.ws:
            await self.ws.close()

        logger.info("Voice client stopped")
