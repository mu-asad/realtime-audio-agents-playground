#!/usr/bin/env python3
"""
Verify that required environment variables are set.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repo root
repo_root = Path(__file__).parent.parent
env_file = repo_root / ".env"

if not env_file.exists():
    print(f"❌ .env file not found at: {env_file}")
    print("   Please create a .env file with your Google Calendar credentials.")
    exit(1)

print(f"✓ .env file found at: {env_file}")

load_dotenv(env_file)

required_vars = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
]

optional_vars = [
    "GOOGLE_CALENDAR_ID",
]

print("\nChecking required environment variables:")
missing = []
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Show first/last few characters for security
        if len(value) > 10:
            masked = f"{value[:4]}...{value[-4:]}"
        else:
            masked = "***"
        print(f"  ✓ {var}: {masked}")
    else:
        print(f"  ❌ {var}: NOT SET")
        missing.append(var)

print("\nChecking optional environment variables:")
for var in optional_vars:
    value = os.getenv(var)
    if value:
        print(f"  ✓ {var}: {value}")
    else:
        print(f"  ⚠ {var}: not set (will use default)")

if missing:
    print(f"\n❌ Missing required variables: {', '.join(missing)}")
    print("   Please add these to your .env file.")
    exit(1)
else:
    print("\n✅ All required environment variables are set!")
    exit(0)

