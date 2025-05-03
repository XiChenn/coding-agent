from typing import List, Dict, Any, Tuple
from datetime import datetime

import yaml

from coding_agent.core.flow_foundation import Node
from coding_agent.logger import setup_logger
from coding_agent.utils.llm_utils import call_llm
from coding_agent.utils.formatters import format_history_summary
from coding_agent.utils.prompts import generate_decision_prompt

# Configure logging
logger = setup_logger("decision_nodes")


#############################################
# Main Decision Agent Node
#############################################
class MainDecisionAgent(Node):
    def prep(self, shared: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        # Get user query and history
        user_query = shared.get("user_query", "")
        history = shared.get("history", [])

        return user_query, history

    def exec(self, inputs: Tuple[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        user_query, history = inputs
        logger.info(f"MainDecisionAgent: Analyzing user query: {user_query}")

        # Format history using the utility function with 'basic' detail level
        history_str = format_history_summary(history)

        # Create the prompt for the LLM using YAML instead of JSON
        prompt = generate_decision_prompt(user_query, history_str)

        # Call LLM to decide action
        response = call_llm(prompt)

        # Look for YAML structure in the response
        yaml_content = ""
        if "```yaml" in response:
            yaml_blocks = response.split("```yaml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
        elif "```yml" in response:
            yaml_blocks = response.split("```yml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
        elif "```" in response:
            # Try to extract from generic code block
            yaml_blocks = response.split("```")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].strip()
        else:
            # If no code blocks, try to use the entire response
            yaml_content = response.strip()

        if yaml_content:
            decision = yaml.safe_load(yaml_content)

            # Validate the required fields
            assert "tool" in decision, "Tool name is missing"
            assert "reason" in decision, "Reason is missing"

            # For tools other than "finish", params must be present
            if decision["tool"] != "finish":
                assert "params" in decision, "Parameters are missing"
            else:
                decision["params"] = {}

            return decision
        else:
            raise ValueError("No YAML object found in response")

    def post(self, shared: Dict[str, Any], prep_res: Any,
             exec_res: Dict[str, Any]) -> str:
        logger.info(f"MainDecisionAgent: Selected tool: {exec_res['tool']}")

        # Initialize history if not present
        if "history" not in shared:
            shared["history"] = []

        # Add this action to history
        shared["history"].append({
            "tool": exec_res["tool"],
            "reason": exec_res["reason"],
            "params": exec_res.get("params", {}),
            "result": None,  # Will be filled in by action nodes
            "timestamp": datetime.now().isoformat()
        })

        # Return the action to take
        return exec_res["tool"]