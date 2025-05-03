import unittest
from unittest.mock import patch, mock_open
from coding_agent.tools.search_tools import grep_search
from coding_agent.tools.search_tools import _glob_to_regex


class TestGrepSearch(unittest.TestCase):
    def setUp(self):
        self.sample_content = "line1\nTest Line\nanother line\n"
        self.multiple_matches = ["Test Line\n"] * 100  # simulate >50 matches

    # @patch('os.walk')
    # @patch('builtins.open', new_callable=mock_open)
    # def test_grep_search_basic(self, mock_file, mock_walk):
    #     mock_walk.return_value = [('.', [], ['file.py'])]
    #     # Simulate file iteration
    #     mock_file.return_value.__iter__.return_value = self.sample_content.splitlines(keepends=True)
    #     results, success = grep_search("Test")
    #     self.assertTrue(success)
    #     self.assertEqual(len(results), 1)
    #     self.assertEqual(results[0]["line_number"], 2)
    #     self.assertEqual(results[0]["content"], "Test Line")
    #     self.assertEqual(results[0]["file"], "./file.py")
    #
    # @patch('os.walk')
    # @patch('builtins.open', new_callable=mock_open)
    # def test_grep_search_case_insensitive(self, mock_file, mock_walk):
    #     mock_walk.return_value = [('.', [], ['file.py'])]
    #     mock_file.return_value.__iter__.return_value = self.sample_content.splitlines(keepends=True)
    #     results, success = grep_search("test", case_sensitive=False)
    #     self.assertTrue(success)
    #     self.assertEqual(len(results), 1)
    #     self.assertEqual(results[0]["content"], "Test Line")

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    def test_grep_search_include_pattern(self, mock_file, mock_walk):
        mock_walk.return_value = [('.', [], ['file1.py', 'file2.txt', 'skip.pyc'])]
        mock_file.return_value.readlines.return_value = ["Test Line"]
        results, success = grep_search("Test", include_pattern="*.py")
        self.assertTrue(success)
        # Expect only the .py file matches.
        for match in results:
            self.assertTrue(match["file"].endswith(".py"))

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    def test_grep_search_exclude_pattern(self, mock_file, mock_walk):
        mock_walk.return_value = [('.', [], ['file.py', 'skip.pyc'])]
        mock_file.return_value.readlines.return_value = ["Test Line"]
        results, success = grep_search("Test", exclude_pattern="*.pyc")
        self.assertTrue(success)
        # Only non-excluded file should match.
        for match in results:
            self.assertFalse(match["file"].endswith(".pyc"))

    @patch('os.walk')
    def test_grep_search_invalid_regex(self, mock_walk):
        results, success = grep_search("[invalid)")
        self.assertFalse(success)
        self.assertEqual(len(results), 0)

    @patch('os.walk')
    @patch('builtins.open')
    def test_grep_search_unreadable_file(self, mock_open_func, mock_walk):
        mock_walk.return_value = [('.', [], ['file.py'])]
        mock_open_func.side_effect = IOError("Unable to open file")
        results, success = grep_search("Test")
        self.assertTrue(success)
        self.assertEqual(len(results), 0)

    # @patch('os.walk')
    # @patch('builtins.open', new_callable=mock_open)
    # def test_grep_search_result_limit(self, mock_file, mock_walk):
    #     mock_walk.return_value = [('.', [], ['file.py'])]
    #     # Simulate a file with more than 50 matching lines.
    #     mock_file.return_value.__iter__.return_value = self.multiple_matches
    #     results, success = grep_search("Test")
    #     self.assertTrue(success)
    #     self.assertEqual(len(results), 50)


class TestGlobToRegex(unittest.TestCase):
    def test_glob_to_regex_basic(self):
        patterns = _glob_to_regex("*.py")
        self.assertEqual(len(patterns), 1)
        self.assertTrue(patterns[0].match("example.py"))
        self.assertFalse(patterns[0].match("example.txt"))

    def test_glob_to_regex_multiple(self):
        patterns = _glob_to_regex("*.py,*.txt")
        self.assertEqual(len(patterns), 2)
        self.assertTrue(any(p.match("test.py") for p in patterns))
        self.assertTrue(any(p.match("test.txt") for p in patterns))

    def test_glob_to_regex_complex(self):
        patterns = _glob_to_regex("test?.py,*.txt")
        self.assertEqual(len(patterns), 2)
        # test? should match test1.py but not test10.py.
        self.assertTrue(patterns[0].match("test1.py"))
        self.assertFalse(patterns[0].match("test10.py"))
        self.assertTrue(patterns[1].match("file.txt"))

    def test_glob_to_regex_invalid(self):
        patterns = _glob_to_regex("[invalid)")
        self.assertEqual(len(patterns), 0)

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()