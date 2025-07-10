import requests
import hashlib
from urllib.parse import urlparse
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

try:
    import html2text
    HAS_HTML2TEXT = True
except ImportError:
    HAS_HTML2TEXT = False


class WebOperations:
    """Web operations tool class for Claude Code tools implementation."""
    
    def __init__(self):
        """Initialize the web operations tool."""
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
        Fetch content from a URL and process it with AI.
        
        Args:
            url: The URL to fetch content from
            prompt: The prompt to run on the fetched content
            
        Returns:
            Dictionary containing:
                - content: The processed/analyzed content
                - url: The final URL (after redirects)
                - cached: Whether the result was from cache
                - redirect: Information about redirects if any occurred
                
        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If fetching fails
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
                    'User-Agent': 'Mozilla/5.0 (compatible; ClaudeCode/1.0)'
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
                import re
                text = re.sub('<[^<]+?>', '', response.text)
                markdown_content = text
            else:
                # For non-HTML content, use as-is
                markdown_content = response.text
                
            # Process with AI (simulated - in real implementation this would call an AI model)
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
        Search the web and return formatted search results.
        
        Args:
            query: The search query
            allowed_domains: Optional list of domains to include
            blocked_domains: Optional list of domains to block
            
        Returns:
            List of search results, each containing:
                - title: Result title
                - url: Result URL
                - snippet: Brief description
                - domain: Domain of the result
                
        Note: This is a simulated implementation. Real implementation would
              use an actual search API.
        """
        if len(query) < 2:
            raise ValueError("Query must be at least 2 characters long")
            
        # Simulate search results (in real implementation, this would call a search API)
        mock_results = [
            {
                'title': f'Search result for "{query}" - Example 1',
                'url': 'https://example.com/result1',
                'snippet': f'This is a relevant result about {query}...',
                'domain': 'example.com'
            },
            {
                'title': f'Documentation: {query}',
                'url': 'https://docs.example.com/topic',
                'snippet': f'Official documentation covering {query} in detail...',
                'domain': 'docs.example.com'
            },
            {
                'title': f'Tutorial: Understanding {query}',
                'url': 'https://tutorial.org/guide',
                'snippet': f'A comprehensive guide to {query} with examples...',
                'domain': 'tutorial.org'
            }
        ]
        
        # Apply domain filtering
        filtered_results = []
        for result in mock_results:
            domain = result['domain']
            
            # Check blocked domains
            if blocked_domains and domain in blocked_domains:
                continue
                
            # Check allowed domains (if specified, only include those)
            if allowed_domains and domain not in allowed_domains:
                continue
                
            filtered_results.append(result)
            
        return filtered_results
        
    def _process_with_ai(self, content: str, prompt: str) -> str:
        """
        Process content with AI based on the prompt.
        
        This is a placeholder for the actual AI processing.
        In a real implementation, this would call an AI model.
        
        Args:
            content: The content to process
            prompt: The prompt to use for processing
            
        Returns:
            Processed content based on the prompt
        """
        # Simulate AI processing
        # In real implementation, this would call an AI model API
        return f"AI Analysis based on prompt: '{prompt}'\\n\\nContent Summary:\\n{content[:500]}..."
        
    def _get_cache_key(self, url: str, prompt: str) -> str:
        """Generate a cache key from URL and prompt."""
        combined = f"{url}|{prompt}"
        return hashlib.md5(combined.encode()).hexdigest()
        
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache if not expired."""
        if cache_key in self._fetch_cache:
            result, timestamp = self._fetch_cache[cache_key]
            if datetime.now() - timestamp < self._cache_duration:
                return result.copy()  # Return a copy to prevent modification
            else:
                # Remove expired entry
                del self._fetch_cache[cache_key]
        return None
        
    def _add_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Add item to cache with current timestamp."""
        self._fetch_cache[cache_key] = (result.copy(), datetime.now())
        
        # Clean up old entries (simple cleanup strategy)
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