#!/usr/bin/env python3
"""
Web Operations MCP Server

A Model Context Protocol server that provides web fetching and search capabilities.
Supports web_fetch for URL content retrieval and web_search using Perplexity API.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import os
import re
import urllib.parse
from urllib.parse import urlparse

import requests
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web-ops-server")

app = Server("web-ops-server")


class WebOperationsServer:
    """Web operations server implementation."""
    
    def __init__(self):
        """Initialize the web operations server."""
        # Cache for WebFetch with 15-minute expiration
        self._fetch_cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_duration = timedelta(minutes=15)
        
        # HTML to markdown converter
        if HAS_HTML2TEXT:
            self._html2text = html2text.HTML2Text()
            self._html2text.ignore_links = False
            self._html2text.ignore_images = False
            self._html2text.body_width = 0  # Don't wrap lines
        else:
            self._html2text = None
    
    def web_fetch(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        Fetch content from a URL and process it with AI-like analysis.
        
        Args:
            url: The URL to fetch content from
            prompt: The prompt to run on the fetched content
            
        Returns:
            Dictionary containing:
                - content: The processed/analyzed content
                - url: The final URL (after redirects)
                - cached: Whether the result was from cache
                - redirect: Information about redirects if any occurred
        """
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
            
        # Upgrade HTTP to HTTPS
        if parsed.scheme == 'http':
            url = url.replace('http://', 'https://', 1)
            
        # Check cache
        cache_key = self._get_cache_key(url, prompt)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            cached_result['cached'] = True
            return cached_result
            
        # Fetch the content
        try:
            response = requests.get(
                url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; MCP-WebOps/1.0)'
                },
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check for redirects to different hosts
            final_url = response.url
            redirect_info = None
            
            if url != final_url:
                original_host = urlparse(url).netloc
                final_host = urlparse(final_url).netloc
                
                if original_host != final_host:
                    redirect_info = {
                        'original_url': url,
                        'final_url': final_url,
                        'message': f"Redirected from {original_host} to {final_host}"
                    }
            
            # Convert HTML to markdown
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' in content_type and self._html2text:
                markdown_content = self._html2text.handle(response.text)
            elif 'text/html' in content_type:
                # Fallback: simple HTML stripping if html2text not available
                text = response.text
                text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', text, flags=re.IGNORECASE)
                text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.IGNORECASE)
                text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.IGNORECASE)
                # Then strip remaining HTML tags
                text = re.sub('<[^<]+?>', '', text)
                # Clean up whitespace
                markdown_content = re.sub(r'\n\s*\n', '\n\n', text.strip())
            else:
                # For non-HTML content, use as-is
                markdown_content = response.text
                
            # Process with AI-like analysis
            processed_content = self._process_with_ai(markdown_content, prompt)
            
            result = {
                'content': processed_content,
                'url': final_url,
                'cached': False
            }
            
            if redirect_info:
                result['redirect'] = redirect_info
                
            # Cache the result
            self._add_to_cache(cache_key, result)
            
            return result
            
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to fetch URL: {str(e)}")
    
    def web_search(self, query: str, allowed_domains: Optional[List[str]] = None, 
                   blocked_domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search the web using Perplexity API or DuckDuckGo fallback.
        
        Args:
            query: The search query
            allowed_domains: Optional list of domains to include
            blocked_domains: Optional list of domains to block
            
        Returns:
            List of search results with title, url, snippet, domain, and content
        """
        if len(query) < 2:
            raise ValueError("Query must be at least 2 characters long")
        
        # Get Perplexity API key
        api_key = os.getenv("PERPLEXITY_API_KEY")
        
        if api_key:
            try:
                return self._search_with_perplexity(query, api_key, allowed_domains, blocked_domains)
            except Exception as e:
                # If Perplexity fails, fall back to DuckDuckGo
                logger.warning(f"Perplexity search failed, falling back to DuckDuckGo: {str(e)}")
                return self._search_with_duckduckgo(query, allowed_domains, blocked_domains)
        else:
            return self._search_with_duckduckgo(query, allowed_domains, blocked_domains)
    
    def _search_with_perplexity(self, query: str, api_key: str, 
                                allowed_domains: Optional[List[str]] = None,
                                blocked_domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search using Perplexity API."""
        
        try:
            # Call Perplexity API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant. Provide comprehensive information with source citations."
                    },
                    {
                        "role": "user", 
                        "content": f"Research and provide detailed information about: {query}. Include specific details, comparisons, and current information with source URLs."
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            citations = result.get("citations", [])
            
            # Extract URLs from citations and content
            search_results = []
            
            # Parse citations to create search results
            for i, citation in enumerate(citations[:5]):  # Limit to top 5 sources
                url = citation
                domain = urlparse(url).netloc
                
                # Apply domain filtering
                if blocked_domains and domain in blocked_domains:
                    continue
                if allowed_domains and domain not in allowed_domains:
                    continue
                
                search_results.append({
                    'title': f"Source {i+1}: {domain}",
                    'url': url,
                    'snippet': f"Information about {query} from {domain}",
                    'domain': domain,
                    'content': content  # Full Perplexity response
                })
            
            # If no citations, create a single result with Perplexity content
            if not search_results:
                search_results.append({
                    'title': f"Perplexity Research: {query}",
                    'url': "https://perplexity.ai",
                    'snippet': f"AI-powered research results for {query}",
                    'domain': "perplexity.ai", 
                    'content': content
                })
            
            return search_results
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Perplexity API search failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Web search error: {str(e)}")
    
    def _search_with_duckduckgo(self, query: str, allowed_domains: Optional[List[str]] = None,
                                blocked_domains: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fallback search using DuckDuckGo HTML interface (no API key required)."""
        try:
            # DuckDuckGo HTML search URL
            search_url = "https://html.duckduckgo.com/html/"
            
            # Search parameters
            params = {
                'q': query,
                's': '0',  # Start from first result
                'dc': '0',  # Disable safe search
                'v': 'l',  # List view
                'o': 'json'  # Request JSON-friendly output
            }
            
            # Headers to appear more like a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            # DuckDuckGo might return 202 (rate limiting) or other status codes
            if response.status_code == 202:
                # Check if this is a CAPTCHA challenge
                if "Unfortunately, bots use DuckDuckGo too" in response.text:
                    return [{
                        'title': f"DuckDuckGo Bot Detection",
                        'url': "https://duckduckgo.com",
                        'snippet': "DuckDuckGo detected automated request and requires CAPTCHA verification",
                        'domain': "duckduckgo.com",
                        'content': f"DuckDuckGo search blocked for: {query}\n\nDuckDuckGo's bot detection system has triggered a CAPTCHA challenge. This commonly happens in containerized environments.\n\nRecommendations:\n1. Set PERPLEXITY_API_KEY for enhanced search without bot detection\n2. Use this server from a non-containerized environment\n3. Contact your administrator about search alternatives\n\n(Note: This is a DuckDuckGo limitation, not a server issue)"
                    }]
                else:
                    # Try to parse it in case it contains some results
                    html_content = response.text
            elif response.status_code != 200:
                return [{
                    'title': f"DuckDuckGo Search Error",
                    'url': "https://duckduckgo.com",
                    'snippet': f"DuckDuckGo returned status {response.status_code}",
                    'domain': "duckduckgo.com",
                    'content': f"DuckDuckGo search error for: {query}\n\nStatus code: {response.status_code}\n\n(Note: Using DuckDuckGo fallback search - for enhanced AI-powered results, set PERPLEXITY_API_KEY)"
                }]
            else:
                response.raise_for_status()
                html_content = response.text
            
            # Parse HTML results
            results = []
            
            import re
            
            # Extract the results section
            results_start = html_content.find('<div id="links" class="results">')
            if results_start == -1:
                results_start = html_content.find('<div class="results">')
            
            if results_start > 0:
                # Get a larger chunk of the results section to capture more results
                results_section = html_content[results_start:results_start + 15000]  # Get more content
                
                # Find individual result items - look for both redirect and direct links
                # Pattern 1: DuckDuckGo redirect links
                redirect_pattern = r'href="(//duckduckgo\.com/l/\?uddg=[^"]+)"[^>]*>([^<]+)</a>'
                redirect_matches = re.findall(redirect_pattern, results_section, re.IGNORECASE)
                
                # Pattern 2: Direct external links
                direct_pattern = r'href="(https?://[^"]+)"[^>]*>([^<]+)</a>'
                direct_matches = re.findall(direct_pattern, results_section, re.IGNORECASE)
                
                # Combine all matches
                all_matches = []
                
                # Process redirect matches
                for url_raw, title_raw in redirect_matches:
                    if title_raw.strip() and len(title_raw.strip()) > 2:
                        all_matches.append((url_raw, title_raw.strip()))
                
                # Process direct matches (avoid duplicates from DuckDuckGo domain)
                for url_raw, title_raw in direct_matches:
                    if 'duckduckgo.com' not in url_raw and title_raw.strip() and len(title_raw.strip()) > 2:
                        all_matches.append((url_raw, title_raw.strip()))
                
                # Remove duplicates by URL
                seen_urls = set()
                unique_matches = []
                for url, title in all_matches:
                    if url not in seen_urls:
                        seen_urls.add(url)
                        unique_matches.append((url, title))
                
                title_matches = unique_matches
                
                for i, match in enumerate(title_matches[:10]):  # Limit to 10 results
                    url_raw, title_raw = match
                    snippet_raw = "No description available"  # DuckDuckGo HTML doesn't always have snippets
                    
                    # Clean up DuckDuckGo redirect URLs
                    if url_raw.startswith('//duckduckgo.com/l/?uddg='):
                        # Extract the actual URL from DuckDuckGo's redirect
                        url_param = url_raw.split('uddg=')[1].split('&')[0]
                        url = urllib.parse.unquote(url_param)
                    elif url_raw.startswith('//'):
                        url = 'https:' + url_raw
                    else:
                        url = url_raw
                    
                    # Skip ads and internal DuckDuckGo links
                    if 'duckduckgo.com/y.js' in url or 'duckduckgo.com/duckduckgo-help' in url:
                        continue
                        
                    try:
                        domain = urlparse(url).netloc
                    except:
                        continue
                    
                    # Apply domain filtering
                    if blocked_domains and domain in blocked_domains:
                        continue
                    if allowed_domains and domain not in allowed_domains:
                        continue
                    
                    # Clean up HTML entities and text
                    title = title_raw.strip()
                    snippet = snippet_raw.strip() if snippet_raw else "No description available"
                    
                    # Clean up HTML entities
                    for old, new in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&#39;', "'")]:
                        title = title.replace(old, new)
                        snippet = snippet.replace(old, new)
                
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'domain': domain,
                        'content': f"DuckDuckGo Search Result: {title}\n\n{snippet}\n\nSource: {url}\n\n(Note: Using DuckDuckGo fallback search - for enhanced AI-powered results, set PERPLEXITY_API_KEY)"
                    })
            else:
                # Fallback: try simpler pattern matching
                simple_links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]+)</a>', html_content)
                for i, (url, title) in enumerate(simple_links[:5]):
                    if 'duckduckgo.com' not in url and len(title.strip()) > 3:
                        domain = urlparse(url).netloc
                        results.append({
                            'title': title.strip(),
                            'url': url,
                            'snippet': "No description available",
                            'domain': domain,
                            'content': f"DuckDuckGo Search Result: {title.strip()}\n\nSource: {url}\n\n(Note: Using DuckDuckGo fallback search - for enhanced AI-powered results, set PERPLEXITY_API_KEY)"
                        })
            
            # If no results found, return a message
            if not results:
                results.append({
                    'title': f"DuckDuckGo Search: {query}",
                    'url': "https://duckduckgo.com",
                    'snippet': "No results found for your search query.",
                    'domain': "duckduckgo.com",
                    'content': f"No search results found for: {query}\n\n(Note: Using DuckDuckGo fallback search - for enhanced AI-powered results, set PERPLEXITY_API_KEY)"
                })
            
            return results
            
        except Exception as e:
            # Return error as a result
            return [{
                'title': "Search Error",
                'url': "https://duckduckgo.com",
                'snippet': f"Search failed: {str(e)}",
                'domain': "duckduckgo.com",
                'content': f"DuckDuckGo search failed: {str(e)}\n\n(Note: Using DuckDuckGo fallback search - for enhanced AI-powered results, set PERPLEXITY_API_KEY)"
            }]
    
    def _process_with_ai(self, content: str, prompt: str) -> str:
        """Process content with AI-like analysis based on the prompt."""
        prompt_lower = prompt.lower()
        
        # Extract key information from content
        lines = content.split('\n')
        content_length = len(content)
        word_count = len(content.split())
        
        # Identify content structure
        headings = [line for line in lines if line.startswith('#')]
        links = [line for line in lines if 'http' in line or 'www.' in line]
        
        # Build analysis based on prompt intent
        analysis_parts = []
        
        if any(keyword in prompt_lower for keyword in ['summarize', 'summary', 'main points']):
            analysis_parts.append("## Summary")
            paragraphs = [line.strip() for line in lines if line.strip() and not line.startswith('#')][:3]
            for para in paragraphs:
                if len(para) > 50:
                    analysis_parts.append(f"- {para[:200]}{'...' if len(para) > 200 else ''}")
                    
        elif any(keyword in prompt_lower for keyword in ['extract', 'find', 'identify']):
            analysis_parts.append("## Extracted Information")
            if 'link' in prompt_lower or 'url' in prompt_lower:
                analysis_parts.append("### Links Found:")
                for link in links[:5]:
                    analysis_parts.append(f"- {link.strip()}")
            elif 'heading' in prompt_lower or 'title' in prompt_lower:
                analysis_parts.append("### Headings Found:")
                for heading in headings[:10]:
                    analysis_parts.append(f"- {heading.strip()}")
            else:
                keywords = [word for word in prompt.split() if len(word) > 3]
                relevant_lines = []
                for line in lines:
                    if any(keyword.lower() in line.lower() for keyword in keywords):
                        relevant_lines.append(line.strip())
                        if len(relevant_lines) >= 5:
                            break
                for line in relevant_lines:
                    analysis_parts.append(f"- {line[:150]}{'...' if len(line) > 150 else ''}")
                    
        elif any(keyword in prompt_lower for keyword in ['analyze', 'analysis', 'understand']):
            analysis_parts.append("## Content Analysis")
            analysis_parts.append(f"**Document Structure:**")
            analysis_parts.append(f"- Length: {content_length:,} characters, {word_count:,} words")
            analysis_parts.append(f"- Sections: {len(headings)} headings found")
            analysis_parts.append(f"- Links: {len(links)} links identified")
            
            if headings:
                analysis_parts.append("\\n**Main Topics:**")
                for heading in headings[:5]:
                    clean_heading = heading.replace('#', '').strip()
                    analysis_parts.append(f"- {clean_heading}")
                    
        elif any(keyword in prompt_lower for keyword in ['explain', 'describe', 'what']):
            analysis_parts.append("## Content Description")
            first_paragraph = next((line.strip() for line in lines if line.strip() and not line.startswith('#')), "")
            if first_paragraph:
                analysis_parts.append(f"This content appears to be about: {first_paragraph[:300]}{'...' if len(first_paragraph) > 300 else ''}")
            
            if headings:
                analysis_parts.append("\\n**Key sections include:**")
                for heading in headings[:7]:
                    clean_heading = heading.replace('#', '').strip()
                    analysis_parts.append(f"- {clean_heading}")
                    
        else:
            # Default comprehensive analysis
            analysis_parts.append("## Content Overview")
            analysis_parts.append(f"Document contains {word_count:,} words across {len(lines)} lines.")
            
            if headings:
                analysis_parts.append("\\n**Structure:**")
                for heading in headings[:5]:
                    analysis_parts.append(f"- {heading.strip()}")
            
            substantial_lines = [line.strip() for line in lines if len(line.strip()) > 100][:3]
            if substantial_lines:
                analysis_parts.append("\\n**Key Content:**")
                for line in substantial_lines:
                    analysis_parts.append(f"- {line[:200]}{'...' if len(line) > 200 else ''}")
        
        # Add metadata
        analysis_parts.append(f"\\n---")
        analysis_parts.append(f"*Analysis based on prompt: \"{prompt}\"*")
        
        return "\\n".join(analysis_parts)
    
    def _get_cache_key(self, url: str, prompt: str) -> str:
        """Generate a cache key from URL and prompt."""
        combined = f"{url}|{prompt}"
        return hashlib.md5(combined.encode()).hexdigest()
        
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache if not expired."""
        if cache_key in self._fetch_cache:
            result, timestamp = self._fetch_cache[cache_key]
            if datetime.now() - timestamp < self._cache_duration:
                return result.copy()
            else:
                del self._fetch_cache[cache_key]
        return None
        
    def _add_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Add item to cache with current timestamp."""
        self._fetch_cache[cache_key] = (result.copy(), datetime.now())
        self._cleanup_cache()
        
    def _cleanup_cache(self) -> None:
        """Remove expired entries from cache."""
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self._fetch_cache.items()
            if current_time - timestamp >= self._cache_duration
        ]
        for key in expired_keys:
            del self._fetch_cache[key]


# Global server instance
web_ops = WebOperationsServer()

# Check if Perplexity API key is available
HAS_PERPLEXITY = bool(os.getenv("PERPLEXITY_API_KEY"))


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    description = "Search the web using Perplexity API (if available) or DuckDuckGo fallback"
    if not HAS_PERPLEXITY:
        description = "Search the web using DuckDuckGo (no API key required)"
    
    return [
        types.Tool(
            name="web_fetch",
            description="Fetch content from a URL and process it with AI-like analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch content from"
                    },
                    "prompt": {
                        "type": "string", 
                        "description": "The prompt to run on the fetched content"
                    }
                },
                "required": ["url", "prompt"]
            }
        ),
        types.Tool(
            name="web_search",
            description=description,
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (minimum 2 characters)"
                    },
                    "allowed_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of domains to include in results"
                    },
                    "blocked_domains": {
                        "type": "array", 
                        "items": {"type": "string"},
                        "description": "Optional list of domains to exclude from results"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
        
    try:
        if name == "web_fetch":
            url = arguments.get("url")
            prompt = arguments.get("prompt")
            
            if not url or not prompt:
                raise ValueError("Both 'url' and 'prompt' arguments are required")
                
            result = web_ops.web_fetch(url, prompt)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "web_search":
            query = arguments.get("query")
            allowed_domains = arguments.get("allowed_domains")
            blocked_domains = arguments.get("blocked_domains")
            
            if not query:
                raise ValueError("'query' argument is required")
                
            results = web_ops.web_search(query, allowed_domains, blocked_domains)
            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the server."""
    # Log server capabilities on startup
    if HAS_PERPLEXITY:
        logger.info("Starting Web Operations MCP Server with Perplexity API for enhanced search")
    else:
        logger.info("Starting Web Operations MCP Server with DuckDuckGo fallback search (no API key set)")
    
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="web-ops-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())