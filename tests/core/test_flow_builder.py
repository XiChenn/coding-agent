import unittest
from coding_agent.core.flow_foundation import Flow
from coding_agent.core.flow_builder import create_edit_flow, create_main_flow
from coding_agent.nodes.decision_nodes import MainDecisionAgent
from coding_agent.nodes.edit_nodes import ReadTargetFileNode, AnalyzeAndPlanNode, ApplyChangesNode
from coding_agent.nodes.file_nodes import ReadFileAction, GrepSearchAction, ListDirAction, DeleteFileAction
from coding_agent.nodes.response_nodes import FormatResponseNode

class TestFlowBuilder(unittest.TestCase):
    def test_create_edit_flow(self):
        flow = create_edit_flow()
        # Verify that a Flow instance is returned
        self.assertIsInstance(flow, Flow)
        start = flow.start_node

        # Verify start node is a ReadTargetFileNode
        self.assertIsInstance(start, ReadTargetFileNode)
        # There should be at least one connection
        self.assertGreater(len(start.successors), 0)
        # Get the next node from the first connection and verify it is an AnalyzeAndPlanNode
        next_node = list(start.successors.values())[0]
        self.assertIsInstance(next_node, AnalyzeAndPlanNode)
        # Verify that this node is connected to an ApplyChangesNode
        self.assertGreater(len(next_node.successors), 0)
        final_node = list(next_node.successors.values())[0]
        self.assertIsInstance(final_node, ApplyChangesNode)

    def test_create_main_flow(self):
        flow = create_main_flow()
        # Verify that a Flow instance is returned
        self.assertIsInstance(flow, Flow)
        main_agent = flow.start_node
        # Verify the main flow starts with a MainDecisionAgent
        self.assertIsInstance(main_agent, MainDecisionAgent)

        # Expected branches from the main agent
        expected_keys = {"read_file", "grep_search", "list_dir", "delete_file", "edit_file", "finish"}
        self.assertTrue(expected_keys.issubset(set(main_agent.successors.keys())))

        # Check connection types on the main agent
        self.assertIsInstance(main_agent.successors["read_file"], ReadFileAction)
        self.assertIsInstance(main_agent.successors["grep_search"], GrepSearchAction)
        self.assertIsInstance(main_agent.successors["list_dir"], ListDirAction)
        self.assertIsInstance(main_agent.successors["delete_file"], DeleteFileAction)
        self.assertIsInstance(main_agent.successors["finish"], FormatResponseNode)

        # The edit flow should be a Flow instance created by create_edit_flow
        edit_flow = main_agent.successors["edit_file"]
        self.assertIsInstance(edit_flow, Flow)

        # Verify that each action node is connected back to the main agent (using default branch)
        for key in ["read_file", "grep_search", "list_dir", "delete_file"]:
            action_node = main_agent.successors[key]
            self.assertGreater(len(action_node.successors), 0)
            # We extract the first connection to check that it loops back to main_agent
            connected_node = list(action_node.successors.values())[0]
            self.assertEqual(connected_node, main_agent)

if __name__ == "__main__":
    unittest.main()