import unittest
from unittest.mock import patch
from coding_agent.nodes.response_nodes import FormatResponseNode

class TestFormatResponseNode(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "history": [
                {
                    "action": "read_file",
                    "params": {"target_file": "test.py"},
                    "reason": "Read file contents",
                    "result": {
                        "success": True,
                        "content": "def test():\n    pass"
                    }
                },
                {
                    "action": "list_dir",
                    "params": {"relative_workspace_path": "."},
                    "reason": "List directory contents",
                    "result": {
                        "success": True,
                        "tree_visualization": "test.py\nREADME.md"
                    }
                }
            ]
        }

    def test_prep(self):
        node = FormatResponseNode()
        history = node.prep(self.shared_data)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["action"], "read_file")
        self.assertEqual(history[1]["action"], "list_dir")

    def test_prep_no_history(self):
        node = FormatResponseNode()
        history = node.prep({})
        self.assertEqual(history, [])

    @patch("coding_agent.nodes.response_nodes.call_llm")
    @patch("coding_agent.nodes.response_nodes.format_history_summary")
    @patch("coding_agent.nodes.response_nodes.generate_response_formatting_prompt")
    def test_exec(self, mock_generate_prompt, mock_format_summary, mock_call_llm):
        mock_format_summary.return_value = "Action summary"
        mock_generate_prompt.return_value = "Formatted prompt"
        mock_call_llm.return_value = "Generated response"

        node = FormatResponseNode()
        response = node.exec(self.shared_data["history"])

        mock_format_summary.assert_called_once_with(self.shared_data["history"])
        mock_generate_prompt.assert_called_once_with("Action summary")
        mock_call_llm.assert_called_once_with("Formatted prompt")
        self.assertEqual(response, "Generated response")

    def test_exec_empty_history(self):
        node = FormatResponseNode()
        response = node.exec([])
        self.assertEqual(response, "No actions were performed.")

    def test_post(self):
        node = FormatResponseNode()
        shared = {}
        result = node.post(shared, [], "Generated response")
        self.assertEqual(result, "done")
        self.assertEqual(shared["response"], "Generated response")

    @patch("coding_agent.nodes.response_nodes.logger")
    def test_post_logging(self, mock_logger):
        node = FormatResponseNode()
        shared = {}
        node.post(shared, [], "Generated response")
        mock_logger.info.assert_called_once_with(
            "###### Final Response Generated ######\nGenerated response\n###### End of Response ######"
        )

if __name__ == "__main__":
    unittest.main()