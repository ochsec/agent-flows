import unittest
import tempfile
import os
import shutil
from tools.file_operations import FileOperations


class TestFileOperations(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.file_ops = FileOperations()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_read_basic(self):
        """Test basic file reading."""
        content = "Line 1\nLine 2\nLine 3"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        result = self.file_ops.read(self.test_file)
        self.assertIn("     1\tLine 1", result)
        self.assertIn("     2\tLine 2", result)
        self.assertIn("     3\tLine 3", result)
        
    def test_read_with_offset_and_limit(self):
        """Test reading with offset and limit."""
        content = "\n".join([f"Line {i}" for i in range(1, 11)])
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        result = self.file_ops.read(self.test_file, offset=3, limit=2)
        self.assertIn("     3\tLine 3", result)
        self.assertIn("     4\tLine 4", result)
        self.assertNotIn("Line 2", result)
        self.assertNotIn("Line 5", result)
        
    def test_read_long_lines_truncation(self):
        """Test that long lines are truncated."""
        long_line = "x" * 3000
        with open(self.test_file, 'w') as f:
            f.write(long_line)
            
        result = self.file_ops.read(self.test_file)
        self.assertIn("x" * 2000 + "...", result)
        self.assertEqual(len(result.split('\t')[1]), 2003)  # 2000 chars + "..."
        
    def test_read_non_absolute_path_error(self):
        """Test that relative paths raise ValueError."""
        with self.assertRaises(ValueError) as cm:
            self.file_ops.read("relative/path.txt")
        self.assertIn("must be absolute", str(cm.exception))
        
    def test_read_missing_file_error(self):
        """Test that missing files raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.file_ops.read("/nonexistent/file.txt")
            
    def test_edit_basic(self):
        """Test basic file editing."""
        content = "Hello World\nThis is a test"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        self.file_ops.edit(self.test_file, "World", "Python")
        
        with open(self.test_file, 'r') as f:
            new_content = f.read()
        self.assertEqual(new_content, "Hello Python\nThis is a test")
        
    def test_edit_replace_all(self):
        """Test editing with replace_all."""
        content = "foo bar foo baz foo"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        self.file_ops.edit(self.test_file, "foo", "XXX", replace_all=True)
        
        with open(self.test_file, 'r') as f:
            new_content = f.read()
        self.assertEqual(new_content, "XXX bar XXX baz XXX")
        
    def test_edit_non_unique_error(self):
        """Test that non-unique strings raise error when replace_all=False."""
        content = "foo bar foo"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        with self.assertRaises(ValueError) as cm:
            self.file_ops.edit(self.test_file, "foo", "bar")
        self.assertIn("appears 2 times", str(cm.exception))
        
    def test_edit_string_not_found_error(self):
        """Test that missing strings raise error."""
        content = "Hello World"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        with self.assertRaises(ValueError) as cm:
            self.file_ops.edit(self.test_file, "Python", "Java")
        self.assertIn("not found", str(cm.exception))
        
    def test_edit_same_strings_error(self):
        """Test that identical old and new strings raise error."""
        content = "Hello World"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        with self.assertRaises(ValueError) as cm:
            self.file_ops.edit(self.test_file, "Hello", "Hello")
        self.assertIn("must be different", str(cm.exception))
        
    def test_multi_edit_basic(self):
        """Test multiple edits in sequence."""
        content = "Hello World\nThis is Python\nPython is great"
        with open(self.test_file, 'w') as f:
            f.write(content)
            
        edits = [
            {"old_string": "World", "new_string": "Universe"},
            {"old_string": "Python", "new_string": "Claude", "replace_all": True},
            {"old_string": "is great", "new_string": "is awesome"}
        ]
        
        self.file_ops.multi_edit(self.test_file, edits)
        
        with open(self.test_file, 'r') as f:
            new_content = f.read()
        self.assertEqual(new_content, "Hello Universe\nThis is Claude\nClaude is awesome")
        
    def test_multi_edit_empty_edits_error(self):
        """Test that empty edits list raises error."""
        with open(self.test_file, 'w') as f:
            f.write("content")
            
        with self.assertRaises(ValueError) as cm:
            self.file_ops.multi_edit(self.test_file, [])
        self.assertIn("At least one edit", str(cm.exception))
        
    def test_write_basic(self):
        """Test basic file writing."""
        content = "New file content"
        self.file_ops.write(self.test_file, content)
        
        with open(self.test_file, 'r') as f:
            written_content = f.read()
        self.assertEqual(written_content, content)
        
    def test_write_creates_parent_dirs(self):
        """Test that write creates parent directories."""
        nested_file = os.path.join(self.test_dir, "sub", "dir", "file.txt")
        self.file_ops.write(nested_file, "content")
        
        self.assertTrue(os.path.exists(nested_file))
        with open(nested_file, 'r') as f:
            self.assertEqual(f.read(), "content")
            
    def test_ls_basic(self):
        """Test basic directory listing."""
        # Create test files and directories
        os.mkdir(os.path.join(self.test_dir, "subdir"))
        with open(os.path.join(self.test_dir, "file1.txt"), 'w') as f:
            f.write("content")
        with open(os.path.join(self.test_dir, "file2.py"), 'w') as f:
            f.write("content")
            
        result = self.file_ops.ls(self.test_dir)
        
        # Directories should come first with trailing slash
        self.assertEqual(result, ["subdir/", "file1.txt", "file2.py"])
        
    def test_ls_with_ignore_patterns(self):
        """Test directory listing with ignore patterns."""
        # Create test files
        with open(os.path.join(self.test_dir, "file.txt"), 'w') as f:
            f.write("content")
        with open(os.path.join(self.test_dir, "file.py"), 'w') as f:
            f.write("content")
        with open(os.path.join(self.test_dir, ".hidden"), 'w') as f:
            f.write("content")
            
        result = self.file_ops.ls(self.test_dir, ignore=["*.py", ".*"])
        
        self.assertEqual(result, ["file.txt"])
        
    def test_ls_not_directory_error(self):
        """Test that listing a file raises NotADirectoryError."""
        with open(self.test_file, 'w') as f:
            f.write("content")
            
        with self.assertRaises(NotADirectoryError):
            self.file_ops.ls(self.test_file)
            
    def test_ls_missing_directory_error(self):
        """Test that listing non-existent directory raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.file_ops.ls("/nonexistent/directory")


if __name__ == '__main__':
    unittest.main()