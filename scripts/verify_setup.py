#!/usr/bin/env python3
"""
Verification script to test the structure without requiring actual Google credentials.

This script verifies:
- Python dependencies are installed
- Node.js dependencies are installed
- MCP server script exists and is valid
- Agent host module can be imported
- Basic structure is correct
"""

import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def check_python_dependencies():
    """Check if Python dependencies are installed."""
    print_header("Checking Python Dependencies")
    
    required_packages = ["mcp", "python-dotenv", "aiohttp", "pytest", "black", "ruff"]
    
    try:
        import importlib
        
        for package in required_packages:
            try:
                if package == "python-dotenv":
                    importlib.import_module("dotenv")
                else:
                    importlib.import_module(package)
                print(f"  ✓ {package} installed")
            except ImportError:
                print(f"  ✗ {package} NOT installed")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error checking dependencies: {e}")
        return False


def check_node_dependencies():
    """Check if Node.js dependencies are installed."""
    print_header("Checking Node.js Dependencies")
    
    mcp_server_dir = Path(__file__).parent.parent / "google-calendar-mcp-server"
    node_modules = mcp_server_dir / "node_modules"
    
    if node_modules.exists():
        print(f"  ✓ node_modules exists in {mcp_server_dir}")
        
        # Check for key packages
        key_packages = ["@modelcontextprotocol/sdk", "googleapis", "dotenv"]
        for package in key_packages:
            if (node_modules / package.split("/")[0]).exists():
                print(f"  ✓ {package} installed")
            else:
                print(f"  ✗ {package} NOT installed")
                return False
        
        return True
    else:
        print(f"  ✗ node_modules NOT found in {mcp_server_dir}")
        print("     Run: cd google-calendar-mcp-server && npm install")
        return False


def check_mcp_server():
    """Check if MCP server file exists and is valid."""
    print_header("Checking MCP Server")
    
    server_file = Path(__file__).parent.parent / "google-calendar-mcp-server" / "server.js"
    
    if server_file.exists():
        print(f"  ✓ server.js exists: {server_file}")
        
        # Check if it's valid JavaScript (basic check)
        content = server_file.read_text()
        if "google.calendar" in content and "CallToolRequestSchema" in content:
            print("  ✓ server.js contains expected MCP and Google Calendar code")
            return True
        else:
            print("  ✗ server.js doesn't appear to be a valid MCP server")
            return False
    else:
        print(f"  ✗ server.js NOT found: {server_file}")
        return False


def check_agent_host():
    """Check if agent host module can be imported."""
    print_header("Checking Agent Host Module")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from agent_host import CalendarAgentHost
        
        print("  ✓ agent_host module imported successfully")
        print("  ✓ CalendarAgentHost class available")
        
        # Check if class has expected methods
        expected_methods = [
            "connect_to_mcp_server",
            "list_events",
            "get_event",
            "create_event",
            "update_event",
            "delete_event",
            "get_free_busy",
        ]
        
        for method in expected_methods:
            if hasattr(CalendarAgentHost, method):
                print(f"  ✓ Method '{method}' exists")
            else:
                print(f"  ✗ Method '{method}' missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ✗ Error importing agent_host: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_documentation():
    """Check if documentation files exist."""
    print_header("Checking Documentation")
    
    docs_dir = Path(__file__).parent.parent / "docs"
    required_docs = [
        "GOOGLE_CALENDAR_SETUP.md",
        "AGENT_SYSTEM_INSTRUCTIONS.md",
    ]
    
    all_exist = True
    for doc in required_docs:
        doc_path = docs_dir / doc
        if doc_path.exists():
            print(f"  ✓ {doc} exists")
        else:
            print(f"  ✗ {doc} NOT found")
            all_exist = False
    
    return all_exist


def check_configuration():
    """Check if configuration files exist."""
    print_header("Checking Configuration Files")
    
    root_dir = Path(__file__).parent.parent
    config_files = [
        ".env.example",
        "pyproject.toml",
        "requirements.txt",
        "google-calendar-mcp-server/package.json",
    ]
    
    all_exist = True
    for config in config_files:
        config_path = root_dir / config
        if config_path.exists():
            print(f"  ✓ {config} exists")
        else:
            print(f"  ✗ {config} NOT found")
            all_exist = False
    
    return all_exist


def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("Google Calendar MCP Integration - Verification Script")
    print("=" * 70)
    
    results = {
        "Python Dependencies": check_python_dependencies(),
        "Node.js Dependencies": check_node_dependencies(),
        "MCP Server": check_mcp_server(),
        "Agent Host": check_agent_host(),
        "Documentation": check_documentation(),
        "Configuration": check_configuration(),
    }
    
    print_header("Verification Summary")
    
    all_passed = True
    for check, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {check}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✓ All checks passed!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Google Calendar credentials to .env")
        print("3. Run: python examples/test_calendar.py")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1
    
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
