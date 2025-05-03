import unittest
from unittest.mock import patch, MagicMock
from coding_agent.nodes.edit_nodes import ReadTargetFileNode, AnalyzeAndPlanNode, ApplyChangesNode

class TestReadTargetFileNode(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "working_dir": "/test/path",
            "history": [
                {
                    "params": {
                        "target_file": "test.py"
                    }
                }
            ]
        }

    def test_prep(self):
        node = ReadTargetFileNode()
        file_path = node.prep(self.shared_data)
        self.assertEqual(file_path, "/test/path/test.py")

    def test_prep_no_history(self):
        node = ReadTargetFileNode()
        with self.assertRaises(ValueError):
            node.prep({})

    @patch("coding_agent.nodes.edit_nodes.read_file")
    def test_exec(self, mock_read_file):
        mock_read_file.return_value = ("file content", True)
        node = ReadTargetFileNode()
        content, success = node.exec("/test/path/test.py")
        self.assertEqual(content, "file content")
        self.assertTrue(success)

    def test_post(self):
        node = ReadTargetFileNode()
        shared = {"history": [{"params": {}}]}
        node.post(shared, "/test/path/test.py", ("file content", True))
        self.assertEqual(shared["history"][0]["file_content"], "file content")


class TestAnalyzeAndPlanNode(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "history": [
                {
                    "file_content": "def test():\n    pass\n",
                    "params": {
                        "instructions": "Add docstring",
                        "code_edit": "Add documentation"
                    }
                }
            ]
        }

    def test_prep(self):
        node = AnalyzeAndPlanNode()
        params = node.prep(self.shared_data)
        self.assertEqual(params["file_content"], "def test():\n    pass\n")
        self.assertEqual(params["instructions"], "Add docstring")
        self.assertEqual(params["code_edit"], "Add documentation")

    # def test_prep_missing_params(self):
    #     node = AnalyzeAndPlanNode()
    #     with self.assertRaises(ValueError):
    #         node.prep({"history": [{"file_content": "test"}]})

    def test_prep_missing_instructions(self):
        node = AnalyzeAndPlanNode()
        with self.assertRaises(ValueError):
            node.prep({"history": [{"file_content": "test", "params": {"code_edit": "test"}}]})

    @patch("coding_agent.nodes.edit_nodes.call_llm")
    def test_exec(self, mock_call_llm):
        mock_call_llm.return_value = """```yaml
reasoning: Add docstring for better documentation
operations:
  - start_line: 1
    end_line: 1
    replacement: 'def test():\n    \"""Test function.\"""'
```"""
        node = AnalyzeAndPlanNode()
        params = node.prep(self.shared_data)
        result = node.exec(params)
        self.assertEqual(result["reasoning"], "Add docstring for better documentation")
        self.assertEqual(len(result["operations"]), 1)

    def test_post(self):
        node = AnalyzeAndPlanNode()
        shared = {}
        exec_res = {
            "reasoning": "Add docstring",
            "operations": [{"start_line": 1, "end_line": 1, "replacement": "new code"}]
        }
        node.post(shared, {}, exec_res)
        self.assertEqual(shared["edit_reasoning"], "Add docstring")
        self.assertEqual(len(shared["edit_operations"]), 1)


class TestApplyChangesNode(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "working_dir": "/test/path",
            "edit_operations": [
                {
                    "start_line": 2,
                    "end_line": 2,
                    "replacement": "    return True"
                },
                {
                    "start_line": 1,
                    "end_line": 1,
                    "replacement": "def test():"
                }
            ],
            "edit_reasoning": "Add return statement",
            "history": [{"params": {"target_file": "test.py"}}]
        }

    def test_prep(self):
        node = ApplyChangesNode()
        operations = node.prep(self.shared_data)
        self.assertEqual(len(operations), 2)
        self.assertEqual(operations[0]["start_line"], 2)
        self.assertEqual(operations[0]["target_file"], "/test/path/test.py")

    def test_prep_no_operations(self):
        node = ApplyChangesNode()
        operations = node.prep({})
        self.assertEqual(operations, [])

    @patch("coding_agent.nodes.edit_nodes.replace_file")
    def test_exec(self, mock_replace_file):
        mock_replace_file.return_value = (True, "Success")
        node = ApplyChangesNode()
        success, message = node.exec({
            "target_file": "/test/path/test.py",
            "start_line": 1,
            "end_line": 1,
            "replacement": "def test():"
        })
        self.assertTrue(success)
        self.assertEqual(message, "Success")

    def test_post(self):
        node = ApplyChangesNode()
        shared = {"history": [{}]}
        exec_res_list = [(True, "Success"), (True, "Success")]
        node.post(shared, [], exec_res_list)
        result = shared["history"][0]["result"]
        self.assertTrue(result["success"])
        self.assertEqual(result["operations"], 2)
        self.assertEqual(len(result["details"]), 2)


if __name__ == "__main__":
    unittest.main()