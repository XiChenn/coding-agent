from typing import List, Dict, Any

from coding_agent.logger import setup_logger

# Configure logging
logger = setup_logger("formatters")

def format_history_summary(history: List[Dict[str, Any]]) -> str:
    if not history:
        return "No previous actions."

    history_str = "\n"

    for i, action in enumerate(history):
        # Header for all entries - removed timestamp
        history_str += f"Action {i + 1}:\n"
        history_str += f"- Tool: {action['tool']}\n"
        history_str += f"- Reason: {action['reason']}\n"

        # Add parameters
        params = action.get("params", {})
        if params:
            history_str += f"- Parameters:\n"
            for k, v in params.items():
                history_str += f"  - {k}: {v}\n"

        # Add detailed result information
        result = action.get("result")
        if result:
            if isinstance(result, dict):
                success = result.get("success", False)
                history_str += f"- Result: {'Success' if success else 'Failed'}\n"

                # Add tool-specific details
                if action['tool'] == 'read_file' and success:
                    content = result.get("content", "")
                    # Show full content without truncating
                    history_str += f"- Content: {content}\n"
                elif action['tool'] == 'grep_search' and success:
                    matches = result.get("matches", [])
                    history_str += f"- Matches: {len(matches)}\n"
                    # Show all matches without limiting to first 3
                    for j, match in enumerate(matches):
                        history_str += f"  {j + 1}. {match.get('file')}:{match.get('line')}: {match.get('content')}\n"
                elif action['tool'] == 'edit_file' and success:
                    operations = result.get("operations", 0)
                    history_str += f"- Operations: {operations}\n"

                    # Include the reasoning if available
                    reasoning = result.get("reasoning", "")
                    if reasoning:
                        history_str += f"- Reasoning: {reasoning}\n"
                elif action['tool'] == 'list_dir' and success:
                    # Get the tree visualization string
                    tree_visualization = result.get("tree_visualization", "")
                    history_str += "- Directory structure:\n"

                    # Properly handle and format the tree visualization
                    if tree_visualization and isinstance(tree_visualization,
                                                         str):
                        # First, ensure we handle any special line ending characters properly
                        clean_tree = tree_visualization.replace('\r\n',
                                                                '\n').strip()

                        if clean_tree:
                            # Add each line with proper indentation
                            for line in clean_tree.split('\n'):
                                # Ensure the line is properly indented
                                if line.strip():  # Only include non-empty lines
                                    history_str += f"  {line}\n"
                        else:
                            history_str += "  (No tree structure data)\n"
                    else:
                        history_str += "  (Empty or inaccessible directory)\n"
                        logger.debug(
                            f"Tree visualization missing or invalid: {tree_visualization}")
            else:
                history_str += f"- Result: {result}\n"

        # Add separator between actions
        history_str += "\n" if i < len(history) - 1 else ""

    return history_str