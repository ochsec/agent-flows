# Web Operations MCP Server

A Model Context Protocol (MCP) server that provides web fetching and search capabilities.

## Features

- **web_fetch**: Fetch content from URLs and process it with AI-like analysis (no API key required)
- **web_search**: Search the web with intelligent fallback:
  - Uses Perplexity API when PERPLEXITY_API_KEY is set (better results with AI analysis)
  - Falls back to DuckDuckGo HTML search when no API key (no key required, basic results)
- Built-in caching for web_fetch with 15-minute expiration
- HTML to Markdown conversion
- Domain filtering for search results
- Redirect handling

## Installation

### Option 1: Python Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (optional, for enhanced search):
   ```bash
   export PERPLEXITY_API_KEY="your-perplexity-api-key"
   ```
   
   Note: If not set, web_search will use DuckDuckGo as a fallback.

### Option 2: Docker Installation

1. Build the Docker image:
   ```bash
   docker build -t web-ops-mcp-server .
   ```

2. Or use docker-compose:
   ```bash
   # Create .env file with your API key
   echo "PERPLEXITY_API_KEY=your-perplexity-api-key" > .env
   
   # Build and run
   docker-compose up --build
   ```

## Usage

### Running the Server

#### Python
```bash
python server.py
```

#### Docker
```bash
# Run with environment variable
docker run -it --rm -e PERPLEXITY_API_KEY="your-key" web-ops-mcp-server

# Or with docker-compose (after creating .env file)
docker-compose up
```

The server runs using stdin/stdout for MCP communication.

### MCP Client Configuration

To use this server with Claude Code or other MCP clients, add it to your MCP settings:

```json
{
  "mcpServers": {
    "web-ops": {
      "command": "python",
      "args": ["/path/to/mcp/web_ops/server.py"],
      "env": {
        "PERPLEXITY_API_KEY": "your-perplexity-api-key"
      }
    }
  }
}
```

For Docker-based deployment:
```json
{
  "mcpServers": {
    "web-ops": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "PERPLEXITY_API_KEY=your-key", "web-ops-mcp-server"]
    }
  }
}
```

### Tools

#### web_fetch

Fetches content from a URL and processes it with AI-like analysis. **No API key required.**

**Parameters:**
- `url` (string, required): The URL to fetch content from
- `prompt` (string, required): The prompt to run on the fetched content

**Returns:**
- `content`: The processed/analyzed content
- `url`: The final URL (after redirects)
- `cached`: Whether the result was from cache
- `redirect`: Information about redirects if any occurred

**Example:**
```json
{
  "name": "web_fetch",
  "arguments": {
    "url": "https://example.com",
    "prompt": "Summarize the main points of this webpage"
  }
}
```

#### web_search

Searches the web with intelligent fallback:
- **With PERPLEXITY_API_KEY**: Uses Perplexity API for AI-powered, comprehensive search results with source citations
- **Without API key**: Falls back to DuckDuckGo HTML search for basic web results

**Parameters:**
- `query` (string, required): The search query (minimum 2 characters)
- `allowed_domains` (array of strings, optional): List of domains to include in results
- `blocked_domains` (array of strings, optional): List of domains to exclude from results

**Returns:**
Array of search results, each containing:
- `title`: Result title
- `url`: Result URL
- `snippet`: Brief description
- `domain`: Domain of the result
- `content`: Full analyzed content from Perplexity

**Example:**
```json
{
  "name": "web_search",
  "arguments": {
    "query": "latest AI developments",
    "allowed_domains": ["arxiv.org", "github.com"]
  }
}
```

## Configuration

### Environment Variables

- `PERPLEXITY_API_KEY`: Optional - enhances web_search with AI-powered results. If not set, web_search falls back to DuckDuckGo.

### Cache Settings

- Web fetch results are cached for 15 minutes
- Cache is automatically cleaned up to remove expired entries

## Dependencies

- `mcp`: Model Context Protocol framework
- `requests`: HTTP library for web requests
- `html2text`: HTML to Markdown conversion (optional but recommended)

## Error Handling

The server handles various error conditions:
- Invalid URLs
- Network timeouts
- Missing API keys
- Domain filtering conflicts
- Request failures

All errors are returned as structured error messages through the MCP protocol.

## Development

The server is built using the MCP framework and follows standard MCP patterns:
- Tool registration via `@app.list_tools()`
- Tool execution via `@app.call_tool()`
- Async/await pattern for all operations
- Structured error handling and logging

## License

This project follows the same license as the parent agent-flows project.