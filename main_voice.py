#!/usr/bin/env python3
"""
Main script for Azure GPT Realtime voice chat.

This script provides a simple voice chat interface using the local microphone
and Azure GPT Realtime API.
"""

import asyncio
import os
import signal
import sys
from pathlib import Path

from colorama import Fore, Style, init
from dotenv import load_dotenv

from src.realtime_voice_client import RealtimeVoiceClient

# Initialize colorama
init()

# Load environment variables
load_dotenv()


def load_system_prompt(prompt_file: str = "prompts/comedian.txt") -> str:
    """
    Load system prompt from file.

    Args:
        prompt_file: Path to prompt file relative to repo root

    Returns:
        System prompt text
    """
    repo_root = Path(__file__).parent
    prompt_path = repo_root / prompt_file

    if not prompt_path.exists():
        print(f"{Fore.YELLOW}Warning: Prompt file not found at {prompt_path}{Style.RESET_ALL}")
        return "You are a helpful assistant."

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Failed to load prompt file: {e}{Style.RESET_ALL}")
        return "You are a helpful assistant."


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


def validate_config():
    """Validate required configuration is present."""
    required_vars = [
        "OPENAI_API_KEY",
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"{Fore.RED}Error: Missing required environment variables:{Style.RESET_ALL}")
        for var in missing:
            print(f"  - {var}")
        print(f"\n{Fore.YELLOW}Please set these in your .env file{Style.RESET_ALL}")
        return False

    return True


async def main():
    """Main entry point for the voice client."""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}OpenAI Realtime Voice Chat{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

    # Validate configuration
    if not validate_config():
        sys.exit(1)

    # Load system prompt
    system_prompt = load_system_prompt()
    print(f"{Fore.YELLOW}System prompt loaded from prompts/comedian.txt{Style.RESET_ALL}\n")

    # Build configuration
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-realtime-preview-2024-10-01"),
        "sample_rate": int(os.getenv("VOICE_CLIENT_SAMPLE_RATE", "16000")),
        "speech_speed": float(os.getenv("VOICE_CLIENT_SPEECH_SPEED", "1.0")),
        "system_prompt": system_prompt,
    }

    # Optional device index
    device_index_str = os.getenv("VOICE_CLIENT_DEVICE_INDEX")
    if device_index_str:
        try:
            config["device_index"] = int(device_index_str)
        except ValueError:
            print(
                f"{Fore.YELLOW}Warning: Invalid VOICE_CLIENT_DEVICE_INDEX, "
                f"using default{Style.RESET_ALL}"
            )

    # Create client
    client = RealtimeVoiceClient(config)
    client.set_transcript_callback(print_transcript)

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
        asyncio.create_task(client.stop())

    signal.signal(signal.SIGINT, signal_handler)

    print(f"{Fore.GREEN}Starting voice session...{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Speak into your microphone. Press Ctrl+C to exit.{Style.RESET_ALL}\n")

    # Start the client
    try:
        await client.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Session ended by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
