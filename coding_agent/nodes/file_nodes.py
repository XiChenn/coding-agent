import os

from typing import List, Dict, Any, Tuple

from coding_agent.core.base_nodes import Node
from coding_agent.logger import setup_logger
from coding_agent.utils.file_utils import delete_file
from coding_agent.utils.file_utils import list_dir, read_file, grep_search

# Configure logging
logger = setup_logger("file_nodes")


#############################################
# Read File Action Node
#############################################
class ReadFileAction(Node):
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

        # Use the reason for logging instead of explanation
        reason = last_action.get("reason", "No reason provided")
        logger.info(f"ReadFileAction: {reason}")

        return full_path

    def exec(self, file_path: str) -> Tuple[str, bool]:
        # Call read_file utility which returns a tuple of (content, success)
        return read_file(file_path)

    def post(self, shared: Dict[str, Any], prep_res: str,
             exec_res: Tuple[str, bool]) -> None:
        # Unpack the tuple returned by read_file()
        content, success = exec_res

        # Update the result in the last history entry
        history = shared.get("history", [])
        if history:
            history[-1]["result"] = {
                "success": success,
                "content": content
            }


#############################################
# Grep Search Action Node
#############################################
class GrepSearchAction(Node):
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        # Get parameters from the last history entry
        history = shared.get("history", [])
        if not history:
            raise ValueError("No history found")

        last_action = history[-1]
        params = last_action["params"]

        if "query" not in params:
            raise ValueError("Missing query parameter")

        # Use the reason for logging instead of explanation
        reason = last_action.get("reason", "No reason provided")
        logger.info(f"GrepSearchAction: {reason}")

        # Ensure paths are relative to working directory
        working_dir = shared.get("working_dir", "")

        return {
            "query": params["query"],
            "case_sensitive": params.get("case_sensitive", False),
            "include_pattern": params.get("include_pattern"),
            "exclude_pattern": params.get("exclude_pattern"),
            "working_dir": working_dir
        }

    def exec(self, params: Dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
        # Use current directory if not specified
        working_dir = params.pop("working_dir", "")

        # Call grep_search utility which returns (success, matches)
        return grep_search(
            query=params["query"],
            case_sensitive=params.get("case_sensitive", False),
            include_pattern=params.get("include_pattern"),
            exclude_pattern=params.get("exclude_pattern"),
            working_dir=working_dir
        )

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any],
             exec_res: Tuple[bool, List[Dict[str, Any]]]) -> None:
        matches, success = exec_res

        # Update the result in the last history entry
        history = shared.get("history", [])
        if history:
            history[-1]["result"] = {
                "success": success,
                "matches": matches
            }


#############################################
# List Directory Action Node
#############################################
class ListDirAction(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        # Get parameters from the last history entry
        history = shared.get("history", [])
        if not history:
            raise ValueError("No history found")

        last_action = history[-1]
        path = last_action["params"].get("relative_workspace_path", ".")

        # Use the reason for logging instead of explanation
        reason = last_action.get("reason", "No reason provided")
        logger.info(f"ListDirAction: {reason}")

        # Ensure path is relative to working directory
        working_dir = shared.get("working_dir", "")
        full_path = os.path.join(working_dir, path) if working_dir else path

        return full_path

    def exec(self, path: str) -> Tuple[bool, str]:
        # Call list_dir utility which now returns (success, tree_str)
        success, tree_str = list_dir(path)

        return success, tree_str

    def post(self, shared: Dict[str, Any], prep_res: str,
             exec_res: Tuple[bool, str]) -> None:
        success, tree_str = exec_res

        # Update the result in the last history entry with the new structure
        history = shared.get("history", [])
        if history:
            history[-1]["result"] = {
                "success": success,
                "tree_visualization": tree_str
            }


#############################################
# Delete File Action Node
#############################################
class DeleteFileAction(Node):
    def prep(self, shared: Dict[str, Any]) -> str:
        # Get parameters from the last history entry
        history = shared.get("history", [])
        if not history:
            raise ValueError("No history found")

        last_action = history[-1]
        file_path = last_action["params"].get("target_file")

        if not file_path:
            raise ValueError("Missing target_file parameter")

        # Use the reason for logging instead of explanation
        reason = last_action.get("reason", "No reason provided")
        logger.info(f"DeleteFileAction: {reason}")

        # Ensure path is relative to working directory
        working_dir = shared.get("working_dir", "")
        full_path = os.path.join(working_dir,
                                 file_path) if working_dir else file_path

        return full_path

    def exec(self, file_path: str) -> tuple[str, bool]:
        # Call delete_file utility which returns (success, message)
        return delete_file(file_path)

    def post(self, shared: Dict[str, Any], prep_res: str,
             exec_res: Tuple[bool, str]) -> None:
        success, message = exec_res

        # Update the result in the last history entry
        history = shared.get("history", [])
        if history:
            history[-1]["result"] = {
                "success": success,
                "message": message
            }
