import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from coding_agent.nodes.decision_nodes import MainDecisionAgent

class TestMainDecisionAgent(unittest.TestCase):
    def setUp(self):
        self.shared_data = {
            "user_query": "What files were modified?",
            "history": [
                {
                    "tool": "ListDirAction",
                    "reason": "List all files in the directory",
                    "params": {"relative_workspace_path": "."},
                    "result": {"success": True, "tree_visualization": "file_tree"},
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }

    def test_prep(self):
        agent = MainDecisionAgent()
        user_query, history = agent.prep(self.shared_data)
        self.assertEqual(user_query, "What files were modified?")
        self.assertEqual(len(history), 1)

    @patch("coding_agent.nodes.decision_nodes.call_llm")
    @patch("coding_agent.nodes.decision_nodes.format_history_summary")
    @patch("coding_agent.nodes.decision_nodes.generate_decision_prompt")
    def test_exec(self, mock_generate_prompt, mock_format_history, mock_call_llm):
        agent = MainDecisionAgent()
        mock_format_history.return_value = "Formatted history"
        mock_generate_prompt.return_value = "Generated prompt"
        mock_call_llm.return_value = """
tool: ListDirAction
reason: "List files in the directory"
params:
  relative_workspace_path: "."
"""
        inputs = agent.prep(self.shared_data)
        decision = agent.exec(inputs)
        self.assertEqual(decision["tool"], "ListDirAction")
        self.assertEqual(decision["reason"], "List files in the directory")
        self.assertEqual(decision["params"]["relative_workspace_path"], ".")

    @patch("coding_agent.nodes.decision_nodes.logger.info")
    def test_post(self, mock_logger):
        agent = MainDecisionAgent()
        prep_res = agent.prep(self.shared_data)
        exec_res = {
            "tool": "ListDirAction",
            "reason": "List files in the directory",
            "params": {"relative_workspace_path": "."}
        }
        tool = agent.post(self.shared_data, prep_res, exec_res)
        self.assertEqual(tool, "ListDirAction")
        self.assertEqual(len(self.shared_data["history"]), 2)
        self.assertEqual(self.shared_data["history"][-1]["tool"], "ListDirAction")
        self.assertEqual(self.shared_data["history"][-1]["reason"], "List files in the directory")
        mock_logger.assert_called_with("MainDecisionAgent: Selected tool: ListDirAction")

if __name__ == "__main__":
    unittest.main()