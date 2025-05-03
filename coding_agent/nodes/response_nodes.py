from typing import List, Dict, Any

from coding_agent.core.flow_foundation import Node
from coding_agent.logger import setup_logger
from coding_agent.utils.llm_utils import call_llm
from coding_agent.utils.formatters import format_history_summary
from coding_agent.utils.prompts import generate_response_formatting_prompt

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
        prompt = generate_response_formatting_prompt(actions_summary)

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