import unittest
from unittest.mock import patch, mock_open
import os
from coding_agent.tools.file_tools import (
    read_file, insert_file, delete_file, remove_file, replace_file, list_dir
)

class TestFileTools(unittest.TestCase):
    def setUp(self):
        self.test_content = "line1\nline2\nline3\n"

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_read_file_entire(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["line1\n", "line2\n", "line3\n"]
        content, success = read_file("test.txt")
        self.assertTrue(success)
        self.assertEqual(content, "1: line1\n2: line2\n3: line3\n")

    @patch("os.path.exists")
    def test_read_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        content, success = read_file("nonexistent.txt")
        self.assertFalse(success)
        self.assertTrue("does not exist" in content)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_read_file_range(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["line1\n", "line2\n", "line3\n"]
        content, success = read_file("test.txt", 1, 2)
        self.assertTrue(success)
        self.assertEqual(content, "1: line1\n2: line2\n")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_insert_file_new(self, mock_file, mock_exists):
        mock_exists.return_value = False
        result, success = insert_file("test.txt", "content")
        self.assertTrue(success)
        self.assertTrue("created" in result)
        mock_file.assert_called_once_with("test.txt", "w", encoding="utf-8")

    @patch("os.path.exists")
    @patch("os.remove")
    @patch("builtins.open", new_callable=mock_open)
    def test_insert_file_replace(self, mock_file, mock_remove, mock_exists):
        mock_exists.return_value = True
        result, success = insert_file("test.txt", "content")
        self.assertTrue(success)
        self.assertTrue("replaced" in result)
        mock_remove.assert_called_once_with("test.txt")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_insert_file_specific_line(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["line1\n", "line2\n"]
        result, success = insert_file("test.txt", "content\n", 2)
        self.assertTrue(success)
        self.assertTrue("inserted into" in result)

    @patch("os.path.exists")
    @patch("os.remove")
    def test_delete_file(self, mock_remove, mock_exists):
        mock_exists.return_value = True
        result, success = delete_file("test.txt")
        self.assertTrue(success)
        self.assertTrue("Successfully deleted" in result)
        mock_remove.assert_called_once_with("test.txt")

    @patch("os.path.exists")
    def test_delete_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        result, success = delete_file("nonexistent.txt")
        self.assertFalse(success)
        self.assertTrue("does not exist" in result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_remove_file_range(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["1\n", "2\n", "3\n"]
        result, success = remove_file("test.txt", 1, 2)
        self.assertTrue(success)
        self.assertTrue("Successfully removed" in result)

    @patch("os.path.exists")
    def test_remove_file_no_range(self, mock_exists):
        mock_exists.return_value = True
        result, success = remove_file("test.txt")
        self.assertFalse(success)
        self.assertTrue("must be specified" in result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_replace_file(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["1\n", "2\n", "3\n"]
        result, success = replace_file("test.txt", 1, 2, "new content\n")
        self.assertTrue(success)
        self.assertTrue("Successfully replaced" in result)

    @patch("os.path.exists")
    def test_replace_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        result, success = replace_file("test.txt", 1, 2, "content")
        self.assertFalse(success)
        self.assertTrue("does not exist" in result)

    @patch("os.path.exists")
    @patch("os.path.isdir")
    @patch("os.listdir")
    @patch("os.path.getsize")
    def test_list_dir(self, mock_size, mock_listdir, mock_isdir, mock_exists):
        mock_exists.return_value = True
        # First return True for the input path check, then handle subsequent checks
        mock_isdir.side_effect = lambda x: True if x == "." else x.endswith("dir")
        mock_listdir.return_value = ["file1.txt", "testdir"]
        mock_size.return_value = 1024

        success, tree = list_dir(".")
        self.assertTrue(success)
        self.assertTrue("file1.txt" in tree)
        self.assertTrue("testdir" in tree)

    @patch("os.path.exists")
    def test_list_dir_not_exists(self, mock_exists):
        mock_exists.return_value = False
        success, tree = list_dir("nonexistent")
        self.assertFalse(success)
        self.assertEqual(tree, "")


class TestFileToolsValidation(unittest.TestCase):
    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_read_file_invalid_range(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["line1\n", "line2\n"]

        # Test start line < 1
        result, success = read_file("test.txt", -1, 1)
        self.assertFalse(success)
        self.assertTrue("Error: start_line_one_indexed must be at least 1" in result)

        # Test end line < start line
        result, success = read_file("test.txt", 2, 1)
        self.assertFalse(success)
        self.assertTrue("Error: end_line_one_indexed_inclusive must be >= start_line_one_indexed" in result)

    def test_insert_file_invalid_line(self):
        result, success = insert_file("test.txt", "content", -1)
        self.assertFalse(success)
        self.assertTrue("must be at least 1" in result)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_remove_file_invalid_range(self, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_file.return_value.readlines.return_value = ["line1\n", "line2\n"]

        # Test start line < 1
        result, success = remove_file("test.txt", -1, 1)
        self.assertFalse(success)
        self.assertTrue("Error: start_line must be at least 1" in result)

        # Test end line < start line
        result, success = remove_file("test.txt", 2, 1)
        self.assertFalse(success)
        self.assertTrue("Error: start_line must be less than or equal to end_line" in result)

    @patch("os.path.exists")
    def test_replace_file_invalid_range(self, mock_exists):
        mock_exists.return_value = True
        result, success = replace_file("test.txt", -1, 1, "content")
        self.assertFalse(success)
        self.assertTrue("must be at least 1" in result)

        result, success = replace_file("test.txt", 2, 1, "content")
        self.assertFalse(success)
        self.assertTrue("must be less than or equal" in result)


if __name__ == "__main__":
    unittest.main()