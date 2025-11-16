import asyncio
import io

import pyaudio
from agents.realtime import RealtimeAgent, RealtimeRunner
from colorama import Fore, Style, init
from dotenv import load_dotenv
import pyaudio

from src.agent_host import CalendarAgentHost
from src.agent_host.spotify_agent import SpotifyAgentHost

# Initialize colorama
init()
SAMPLE_RATE = 24000  # GPT realtime PCM16 default
CHANNELS = 1

CHUNK = 1024
RATE = 16000

p = pyaudio.PyAudio()
output_stream = p.open(
    format=pyaudio.paInt16,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    output=True,
)

async def mic_stream(session):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            # THIS is the correct call:
            await session.send_audio(data)
            await asyncio.sleep(0)  # yield to event loop
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def _truncate_str(s: str, max_length: int) -> str:
    return s if len(s) <= max_length else s[:max_length] + "..."

def print_transcript(role: str, text: str):
    """
    Print transcript with color coding.

    Args:
        role: 'user' or 'assistant'
        text: Transcript text
    """
    if role == "user":
        print(f"{Fore.GREEN}[USER]: {text}{Style.RESET_ALL}")
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
    await initialize_mcp_agents()

    # Collect all tools from both agents
    tools = []
    if calendar_agent:
        tools.extend(calendar_agent.get_all_tools())
        print(f"{Fore.GREEN}Added {len(calendar_agent.get_all_tools())} calendar tools{Style.RESET_ALL}")
    if spotify_agent:
        tools.extend(spotify_agent.get_all_tools())
        print(f"{Fore.GREEN}Added {len(spotify_agent.get_all_tools())} Spotify tools{Style.RESET_ALL}")

    print(f"{Fore.CYAN}Total tools available: {len(tools)}{Style.RESET_ALL}\n")

    # text = io.FileIO.readlines()
    agent = RealtimeAgent(
        tools=tools,
        name="Assistant",
        instructions="You are a helpful voice assistant with access to Google Calendar and Spotify. Keep responses brief and conversational. make your responses rhyme.",
    )

    runner = RealtimeRunner(
        starting_agent=agent,
        config={
            "model_settings": {
                "model_name": "gpt-realtime",
                "voice": "ash",
                "speed" : 1.5,
                "modalities": ["audio"],
                "language": "en-US",
                "system"
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "gpt-4o-mini-transcribe", "language": "en"},
                "turn_detection": {"type": "semantic_vad", "interrupt_response": True},
            }
        },
    )

    session = await runner.run()

    async with session:
        print("Session started. Mic streaming enabled.")
        # start mic pump
        asyncio.create_task(mic_stream(session))

        async for event in session:
            print(event.type)
            try:
                if event.type == "agent_start":
                    pass
                    print(f"Agent started: {event.agent.name}")
                elif event.type == "agent_end":
                    pass
                    print(f"Agent ended: {event.agent.name}")
                elif event.type == "handoff":
                    print(f"Handoff from {event.from_agent.name} to {event.to_agent.name}")
                elif event.type == "tool_start":
                    pass
                    print(f"Tool started: {event.tool.name}")
                elif event.type == "tool_end":
                    pass
                    print(f"Tool ended: {event.tool.name}; output: {event.output}")
                elif event.type == "audio_end":
                    pass
                    print("Audio ended")
                elif event.type == "conversation.item.input_audio_transcription.delta":
                    print("[partial]", event.delta.get("text", ""))

                elif event.type == "conversation.item.input_audio_transcription.completed":
                    print("[final]", event.transcript)

                elif event.type == "conversation.item.input_audio_transcription.completed":
                    # User's speech transcription
                    transcript = event.get("transcript", "")
                    if transcript:
                        print_transcript("user", transcript)

                elif event.type == "response.audio_transcript.delta":
                    pass
                    # Assistant's partial text response
                    delta = event.get("delta", "")
                    if delta:
                        # We'll accumulate these and print on 'done'
                        pass
                elif event.type == "audio":
                    # Play the chunk the model just generated
                    chunk = event.audio.data  # raw PCM16 bytes
                    if chunk:
                        output_stream.write(chunk)
                    # event.audio is raw PCM16 out; hook to playback here
                    # pass
                elif event.type == "audio_interrupted":
                    print("Audio interrupted")
                elif event.type == "error":
                    print(f"Error: {event.error}")
                elif event.type == "raw_model_event":
                    pass
                    # print(f"Raw model event: {_truncate_str(str(event.data), 200)}")
            except Exception as e:
                print(f"Error processing event: {_truncate_str(str(e), 200)}")

if __name__ == "__main__":
    asyncio.run(main())
