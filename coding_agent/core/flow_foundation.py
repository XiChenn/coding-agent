import asyncio, warnings, copy, time
from typing import Dict, Any, Optional


class BaseNode:
    """Base class for all workflow nodes."""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name: str = name or self.__class__.__name__
        self.params: Dict[str, Any] = {}
        self.successors: Dict[str, 'BaseNode'] = {}

    def set_params(self, params: Dict[str, Any]) -> 'BaseNode':
        """Set node parameters and return self for chaining."""
        self.params = params
        return self

    def to(self, node: 'BaseNode', action: str = "default") -> 'BaseNode':
        """Connect this node to a successor for the given action."""
        if action in self.successors:
            warnings.warn(f"Overwriting successor for action '{action}'")
        self.successors[action] = node
        return node

    def prep(self, shared: Any) -> Any:
        """Prepare for execution with shared context."""
        return shared

    def exec(self, prep_res: Any) -> Any:
        """Execute node logic with preparation result."""
        pass

    def post(self, shared: Any, prep_res: Any, exec_res: Any) -> Any:
        """Post-process execution results."""
        pass

    def _exec(self, prep_res: Any) -> Any:
        return self.exec(prep_res)

    def _run(self, shared: Any) -> Any:
        prep_res = self.prep(shared)
        exec_res = self._exec(prep_res)
        return self.post(shared, prep_res, exec_res)

    def run(self, shared: Any) -> Any:
        if self.successors:
            warnings.warn("Node won't run successors. Use Flow.")
        return self._run(shared)

    def __str__(self) -> str:
        """String representation of the node."""
        return f"{self.name}(successors={list(self.successors.keys())})"

    def __repr__(self) -> str:
        return self.__str__()


class Node(BaseNode):
    """Node with retry capabilities."""

    def __init__(self, max_retries: int =1 , wait: int = 0):
        super().__init__()
        self.max_retries = max(1, max_retries)  # Ensure at least 1 retry
        self.wait = max(0, wait)  # Ensure non-negative wait
        self.cur_retry = 0

    def exec_fallback(self, prep_res: Any, exc: Exception) -> Any:
        """Handle execution failure after all retries."""
        raise exc

    def _exec(self, prep_res: Any) -> Any:
        for self.cur_retry in range(self.max_retries):
            try:
                return self.exec(prep_res)
            except Exception as e:
                if self.cur_retry == self.max_retries - 1:
                    return self.exec_fallback(prep_res, e)
                if self.wait > 0:
                    time.sleep(self.wait)


class BatchNode(Node):
    """Node that processes batches of items."""
    def _exec(self, items):
        return [super(BatchNode, self)._exec(i) for i in (items or [])]


class Flow(BaseNode):
    """Orchestrates a flow of connected nodes."""

    def __init__(self, start=None):
        super().__init__()
        self.start_node = start

    def start(self, start_node):
        """Set the starting node for this flow."""
        self.start_node = start_node
        return start_node

    def get_next_node(self, curr, action):
        """Get the next node based on current node and action."""
        nxt = curr.successors.get(action or "default")
        if not nxt and curr.successors:
            warnings.warn(f"Flow ends: '{action}' not found in {list(curr.successors)}")
        return nxt

    def _orch(self, shared, params=None):
        """Orchestrate execution of the entire flow."""
        curr = copy.copy(self.start_node)
        node_params = params or {**self.params}
        last_action = None
        while curr:
            curr.set_params(node_params)
            last_action = curr._run(shared)
            curr = copy.copy(self.get_next_node(curr, last_action))

        return last_action

    def _run(self, shared):
        prep_res = self.prep(shared)
        orch_res = self._orch(shared)
        return self.post(shared, prep_res, orch_res)

    def post(self, shared, prep_res, exec_res):
        return exec_res


class BatchFlow(Flow):
    """Flow that processes batches of parameter sets."""

    def _run(self, shared):
        prep_res = self.prep(shared) or []
        for batch_params in prep_res:
            self._orch(shared, {**self.params, **batch_params})
        return self.post(shared, prep_res, None)


class AsyncNode(Node):
    """Node with asynchronous execution capability."""

    async def prep_async(self, shared):
        """Asynchronous preparation."""
        pass

    async def exec_async(self, prep_res):
        """Asynchronous execution."""
        pass

    async def exec_fallback_async(self, prep_res, exc):
        """Asynchronous fallback after failed retries."""
        raise exc

    async def post_async(self, shared, prep_res, exec_res):
        """Asynchronous post-processing."""
        return exec_res

    async def _exec(self, prep_res):
        """Execute async with retry logic."""
        for i in range(self.max_retries):
            try:
                return await self.exec_async(prep_res)
            except Exception as e:
                if i == self.max_retries - 1:
                    return await self.exec_fallback_async(prep_res, e)
                if self.wait > 0:
                    await asyncio.sleep(self.wait)

    async def run_async(self, shared):
        """Public method to execute this node asynchronously."""
        if self.successors:
            warnings.warn("Node won't run successors. Use AsyncFlow.")
        return await self._run_async(shared)

    async def _run_async(self, shared):
        """Run the async node's complete workflow."""
        prep_res = await self.prep_async(shared)
        exec_res = await self._exec(prep_res)
        return await self.post_async(shared, prep_res, exec_res)

    def _run(self, shared):
        """Prevent synchronous execution of async nodes."""
        raise RuntimeError("Use run_async.")


class AsyncBatchNode(AsyncNode, BatchNode):
    """Asynchronous node that processes batches of items sequentially."""

    async def _exec(self, items):
        return [await super(AsyncBatchNode, self)._exec(i) for i in items or []]


class AsyncParallelBatchNode(AsyncNode, BatchNode):
    """Asynchronous node that processes batches of items in parallel."""

    async def _exec(self, items):
        if not items:
            return []
        return await asyncio.gather(*(super(AsyncParallelBatchNode, self)._exec(i) for i in items))


class AsyncFlow(Flow, AsyncNode):
    """Flow with asynchronous execution capability."""

    async def _orch_async(self, shared, params=None):
        """Orchestrate asynchronous execution of the flow."""
        curr = copy.copy(self.start_node)
        node_params = params or {**self.params}
        last_action = None

        while curr:
            curr.set_params(node_params)
            if isinstance(curr, AsyncNode):
                last_action = await curr._run_async(shared)
            else:
                last_action = curr._run(shared)
            curr = copy.copy(self.get_next_node(curr, last_action))

        return last_action

    async def _run_async(self, shared):
        """Run the async flow."""
        prep_res = await self.prep_async(shared)
        orch_res = await self._orch_async(shared)
        return await self.post_async(shared, prep_res, orch_res)

    async def post_async(self, shared, prep_res, exec_res):
        return exec_res


class AsyncBatchFlow(AsyncFlow, BatchFlow):
    """Async flow that processes batches of parameter sets sequentially."""

    async def _run_async(self, shared):
        prep_res = await self.prep_async(shared) or []
        for bp in prep_res:
            await self._orch_async(shared, {**self.params, **bp})
        return await self.post_async(shared, prep_res, None)


class AsyncParallelBatchFlow(AsyncFlow, BatchFlow):
    """Async flow that processes batches of parameter sets in parallel."""

    async def _run_async(self, shared):
        prep_res = await self.prep_async(shared) or []
        tasks = []
        for bp in prep_res:
            tasks.append(self._orch_async(shared, {**self.params, **bp}))
        if tasks:
            await asyncio.gather(*tasks)
        return await self.post_async(shared, prep_res, None)