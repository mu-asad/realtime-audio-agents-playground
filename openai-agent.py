"""
OpenAI Realtime Agent with Calendar and Spotify Integration

This script integrates Google Calendar and Spotify MCP servers with the OpenAI Realtime Agent,
allowing voice control of calendar events and music playback.
"""

import asyncio
import os

import pyaudio
from agents.realtime import RealtimeAgent, RealtimeRunner
from colorama import Fore, Style, init
from dotenv import load_dotenv

from src.agent_host import CalendarAgentHost
from src.agent_host.spotify_agent import SpotifyAgentHost

# Initialize colorama
init()
SAMPLE_RATE = 24000  # GPT realtime PCM16 default
CHANNELS = 1
CHUNK = 1024
RATE = 16000

# Global audio output stream
p = pyaudio.PyAudio()
output_stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    output=True,
)

# Global MCP agent hosts
calendar_agent: CalendarAgentHost = None
spotify_agent: SpotifyAgentHost = None


async def mic_stream(session):
    """Stream microphone input to the realtime session."""
    p_mic = pyaudio.PyAudio()
    stream = p_mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            await session.send_audio(data)
            await asyncio.sleep(0)  # yield to event loop
    finally:
        stream.stop_stream()
        stream.close()
        p_mic.terminate()


def _truncate_str(s: str, max_length: int) -> str:
    """Truncate string to max length."""
    return s if len(s) <= max_length else s[:max_length] + "..."


def print_transcript(role: str, text: str):
    """Print transcript with color coding."""
    if role == "user":
        print(f"{Fore.GREEN}[Asad]: {text}{Style.RESET_ALL}")
    elif role == "assistant":
        print(f"{Fore.BLUE}[ASSISTANT]: {text}{Style.RESET_ALL}")
    else:
        print(f"[{role.upper()}]: {text}")


async def initialize_mcp_agents():
    """Initialize and connect to MCP agents."""
    global calendar_agent, spotify_agent

    print(f"{Fore.CYAN}Initializing MCP agents...{Style.RESET_ALL}")

    # Initialize Calendar Agent
    try:
        print(f"{Fore.YELLOW}Connecting to Google Calendar...{Style.RESET_ALL}")
        calendar_agent = CalendarAgentHost()
        await calendar_agent.connect_to_mcp_server()
        print(f"{Fore.GREEN}✓ Calendar agent connected{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to connect Calendar agent: {e}{Style.RESET_ALL}")
        calendar_agent = None

    # Initialize Spotify Agent
    try:
        print(f"{Fore.YELLOW}Connecting to Spotify...{Style.RESET_ALL}")
        spotify_agent = SpotifyAgentHost()
        await spotify_agent.connect_to_mcp_server()
        print(f"{Fore.GREEN}✓ Spotify agent connected{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Failed to connect Spotify agent: {e}{Style.RESET_ALL}")
        spotify_agent = None

    print(f"{Fore.CYAN}MCP agents initialization complete{Style.RESET_ALL}\n")


async def main():
    load_dotenv()

    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}OpenAI Realtime Agent with Calendar & Spotify Integration{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    # Load agent instructions from prompt file
    prompt_file = "prompts/DHA-ONE.md"
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            agent_instructions = f.read()
        print(f"{Fore.GREEN}✓ Loaded instructions from {prompt_file}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}✗ Could not find {prompt_file}, using default instructions{Style.RESET_ALL}")
        agent_instructions = (
            "You are a helpful voice assistant with access to calendar and music controls.\n"
            "\n"
            "You can help users with:\n"
            "- Managing their calendar (viewing events, creating new events, "
            "updating events, deleting events)\n"
            "- Controlling Spotify music playback (play, pause, skip, search for songs, "
            "check what's playing)\n"
            "\n"
            "When users ask about their schedule or to create events, use the calendar tools.\n"
            "When users ask to play music or control playback, use the Spotify tools.\n"
            "\n"
            "Keep responses brief and conversational. Always confirm actions before executing them."
        )

    # Initialize MCP agents
    await initialize_mcp_agents()

    # Collect all tools from both agents
    tools = []
    if calendar_agent:
        tools.extend(calendar_agent.get_all_tools())
        calendar_tools_count = len(calendar_agent.get_all_tools())
        print(f"{Fore.GREEN}Added {calendar_tools_count} calendar tools{Style.RESET_ALL}")
    if spotify_agent:
        tools.extend(spotify_agent.get_all_tools())
        spotify_tools_count = len(spotify_agent.get_all_tools())
        print(f"{Fore.GREEN}Added {spotify_tools_count} Spotify tools{Style.RESET_ALL}")

    print(f"{Fore.CYAN}Total tools available: {len(tools)}{Style.RESET_ALL}\n")

    # Runtime configuration from environment
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-realtime-preview-2024-10-01")
    voice = os.getenv("VOICE_CLIENT_VOICE", "ash")
    try:
        speed = float(os.getenv("VOICE_CLIENT_SPEECH_SPEED", "1.5"))
    except ValueError:
        speed = 1.5

    language = "en-US"  # Fixed for now, can be made configurable later
    input_audio_format = os.getenv("VOICE_CLIENT_INPUT_AUDIO_FORMAT", "pcm16")
    output_audio_format = os.getenv("VOICE_CLIENT_OUTPUT_AUDIO_FORMAT", "pcm16")

    # Transcription settings
    transcription_enabled = os.getenv("VOICE_CLIENT_TRANSCRIPTION_ENABLED", "true").lower() == "true"
    transcription_model = os.getenv("VOICE_CLIENT_TRANSCRIPTION_MODEL", "whisper-1")

    # VAD / turn detection settings
    turn_type = "server_vad"  # Fixed for now
    try:
        turn_threshold = float(os.getenv("VOICE_CLIENT_VAD_THRESHOLD", "0.5"))
    except ValueError:
        turn_threshold = 0.5
    try:
        prefix_padding_ms = int(os.getenv("VOICE_CLIENT_VAD_PREFIX_PADDING_MS", "300"))
    except ValueError:
        prefix_padding_ms = 300
    try:
        silence_duration_ms = int(os.getenv("VOICE_CLIENT_VAD_SILENCE_DURATION_MS", "500"))
    except ValueError:
        silence_duration_ms = 500

    # Create agent with loaded instructions
    agent = RealtimeAgent(
        tools=tools,
        name="DHĀWAN",
        instructions=agent_instructions,
    )

    # Configure runner with tools using env-based config
    runner = RealtimeRunner(
        starting_agent=agent,
        config={
            "model_settings": {
                "model_name": model_name,
                "voice": voice,
                "speed": speed,
                "modalities": ["audio"],
                "language": language,
                "input_audio_format": input_audio_format,
                "output_audio_format": output_audio_format,
                "input_audio_transcription": {"model": transcription_model} if transcription_enabled else None,
                "turn_detection": {
                    "type": turn_type,
                    "threshold": turn_threshold,
                    "prefix_padding_ms": prefix_padding_ms,
                    "silence_duration_ms": silence_duration_ms,
                },
            }
        },
    )

    session = await runner.run()

    async with session:
        print(f"{Fore.GREEN}Session started. Mic streaming enabled.{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Speak into your microphone to interact with the "
            f"assistant.{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}Press Ctrl+C to exit.{Style.RESET_ALL}\n")

        # Start mic stream
        asyncio.create_task(mic_stream(session))

        async for event in session:
            try:
                if event.type == "agent_start":
                    print(f"{Fore.CYAN}Agent started: {event.agent.name}{Style.RESET_ALL}")

                elif event.type == "agent_end":
                    print(f"{Fore.CYAN}Agent ended: {event.agent.name}{Style.RESET_ALL}")

                elif event.type == "handoff":
                    print(
                        f"{Fore.YELLOW}Handoff from {event.from_agent.name} "
                        f"to {event.to_agent.name}{Style.RESET_ALL}"
                    )

                elif event.type == "tool_start":
                    tool_name = getattr(event.tool, "name", "unknown")
                    print(f"{Fore.MAGENTA}🔧 Tool started: {tool_name}{Style.RESET_ALL}")

                elif event.type == "tool_end":
                    tool_name = getattr(event.tool, "name", "unknown")
                    print(f"{Fore.MAGENTA}✓ Tool completed: {tool_name}{Style.RESET_ALL}")
                    # Print tool output (truncated)
                    output_str = str(event.output)
                    if len(output_str) > 200:
                        output_str = output_str[:200] + "..."
                    print(f"{Fore.MAGENTA}  Output: {output_str}{Style.RESET_ALL}")

                elif event.type == "conversation.item.input_audio_transcription.completed":
                    transcript = getattr(event, "transcript", None)
                    if transcript:
                        print_transcript("user", transcript)

                elif event.type == "response.audio_transcript.delta":
                    delta = getattr(event, "delta", None)
                    if delta:
                        print(f"{Fore.BLUE}{delta}{Style.RESET_ALL}", end="", flush=True)

                elif event.type == "response.audio_transcript.done":
                    transcript = getattr(event, "transcript", None)
                    if transcript:
                        print()  # New line after deltas
                        print_transcript("assistant", transcript)

                elif event.type == "audio":
                    # Play the audio chunk
                    chunk = event.audio.data
                    if chunk:
                        output_stream.write(chunk)

                elif event.type == "audio_interrupted":
                    print(f"{Fore.YELLOW}Audio interrupted{Style.RESET_ALL}")

                elif event.type == "error":
                    print(f"{Fore.RED}Error: {event.error}{Style.RESET_ALL}")

                elif event.type == "raw_model_event":
                    # The agents library handles tool calls automatically
                    # No need for manual tool call handling
                    pass

            except Exception as e:
                error_msg = _truncate_str(str(e), 200)
                print(f"{Fore.RED}Error processing event: {error_msg}{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
    finally:
        # Cleanup
        output_stream.stop_stream()
        output_stream.close()
        p.terminate()
        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
