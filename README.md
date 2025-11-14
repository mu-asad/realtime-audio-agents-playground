# azure-realtime-audio-playground

A sandbox for experimenting with live audio (mic → Azure Realtime → audio/text back), with minimal assumptions about tech stack.

## Project Structure

```
azure-realtime-audio-playground/
├── server/              # WebSocket server for audio streaming
│   ├── __init__.py
│   └── audio_server.py  # Server implementation with Azure integration stub
├── client/              # WebSocket client for audio capture
│   ├── __init__.py
│   └── audio_client.py  # Client implementation (placeholder)
├── .env.local.example   # Template for environment variables
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Python project configuration
└── README.md           # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mu-asad/azure-realtime-audio-playground.git
   cd azure-realtime-audio-playground
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your Azure OpenAI credentials
   ```

### Running the Server

The server provides a WebSocket endpoint for audio streaming:

```bash
python -m server.audio_server
```

The server will start on `ws://localhost:8765` by default.

### Running the Client

The client connects to the server and sends test data:

```bash
python -m client.audio_client
```

## Configuration

All configuration is managed through environment variables in `.env.local`:

- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT` - Your Azure OpenAI deployment name
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-10-01-preview)
- `SERVER_HOST` - WebSocket server host (default: localhost)
- `SERVER_PORT` - WebSocket server port (default: 8765)

**Important:** Never commit `.env.local` to version control. It contains sensitive credentials.

## Current Status

This is a minimal stub implementation:

- ✅ Server WebSocket endpoint (not calling Azure yet)
- ✅ Client WebSocket connection (not capturing audio yet)
- ✅ Environment-based configuration
- ✅ Basic message passing between client and server
- ⏳ Azure OpenAI Realtime API integration (planned)
- ⏳ Live microphone audio capture (planned)
- ⏳ Audio playback (planned)

## Development

The project is intentionally minimal and easy to extend. Key extension points:

1. **Server (`server/audio_server.py`):**
   - Add Azure OpenAI Realtime API connection
   - Implement audio forwarding to Azure
   - Handle Azure responses

2. **Client (`client/audio_client.py`):**
   - Add microphone audio capture using PyAudio
   - Implement audio playback
   - Add UI/controls

## License

See LICENSE file for details.
