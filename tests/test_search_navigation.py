import unittest
import tempfile
import os
import shutil
import time
import re
from tools.search_navigation import SearchNavigation


class TestSearchNavigation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.search_nav = SearchNavigation()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test directory structure
        self.subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.subdir)
        
        # Create test files with different extensions
        self.test_files = {
            "test1.py": "def hello():\n    print('Hello World')\n    return 'test'",
            "test2.js": "function hello() {\n    console.log('Hello World');\n    return 'test';\n}",
            "test3.txt": "This is a test file\nwith multiple lines\nand test content",
            "subdir/nested.py": "class TestClass:\n    def method(self):\n        return 'nested test'",
            "README.md": "# Test Project\n\nThis is a test project for testing purposes."
        }
        
        # Create files with slight delays to ensure different modification times
        for i, (filename, content) in enumerate(self.test_files.items()):
            filepath = os.path.join(self.test_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            # Add small delay to ensure different modification times
            time.sleep(0.01)
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_glob_basic_pattern(self):
        """Test basic glob pattern matching."""
        results = self.search_nav.glob("*.py", self.test_dir)
        
        # Should find Python files
        py_files = [f for f in results if f.endswith('.py')]
        self.assertEqual(len(py_files), 1)  # Only test1.py, not nested.py
        self.assertTrue(any('test1.py' in f for f in py_files))
        
    def test_glob_recursive_pattern(self):
        """Test recursive glob pattern matching."""
        results = self.search_nav.glob("**/*.py", self.test_dir)
        
        # Should find all Python files recursively
        py_files = [f for f in results if f.endswith('.py')]
        self.assertEqual(len(py_files), 2)  # test1.py and nested.py
        self.assertTrue(any('test1.py' in f for f in py_files))
        self.assertTrue(any('nested.py' in f for f in py_files))
        
    def test_glob_wildcard_pattern(self):
        """Test wildcard pattern matching."""
        results = self.search_nav.glob("test*", self.test_dir)
        
        # Should find files starting with 'test'
        self.assertGreater(len(results), 0)
        for result in results:
            filename = os.path.basename(result)
            self.assertTrue(filename.startswith('test'))
            
    def test_glob_specific_extension(self):
        """Test matching specific file extensions."""
        results = self.search_nav.glob("*.js", self.test_dir)
        
        # Should find JavaScript files
        js_files = [f for f in results if f.endswith('.js')]
        self.assertEqual(len(js_files), 1)
        self.assertTrue(any('test2.js' in f for f in js_files))
        
    def test_glob_modification_time_sorting(self):
        """Test that results are sorted by modification time."""
        results = self.search_nav.glob("test*", self.test_dir)
        
        # Should be sorted by modification time (newest first)
        if len(results) > 1:
            for i in range(len(results) - 1):
                mtime1 = os.path.getmtime(results[i])
                mtime2 = os.path.getmtime(results[i + 1])
                self.assertGreaterEqual(mtime1, mtime2)
                
    def test_glob_nonexistent_path(self):
        """Test glob with non-existent path."""
        with self.assertRaises(ValueError) as cm:
            self.search_nav.glob("*.py", "/nonexistent/path")
        self.assertIn("does not exist", str(cm.exception))
        
    def test_glob_default_path(self):
        """Test glob with default path (current directory)."""
        old_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            results = self.search_nav.glob("*.py")
            self.assertGreater(len(results), 0)
        finally:
            os.chdir(old_cwd)
            
    def test_grep_basic_pattern(self):
        """Test basic grep pattern matching."""
        results = self.search_nav.grep("hello", path=self.test_dir)
        
        # Should find files containing 'hello'
        self.assertGreater(len(results), 0)
        
        # Verify the content actually contains the pattern
        for result in results:
            with open(result, 'r') as f:
                content = f.read()
                self.assertIn('hello', content.lower())
                
    def test_grep_regex_pattern(self):
        """Test grep with regex patterns."""
        results = self.search_nav.grep(r"def\s+\w+", path=self.test_dir)
        
        # Should find files with function definitions
        self.assertGreater(len(results), 0)
        
        # Verify matches
        for result in results:
            with open(result, 'r') as f:
                content = f.read()
                self.assertTrue(re.search(r"def\s+\w+", content))
                
    def test_grep_with_include_pattern(self):
        """Test grep with file include pattern."""
        results = self.search_nav.grep("test", include="*.py", path=self.test_dir)
        
        # Should only search Python files
        for result in results:
            self.assertTrue(result.endswith('.py'))
            
    def test_grep_case_sensitive(self):
        """Test grep case sensitivity."""
        results_lower = self.search_nav.grep("hello", path=self.test_dir)
        results_upper = self.search_nav.grep("HELLO", path=self.test_dir)
        
        # Should be case sensitive
        self.assertGreater(len(results_lower), len(results_upper))
        
    def test_grep_invalid_regex(self):
        """Test grep with invalid regex pattern."""
        with self.assertRaises(re.error):
            self.search_nav.grep("[invalid", path=self.test_dir)
            
    def test_grep_nonexistent_path(self):
        """Test grep with non-existent path."""
        with self.assertRaises(ValueError) as cm:
            self.search_nav.grep("pattern", path="/nonexistent/path")
        self.assertIn("does not exist", str(cm.exception))
        
    def test_grep_modification_time_sorting(self):
        """Test that grep results are sorted by modification time."""
        results = self.search_nav.grep("test", path=self.test_dir)
        
        # Should be sorted by modification time (newest first)
        if len(results) > 1:
            for i in range(len(results) - 1):
                mtime1 = os.path.getmtime(results[i])
                mtime2 = os.path.getmtime(results[i + 1])
                self.assertGreaterEqual(mtime1, mtime2)
                
    def test_grep_complex_include_pattern(self):
        """Test grep with complex include pattern."""
        results = self.search_nav.grep("test", include="*.{py,js}", path=self.test_dir)
        
        # Should find files with .py or .js extensions
        for result in results:
            self.assertTrue(result.endswith('.py') or result.endswith('.js'))


if __name__ == '__main__':
    unittest.main()