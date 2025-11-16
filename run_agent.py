#!/usr/bin/env python3
"""
Quick Start Script for OpenAI Realtime Agent with Integrations

This script provides an easy way to run the integrated agent with
options to enable/disable specific integrations.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    parser = argparse.ArgumentParser(
        description="Run OpenAI Realtime Agent with optional Calendar and Spotify integration"
    )
    parser.add_argument(
        "--no-calendar",
        action="store_true",
        help="Disable Google Calendar integration"
    )
    parser.add_argument(
        "--no-spotify",
        action="store_true",
        help="Disable Spotify integration"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default="ash",
        choices=["alloy", "echo", "shimmer", "ash", "ballad", "coral", "sage", "verse"],
        help="Voice to use for the assistant (default: ash)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.5,
        help="Speech speed multiplier (0.25 to 4.0, default: 1.5)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Set environment variables based on args
    import os
    os.environ["SKIP_CALENDAR"] = "1" if args.no_calendar else "0"
    os.environ["SKIP_SPOTIFY"] = "1" if args.no_spotify else "0"
    os.environ["VOICE_SETTING"] = args.voice
    os.environ["SPEED_SETTING"] = str(args.speed)

    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    print("=" * 70)
    print("OpenAI Realtime Agent - Quick Start")
    print("=" * 70)
    print()
    print(f"Voice: {args.voice}")
    print(f"Speed: {args.speed}x")
    print(f"Calendar: {'Disabled' if args.no_calendar else 'Enabled'}")
    print(f"Spotify: {'Disabled' if args.no_spotify else 'Enabled'}")
    print()
    print("Starting agent...")
    print()

    # Import and run the main script
    try:
        # Dynamic import to use the environment variables
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "integrated_agent",
            project_root / "openai-agent-integrated.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Run the main function
        asyncio.run(module.main())

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

