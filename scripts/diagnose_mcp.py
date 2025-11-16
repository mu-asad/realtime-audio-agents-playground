#!/usr/bin/env python3
"""
Diagnostic script to check MCP server startup.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

async def test_node_server():
    """Test if the Node.js server can start."""
    repo_root = Path(__file__).parent.parent
    server_script = repo_root / "google-calendar-mcp-server" / "server.js"

    print(f"Testing MCP server at: {server_script}")

    if not server_script.exists():
        print(f"❌ Server script not found!")
        return False

    print("✓ Server script exists")

    # Try to start the server process
    print("\nStarting server process...")
    try:
        process = await asyncio.create_subprocess_exec(
            "node",
            str(server_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Wait a bit and see if it outputs anything
        try:
            stdout, stderr = await asyncio.wait_for(
                asyncio.gather(
                    process.stdout.readline(),
                    process.stderr.readline()
                ),
                timeout=3.0
            )

            if stderr:
                print(f"Server stderr: {stderr.decode().strip()}")
            if stdout:
                print(f"Server stdout: {stdout.decode().strip()}")

        except asyncio.TimeoutError:
            print("⚠ Server started but no output received (this might be normal)")

        # Check if process is still running
        if process.returncode is None:
            print("✓ Server process is running")
            process.terminate()
            await process.wait()
            return True
        else:
            print(f"❌ Server exited with code: {process.returncode}")
            # Read remaining output
            stdout, stderr = await process.communicate()
            if stderr:
                print(f"Error output:\n{stderr.decode()}")
            return False

    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js.")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_mcp_dependencies():
    """Check if MCP server dependencies are installed."""
    repo_root = Path(__file__).parent.parent
    node_modules = repo_root / "google-calendar-mcp-server" / "node_modules"
    package_json = repo_root / "google-calendar-mcp-server" / "package.json"

    print("\nChecking MCP server dependencies...")

    if not package_json.exists():
        print("❌ package.json not found")
        return False

    print("✓ package.json exists")

    if not node_modules.exists():
        print("❌ node_modules not found")
        print("   Run: cd google-calendar-mcp-server && npm install")
        return False

    print("✓ node_modules exists")

    # Check for key dependencies
    required_deps = [
        "@modelcontextprotocol/sdk",
        "googleapis",
        "dotenv"
    ]

    for dep in required_deps:
        dep_path = node_modules / dep.replace("/", Path("/"))
        if dep_path.exists():
            print(f"  ✓ {dep}")
        else:
            print(f"  ❌ {dep} not found")
            return False

    return True

async def main():
    print("=" * 60)
    print("MCP Server Diagnostic Tool")
    print("=" * 60)

    # Check dependencies
    deps_ok = await check_mcp_dependencies()

    if not deps_ok:
        print("\n❌ Dependencies check failed")
        return False

    # Test server startup
    server_ok = await test_node_server()

    if not server_ok:
        print("\n❌ Server startup test failed")
        return False

    print("\n✅ All checks passed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

