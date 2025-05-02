from typing import List, Dict, Any

from coding_agent.core.base_nodes import Node
from coding_agent.logger import setup_logger
from coding_agent.utils.llm_utils import call_llm
from coding_agent.utils.formatters import format_history_summary

# Configure logging
logger = setup_logger("response_nodes")

#############################################
# Format Response Node
#############################################
class FormatResponseNode(Node):
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get history
        history = shared.get("history", [])

        return history

    def exec(self, history: List[Dict[str, Any]]) -> str:
        # If no history, return a generic message
        if not history:
            return "No actions were performed."

        # Generate a summary of actions for the LLM using the utility function
        actions_summary = format_history_summary(history)

        # Prompt for the LLM to generate the final response
        prompt = f"""
You are a coding assistant. You have just performed a series of actions based on the 
user's request. Summarize what you did in a clear, helpful response.

Here are the actions you performed:
{actions_summary}

Generate a comprehensive yet concise response that explains:
1. What actions were taken
2. What was found or modified
3. Any next steps the user might want to take

IMPORTANT: 
- Focus on the outcomes and results, not the specific tools used
- Write as if you are directly speaking to the user
- When providing code examples or structured information, use YAML format enclosed in triple backticks
"""

        # Call LLM to generate response
        response = call_llm(prompt)

        return response

    def post(self, shared: Dict[str, Any], prep_res: List[Dict[str, Any]],
             exec_res: str) -> str:
        logger.info(
            f"###### Final Response Generated ######\n{exec_res}\n###### End of Response ######")

        # Store response in shared
        shared["response"] = exec_res

        return "done"