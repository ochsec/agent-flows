import unittest
from unittest.mock import patch, Mock, MagicMock
import time
from datetime import datetime, timedelta
from tools.web_operations import WebOperations
import requests


class TestWebOperations(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.web_ops = WebOperations()
        
    def test_web_fetch_invalid_url(self):
        """Test that invalid URLs raise ValueError."""
        with self.assertRaises(ValueError):
            self.web_ops.web_fetch("not-a-url", "test prompt")
            
        with self.assertRaises(ValueError):
            self.web_ops.web_fetch("://missing-scheme.com", "test prompt")
            
    @patch('requests.get')
    def test_web_fetch_basic(self, mock_get):
        """Test basic web fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.text = "<html><body><h1>Test Page</h1><p>Content</p></body></html>"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response
        
        result = self.web_ops.web_fetch("https://example.com", "Summarize this page")
        
        self.assertIn('content', result)
        self.assertEqual(result['url'], "https://example.com")
        self.assertFalse(result['cached'])
        mock_get.assert_called_once()
        
    @patch('requests.get')
    def test_web_fetch_http_upgrade(self, mock_get):
        """Test that HTTP URLs are upgraded to HTTPS."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.text = "Test content"
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_get.return_value = mock_response
        
        self.web_ops.web_fetch("http://example.com", "Test")
        
        # Check that the request was made with https
        args, kwargs = mock_get.call_args
        self.assertTrue(args[0].startswith("https://"))
        
    @patch('requests.get')
    def test_web_fetch_redirect_detection(self, mock_get):
        """Test detection of redirects to different hosts."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://different-host.com/page"
        mock_response.text = "Redirected content"
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_get.return_value = mock_response
        
        result = self.web_ops.web_fetch("https://example.com", "Test")
        
        self.assertIn('redirect', result)
        self.assertEqual(result['redirect']['original_url'], "https://example.com")
        self.assertEqual(result['redirect']['final_url'], "https://different-host.com/page")
        self.assertIn("example.com", result['redirect']['message'])
        self.assertIn("different-host.com", result['redirect']['message'])
        
    @patch('requests.get')
    def test_web_fetch_cache(self, mock_get):
        """Test caching mechanism."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.text = "Test content"
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_get.return_value = mock_response
        
        # First call - should hit the network
        result1 = self.web_ops.web_fetch("https://example.com", "Test prompt")
        self.assertFalse(result1['cached'])
        
        # Second call - should use cache
        result2 = self.web_ops.web_fetch("https://example.com", "Test prompt")
        self.assertTrue(result2['cached'])
        
        # Verify network was only called once
        mock_get.assert_called_once()
        
    @patch('requests.get')
    def test_web_fetch_cache_expiration(self, mock_get):
        """Test that cache expires after 15 minutes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.text = "Test content"
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_get.return_value = mock_response
        
        # First call
        self.web_ops.web_fetch("https://example.com", "Test")
        
        # Manually expire the cache by modifying the timestamp
        cache_key = list(self.web_ops._fetch_cache.keys())[0]
        result, _ = self.web_ops._fetch_cache[cache_key]
        expired_time = datetime.now() - timedelta(minutes=16)
        self.web_ops._fetch_cache[cache_key] = (result, expired_time)
        
        # Second call should hit network again
        result = self.web_ops.web_fetch("https://example.com", "Test")
        self.assertFalse(result['cached'])
        self.assertEqual(mock_get.call_count, 2)
        
    @patch('requests.get')
    def test_web_fetch_different_prompts_not_cached(self, mock_get):
        """Test that different prompts create different cache entries."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.text = "Test content"
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_get.return_value = mock_response
        
        # Same URL, different prompts
        self.web_ops.web_fetch("https://example.com", "Prompt 1")
        self.web_ops.web_fetch("https://example.com", "Prompt 2")
        
        # Should make two network calls
        self.assertEqual(mock_get.call_count, 2)
        
    @patch('requests.get')
    def test_web_fetch_html_to_markdown(self, mock_get):
        """Test HTML to markdown conversion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.text = """
        <html>
            <body>
                <h1>Title</h1>
                <p>This is a <strong>test</strong> paragraph.</p>
                <a href="https://link.com">Link</a>
            </body>
        </html>
        """
        mock_response.headers = {'Content-Type': 'text/html; charset=utf-8'}
        mock_get.return_value = mock_response
        
        result = self.web_ops.web_fetch("https://example.com", "Convert to markdown")
        
        # AI processing is mocked, but we can verify it was called
        self.assertIn('content', result)
        self.assertIn("AI Analysis", result['content'])
        
    @patch('requests.get')
    def test_web_fetch_request_error(self, mock_get):
        """Test handling of request errors."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        with self.assertRaises(requests.RequestException) as cm:
            self.web_ops.web_fetch("https://example.com", "Test")
        self.assertIn("Failed to fetch URL", str(cm.exception))
        
    def test_web_search_basic(self):
        """Test basic web search."""
        results = self.web_ops.web_search("python programming")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Check result structure
        for result in results:
            self.assertIn('title', result)
            self.assertIn('url', result)
            self.assertIn('snippet', result)
            self.assertIn('domain', result)
            self.assertIn("python programming", result['title'].lower())
            
    def test_web_search_query_validation(self):
        """Test that short queries are rejected."""
        with self.assertRaises(ValueError) as cm:
            self.web_ops.web_search("a")
        self.assertIn("at least 2 characters", str(cm.exception))
        
    def test_web_search_allowed_domains(self):
        """Test domain allow list filtering."""
        results = self.web_ops.web_search(
            "test query",
            allowed_domains=["example.com", "docs.example.com"]
        )
        
        for result in results:
            self.assertIn(result['domain'], ["example.com", "docs.example.com"])
            
    def test_web_search_blocked_domains(self):
        """Test domain block list filtering."""
        results = self.web_ops.web_search(
            "test query",
            blocked_domains=["example.com"]
        )
        
        for result in results:
            self.assertNotEqual(result['domain'], "example.com")
            
    def test_web_search_combined_filtering(self):
        """Test combined allow and block list filtering."""
        results = self.web_ops.web_search(
            "test query",
            allowed_domains=["example.com", "docs.example.com", "tutorial.org"],
            blocked_domains=["example.com"]
        )
        
        domains = [r['domain'] for r in results]
        self.assertNotIn("example.com", domains)
        self.assertIn("docs.example.com", domains)
        self.assertIn("tutorial.org", domains)
        
    def test_cache_cleanup(self):
        """Test that cache cleanup removes expired entries."""
        # Add some entries to cache with expired timestamps
        expired_time = datetime.now() - timedelta(minutes=20)
        current_time = datetime.now()
        
        self.web_ops._fetch_cache['expired1'] = ({}, expired_time)
        self.web_ops._fetch_cache['expired2'] = ({}, expired_time)
        self.web_ops._fetch_cache['current'] = ({}, current_time)
        
        # Trigger cleanup
        self.web_ops._cleanup_cache()
        
        # Check that expired entries are removed
        self.assertNotIn('expired1', self.web_ops._fetch_cache)
        self.assertNotIn('expired2', self.web_ops._fetch_cache)
        self.assertIn('current', self.web_ops._fetch_cache)


if __name__ == '__main__':
    unittest.main()