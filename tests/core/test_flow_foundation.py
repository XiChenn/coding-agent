import unittest
from unittest.mock import MagicMock, patch

from coding_agent.core.flow_foundation import (
    BaseNode, Node, BatchNode, Flow, BatchFlow
)


class TestBaseNode(unittest.TestCase):
    def test_init(self):
        node = BaseNode()
        self.assertEqual(node.name, "BaseNode")
        self.assertEqual(node.params, {})
        self.assertEqual(node.successors, {})

        named_node = BaseNode(name="CustomNode")
        self.assertEqual(named_node.name, "CustomNode")

    def test_set_params(self):
        node = BaseNode()
        params = {"key": "value"}
        result = node.set_params(params)
        self.assertEqual(node.params, params)
        self.assertEqual(result, node)  # Should return self for chaining

    def test_to_connection(self):
        node1 = BaseNode(name="Node1")
        node2 = BaseNode(name="Node2")

        result = node1.to(node2)
        self.assertEqual(node1.successors["default"], node2)
        self.assertEqual(result,
                         node2)  # Should return target node for chaining

        node3 = BaseNode(name="Node3")
        node1.to(node3, "custom_action")
        self.assertEqual(node1.successors["custom_action"], node3)

    def test_to_method_chaining(self):
        node1 = BaseNode(name="Node1")
        node2 = BaseNode(name="Node2")
        node3 = BaseNode(name="Node3")
        # Chain the connections
        result = node1.to(node2, "action1").to(node3, "action2")
        # The 'to' method returns the target node for chaining.
        self.assertEqual(result, node3)
        # Verify the connections on the original nodes.
        self.assertEqual(node1.successors["action1"], node2)
        self.assertEqual(node2.successors["action2"], node3)

    def test_run(self):
        node = BaseNode()
        node.prep = MagicMock(return_value="prep_result")
        node.exec = MagicMock(return_value="exec_result")
        node.post = MagicMock(return_value="final_result")

        result = node.run("shared_context")
        node.prep.assert_called_once_with("shared_context")
        node.exec.assert_called_once_with("prep_result")
        node.post.assert_called_once_with("shared_context", "prep_result",
                                          "exec_result")
        self.assertEqual(result, "final_result")


class TestNode(unittest.TestCase):
    def test_retry_logic(self):
        node = Node(max_retries=3, wait=0)

        # Test successful execution on first try
        node.exec = MagicMock(return_value="success")
        result = node._exec("input")
        self.assertEqual(result, "success")
        self.assertEqual(node.exec.call_count, 1)

        # Test retry logic
        node.exec = MagicMock(side_effect=[ValueError, ValueError, "success"])
        result = node._exec("input")
        self.assertEqual(result, "success")
        self.assertEqual(node.exec.call_count, 3)

        # Test fallback when all retries fail
        node.exec = MagicMock(side_effect=ValueError("error"))
        node.exec_fallback = MagicMock(return_value="fallback")
        result = node._exec("input")
        self.assertEqual(result, "fallback")
        self.assertEqual(node.exec.call_count, 3)
        node.exec_fallback.assert_called_once()


class TestBatchNode(unittest.TestCase):
    def test_batch_processing(self):
        node = BatchNode()
        node.exec = MagicMock(side_effect=lambda x: f"processed_{x}")

        result = node._exec(["a", "b", "c"])
        self.assertEqual(result, ["processed_a", "processed_b", "processed_c"])
        self.assertEqual(node.exec.call_count, 3)

        # Test with empty batch
        result = node._exec([])
        self.assertEqual(result, [])

        # Test with None
        result = node._exec(None)
        self.assertEqual(result, [])


class TestFlow(unittest.TestCase):
    def test_flow_execution(self):
        node1 = BaseNode(name="Node1")
        node2 = BaseNode(name="Node2")
        node3 = BaseNode(name="Node3")

        # Set up mock functions
        node1._run = MagicMock(return_value="action1")
        node2._run = MagicMock(return_value="action2")
        node3._run = MagicMock(return_value="final")

        # Connect nodes
        node1.to(node2, "action1")
        node2.to(node3, "action2")

        flow = Flow(start=node1)
        result = flow._run("shared_context")

        # Verify execution path
        node1._run.assert_called_once_with("shared_context")
        node2._run.assert_called_once_with("shared_context")
        node3._run.assert_called_once_with("shared_context")
        self.assertEqual(result, "final")

    def test_parameter_handling(self):
        """Test specifically the line: node_params = params or {**self.params}"""
        start_node = BaseNode()
        flow = Flow(start=start_node)

        # Case 1: params provided
        flow.params = {"flow_param": "value"}
        provided_params = {"override_param": "new_value"}

        with patch.object(Flow, 'get_next_node', return_value=None):
            with patch.object(BaseNode, '_run'):
                with patch.object(BaseNode, 'set_params') as mock_set_params:
                    flow._orch("shared", provided_params)
                    # Verify the provided params were used
                    mock_set_params.assert_called_once_with(provided_params)

        # Case 2: no params provided, use flow.params
        with patch.object(Flow, 'get_next_node', return_value=None):
            with patch.object(BaseNode, '_run'):
                with patch.object(BaseNode, 'set_params') as mock_set_params:
                    flow._orch("shared", None)
                    # Verify flow.params was used
                    mock_set_params.assert_called_once_with(
                        {"flow_param": "value"})


class TestBatchFlow(unittest.TestCase):
    def test_batch_flow(self):
        flow = BatchFlow()
        flow._orch = MagicMock()
        flow.prep = MagicMock(
            return_value=[{"param1": "value1"}, {"param2": "value2"}])

        flow._run("shared")
        self.assertEqual(flow._orch.call_count, 2)
        flow._orch.assert_any_call("shared", {"param1": "value1"})
        flow._orch.assert_any_call("shared", {"param2": "value2"})


if __name__ == "__main__":
    unittest.main()