import os
from typing import List, Dict, Any, Tuple

import yaml

from coding_agent.core.base_nodes import Node, BatchNode
from coding_agent.logger import setup_logger
from coding_agent.utils.llm_utils import call_llm
from coding_agent.tools.file_tools import read_file, replace_file

# Configure logging
logger = setup_logger("edit_nodes")

#############################################
# Read Target File Node (Edit Agent)
#############################################
class ReadTargetFileNode(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        # Get parameters from the last history entry
        history = shared.get("history", [])
        if not history:
            raise ValueError("No history found")

        last_action = history[-1]
        file_path = last_action["params"].get("target_file")

        if not file_path:
            raise ValueError("Missing target_file parameter")

        # Ensure path is relative to working directory
        working_dir = shared.get("working_dir", "")
        full_path = os.path.join(working_dir,
                                 file_path) if working_dir else file_path

        return full_path

    def exec(self, file_path: str) -> Tuple[str, bool]:
        # Call read_file utility which returns (content, success)
        return read_file(file_path)

    def post(self, shared: Dict[str, Any], prep_res: str,
             exec_res: Tuple[str, bool]) -> None:
        content, success = exec_res
        logger.info("ReadTargetFileNode: File read completed for editing")

        # Store file content in the history entry
        history = shared.get("history", [])
        if history:
            history[-1]["file_content"] = content


#############################################
# Analyze and Plan Changes Node
#############################################
class AnalyzeAndPlanNode(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        # Get history
        history = shared.get("history", [])
        if not history:
            raise ValueError("No history found")

        last_action = history[-1]
        file_content = last_action.get("file_content")
        instructions = last_action["params"].get("instructions")
        code_edit = last_action["params"].get("code_edit")

        if not file_content:
            raise ValueError("File content not found")
        if not instructions:
            raise ValueError("Missing instructions parameter")
        if not code_edit:
            raise ValueError("Missing code_edit parameter")

        return {
            "file_content": file_content,
            "instructions": instructions,
            "code_edit": code_edit
        }

    def exec(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        file_content = params["file_content"]
        instructions = params["instructions"]
        code_edit = params["code_edit"]

        # File content as lines
        file_lines = file_content.split('\n')
        total_lines = len(file_lines)

        # Generate a prompt for the LLM to analyze the edit using YAML instead of JSON
        prompt = f"""
As a code editing assistant, I need to convert the following code edit instruction 
and code edit pattern into specific edit operations (start_line, end_line, replacement).

FILE CONTENT:
{file_content}

EDIT INSTRUCTIONS: 
{instructions}

CODE EDIT PATTERN (markers like "// ... existing code ..." indicate unchanged code):
{code_edit}

Analyze the file content and the edit pattern to determine exactly where changes should be made. 
Be very careful with start and end lines. They are 1-indexed and inclusive. These will be REPLACED, not APPENDED!
If you want APPEND, just copy that line as the first line of the replacement.
Return a YAML object with your reasoning and an array of edit operations:

```yaml
reasoning: |
  First explain your thinking process about how you're interpreting the edit pattern.
  Explain how you identified where the edits should be made in the original file.
  Describe any assumptions or decisions you made when determining the edit locations. 
  You need to be very precise with the start and end lines! Reason why not 1 line before or after the start and end lines.

operations:
  - start_line: 10
    end_line: 15
    replacement: |
      def process_file(filename):
          # New implementation with better error handling
          try:
              with open(filename, 'r') as f:
                  return f.read()
          except FileNotFoundError:
              return None

  - start_line: 25
    end_line: 25
    replacement: |
      logger.info("File processing completed")
```

For lines that include "// ... existing code ...", do not include them in the replacement.
Instead, identify the exact lines they represent in the original file and set the line 
numbers accordingly. Start_line and end_line are 1-indexed.

If the instruction indicates content should be appended to the file, set both start_line and end_line 
to the maximum line number + 1, which will add the content at the end of the file.
"""

        # Call LLM to analyze
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

        if yaml_content:
            decision = yaml.safe_load(yaml_content)

            # Validate the required fields
            assert "reasoning" in decision, "Reasoning is missing"
            assert "operations" in decision, "Operations are missing"

            # Ensure operations is a list
            if not isinstance(decision["operations"], list):
                raise ValueError("Operations are not a list")

            # Validate operations
            for op in decision["operations"]:
                assert "start_line" in op, "start_line is missing"
                assert "end_line" in op, "end_line is missing"
                assert "replacement" in op, "replacement is missing"
                assert 1 <= op[
                    "start_line"] <= total_lines, f"start_line out of range: {op['start_line']}"
                assert 1 <= op[
                    "end_line"] <= total_lines, f"end_line out of range: {op['end_line']}"
                assert op["start_line"] <= op[
                    "end_line"], f"start_line > end_line: {op['start_line']} > {op['end_line']}"

            return decision
        else:
            raise ValueError("No YAML object found in response")

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any],
             exec_res: Dict[str, Any]) -> None:
        # Store reasoning and edit operations in shared
        shared["edit_reasoning"] = exec_res.get("reasoning", "")
        shared["edit_operations"] = exec_res.get("operations", [])


#############################################
# Apply Changes Batch Node
#############################################
class ApplyChangesNode(BatchNode):
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get edit operations
        edit_operations = shared.get("edit_operations", [])
        if not edit_operations:
            logger.warning("No edit operations found")
            return []

        # Sort edit operations in descending order by start_line
        # This ensures that line numbers remain valid as we edit from bottom to top
        sorted_ops = sorted(edit_operations, key=lambda op: op["start_line"],
                            reverse=True)

        # Get target file from history
        history = shared.get("history", [])
        if not history:
            raise ValueError("No history found")

        last_action = history[-1]
        target_file = last_action["params"].get("target_file")

        if not target_file:
            raise ValueError("Missing target_file parameter")

        # Ensure path is relative to working directory
        working_dir = shared.get("working_dir", "")
        full_path = os.path.join(working_dir,
                                 target_file) if working_dir else target_file

        # Attach file path to each operation
        for op in sorted_ops:
            op["target_file"] = full_path

        return sorted_ops

    def exec(self, op: Dict[str, Any]) -> tuple[str, bool]:
        # Call replace_file utility which returns (success, message)
        return replace_file(
            target_file=op["target_file"],
            start_line=op["start_line"],
            end_line=op["end_line"],
            content=op["replacement"]
        )

    def post(self, shared: Dict[str, Any], prep_res: List[Dict[str, Any]],
             exec_res_list: List[Tuple[bool, str]]) -> None:
        # Check if all operations were successful
        all_successful = all(success for success, _ in exec_res_list)

        # Format results for history
        result_details = [
            {"success": success, "message": message}
            for success, message in exec_res_list
        ]

        # Update edit result in history
        history = shared.get("history", [])
        if history:
            history[-1]["result"] = {
                "success": all_successful,
                "operations": len(exec_res_list),
                "details": result_details,
                "reasoning": shared.get("edit_reasoning", "")
            }

        # Clear edit operations and reasoning after processing
        shared.pop("edit_operations", None)
        shared.pop("edit_reasoning", None)