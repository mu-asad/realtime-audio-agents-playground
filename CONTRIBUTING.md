# Contributing to Azure Realtime Audio Playground

Thank you for your interest in contributing! This document provides guidelines for contributing to the Google Calendar MCP integration and the broader project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/azure-realtime-audio-playground.git
   cd azure-realtime-audio-playground
   ```
3. **Set up your development environment**:
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Node.js dependencies
   cd google-calendar-mcp-server && npm install && cd ..
   ```
4. **Verify your setup**:
   ```bash
   python scripts/verify_setup.py
   ```

## Development Workflow

### Making Changes

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards (see below)

3. **Test your changes**:
   ```bash
   # Run tests
   python examples/test_calendar.py
   
   # Run verification
   python scripts/verify_setup.py
   ```

4. **Lint and format your code**:
   ```bash
   # Python
   black src/ examples/ scripts/*.py
   ruff check src/ examples/ scripts/*.py
   
   # If you modified Node.js code, you can add linting there too
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request** on GitHub

## Coding Standards

### Python Code

- **Formatting**: Use `black` with default settings (100 character line length)
- **Linting**: Code must pass `ruff check` with no errors
- **Type Hints**: Add type hints to function signatures
- **Docstrings**: Use docstrings for classes and public methods
- **Async/Await**: Use async/await for I/O operations

Example:
```python
async def list_events(
    self,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    max_results: int = 10,
) -> Dict[str, Any]:
    """
    List calendar events.
    
    Args:
        time_min: Start time in ISO 8601 format
        time_max: End time in ISO 8601 format
        max_results: Maximum number of events
        
    Returns:
        Dictionary containing events and metadata
    """
    # Implementation
```

### Node.js Code

- **Style**: Follow standard JavaScript/ES6+ conventions
- **Async**: Use async/await instead of callbacks
- **Error Handling**: Always handle errors gracefully
- **Comments**: Add comments for complex logic

### Documentation

- **Markdown**: Use proper Markdown formatting
- **Examples**: Include code examples for new features
- **Links**: Keep internal links up to date
- **Clarity**: Write for users who may be unfamiliar with the codebase

## Testing

### Running Tests

```bash
# Basic test suite
python examples/test_calendar.py

# Advanced examples
python examples/advanced_examples.py

# Verification
python scripts/verify_setup.py
```

### Writing Tests

When adding new features:
1. Add test cases to `examples/test_calendar.py` if appropriate
2. Create new example scripts for complex features
3. Update verification script if adding new dependencies

## Common Contributions

### Adding New Calendar Tools

1. Add the tool definition to `google-calendar-mcp-server/server.js`:
   ```javascript
   {
     name: "new_tool",
     description: "Description of what it does",
     inputSchema: {
       type: "object",
       properties: {
         // Define parameters
       },
       required: ["param1"]
     }
   }
   ```

2. Implement the handler function:
   ```javascript
   async function newTool(args) {
     // Implementation
     return { result: "data" };
   }
   ```

3. Add to TOOL_HANDLERS:
   ```javascript
   const TOOL_HANDLERS = {
     // existing tools...
     new_tool: newTool,
   };
   ```

4. Add convenience method to `src/agent_host/calendar_agent.py`:
   ```python
   async def new_tool(self, param1: str) -> Dict[str, Any]:
       """Description of what it does."""
       return await self.call_tool("new_tool", {"param1": param1})
   ```

5. Update documentation and tests

### Improving Documentation

- Documentation lives in the `docs/` directory
- Update relevant .md files
- Keep examples up to date
- Add screenshots if helpful

### Fixing Bugs

1. Create an issue describing the bug (if one doesn't exist)
2. Reference the issue in your commit message: "Fix #123: Description"
3. Add a test that would have caught the bug
4. Verify the fix with existing tests

## Code Review

All contributions require code review. Reviewers will check:
- Code quality and style
- Test coverage
- Documentation updates
- Backwards compatibility
- Security implications

## Security

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email the maintainers directly
3. Include details of the vulnerability
4. Allow time for a fix before public disclosure

## Questions?

- Open an issue for general questions
- Check existing documentation first
- Be respectful and patient

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Recognition

Contributors will be recognized in:
- Git commit history
- Release notes (for significant contributions)
- Project README (for major features)

Thank you for contributing! 🎉
