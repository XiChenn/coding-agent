import unittest
from unittest.mock import patch, MagicMock
from coding_agent.nodes.file_nodes import (
    ReadFileAction, GrepSearchAction, ListDirAction, DeleteFileAction
)

class TestReadFileAction(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "working_dir": "/test/path",
            "history": [
                {
                    "params": {
                        "target_file": "test.py"
                    },
                    "reason": "Read test file"
                }
            ]
        }

    def test_prep(self):
        node = ReadFileAction()
        file_path = node.prep(self.shared_data)
        self.assertEqual(file_path, "/test/path/test.py")

    def test_prep_no_history(self):
        node = ReadFileAction()
        with self.assertRaises(ValueError):
            node.prep({})

    def test_prep_no_target_file(self):
        node = ReadFileAction()
        with self.assertRaises(ValueError):
            node.prep({"history": [{"params": {}}]})

    @patch("coding_agent.nodes.file_nodes.read_file")
    def test_exec(self, mock_read_file):
        mock_read_file.return_value = ("file content", True)
        node = ReadFileAction()
        content, success = node.exec("/test/path/test.py")
        self.assertEqual(content, "file content")
        self.assertTrue(success)

    def test_post(self):
        node = ReadFileAction()
        shared = {"history": [{}]}
        node.post(shared, "/test/path/test.py", ("file content", True))
        self.assertEqual(shared["history"][0]["result"]["content"], "file content")
        self.assertTrue(shared["history"][0]["result"]["success"])


class TestGrepSearchAction(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "working_dir": "/test/path",
            "history": [
                {
                    "params": {
                        "query": "test",
                        "case_sensitive": True,
                        "include_pattern": "*.py",
                        "exclude_pattern": "*.pyc"
                    },
                    "reason": "Search for test"
                }
            ]
        }

    def test_prep(self):
        node = GrepSearchAction()
        params = node.prep(self.shared_data)
        self.assertEqual(params["query"], "test")
        self.assertTrue(params["case_sensitive"])
        self.assertEqual(params["include_pattern"], "*.py")
        self.assertEqual(params["exclude_pattern"], "*.pyc")
        self.assertEqual(params["working_dir"], "/test/path")

    def test_prep_no_history(self):
        node = GrepSearchAction()
        with self.assertRaises(ValueError):
            node.prep({})

    def test_prep_no_query(self):
        node = GrepSearchAction()
        with self.assertRaises(ValueError):
            node.prep({"history": [{"params": {}}]})

    @patch("coding_agent.nodes.file_nodes.grep_search")
    def test_exec(self, mock_grep_search):
        matches = [{"file": "test.py", "line": 1, "content": "test"}]
        mock_grep_search.return_value = (matches, True)
        node = GrepSearchAction()
        result, success = node.exec({
            "query": "test",
            "case_sensitive": True,
            "working_dir": "/test/path"
        })
        self.assertEqual(result, matches)
        self.assertTrue(success)

    def test_post(self):
        node = GrepSearchAction()
        shared = {"history": [{}]}
        matches = [{"file": "test.py", "line": 1, "content": "test"}]
        node.post(shared, {}, (matches, True))
        self.assertEqual(shared["history"][0]["result"]["matches"], matches)
        self.assertTrue(shared["history"][0]["result"]["success"])


class TestListDirAction(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "working_dir": "/test/path",
            "history": [
                {
                    "params": {
                        "relative_workspace_path": "src"
                    },
                    "reason": "List directory"
                }
            ]
        }

    def test_prep(self):
        node = ListDirAction()
        path = node.prep(self.shared_data)
        self.assertEqual(path, "/test/path/src")

    def test_prep_default_path(self):
        node = ListDirAction()
        shared = {"working_dir": "/test/path", "history": [{"params": {}}]}
        path = node.prep(shared)
        self.assertEqual(path, "/test/path/.")

    @patch("coding_agent.nodes.file_nodes.list_dir")
    def test_exec(self, mock_list_dir):
        mock_list_dir.return_value = (True, "dir_tree")
        node = ListDirAction()
        success, tree_str = node.exec("/test/path")
        self.assertTrue(success)
        self.assertEqual(tree_str, "dir_tree")

    def test_post(self):
        node = ListDirAction()
        shared = {"history": [{}]}
        node.post(shared, "/test/path", (True, "dir_tree"))
        self.assertTrue(shared["history"][0]["result"]["success"])
        self.assertEqual(shared["history"][0]["result"]["tree_visualization"], "dir_tree")


class TestDeleteFileAction(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "working_dir": "/test/path",
            "history": [
                {
                    "params": {
                        "target_file": "test.py"
                    },
                    "reason": "Delete test file"
                }
            ]
        }

    def test_prep(self):
        node = DeleteFileAction()
        file_path = node.prep(self.shared_data)
        self.assertEqual(file_path, "/test/path/test.py")

    def test_prep_no_target_file(self):
        node = DeleteFileAction()
        with self.assertRaises(ValueError):
            node.prep({"history": [{"params": {}}]})

    @patch("coding_agent.nodes.file_nodes.delete_file")
    def test_exec(self, mock_delete_file):
        mock_delete_file.return_value = (True, "File deleted")
        node = DeleteFileAction()
        success, message = node.exec("/test/path/test.py")
        self.assertTrue(success)
        self.assertEqual(message, "File deleted")

    def test_post(self):
        node = DeleteFileAction()
        shared = {"history": [{}]}
        node.post(shared, "/test/path/test.py", (True, "File deleted"))
        self.assertTrue(shared["history"][0]["result"]["success"])
        self.assertEqual(shared["history"][0]["result"]["message"], "File deleted")


if __name__ == "__main__":
    unittest.main()