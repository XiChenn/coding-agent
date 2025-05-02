import os
from typing import Tuple, Optional, List, Dict, Any

from coding_agent.logger import setup_logger

# Configure logging
logger = setup_logger("file_tools")


def read_file(
        target_file: str,
        start_line_one_indexed: Optional[int] = None,
        end_line_one_indexed_inclusive: Optional[int] = None,
        should_read_entire_file: bool = False
) -> Tuple[str, bool]:
    """
    Read content from a file with support for line ranges.
    Prepends 1-based line numbers to each line in the output.

    Args:
        target_file: Path to the file (relative or absolute)
        start_line_one_indexed: Starting line number (1-based). If None, defaults to reading entire file.
        end_line_one_indexed_inclusive: Ending line number (1-based). If None, defaults to reading entire file.
        should_read_entire_file: If True, ignore line parameters and read entire file

    Returns:
        Tuple of (file content with line numbers, success status)
    """
    try:
        if not os.path.exists(target_file):
            return f"Error: File {target_file} does not exist", False

        # If only target_file is provided or any line parameter is None, read the entire file
        if start_line_one_indexed is None or end_line_one_indexed_inclusive is None:
            should_read_entire_file = True

        with open(target_file, 'r', encoding='utf-8') as f:
            if should_read_entire_file:
                lines = f.readlines()
                # Add line numbers to each line
                numbered_lines = [f"{i + 1}: {line}" for i, line in
                                  enumerate(lines)]
                return ''.join(numbered_lines), True

            # Validate line range parameters
            if start_line_one_indexed < 1:
                return "Error: start_line_one_indexed must be at least 1", False

            if end_line_one_indexed_inclusive < start_line_one_indexed:
                return "Error: end_line_one_indexed_inclusive must be >= start_line_one_indexed", False

            # Check if requested range exceeds 250 lines limit
            if end_line_one_indexed_inclusive - start_line_one_indexed + 1 > 250:
                return "Error: Cannot read more than 250 lines at once", False

            # Read the specified lines
            lines = f.readlines()

            # Adjust for one-indexed to zero-indexed
            start_idx = start_line_one_indexed - 1
            end_idx = end_line_one_indexed_inclusive - 1

            # Check if the requested range is out of bounds
            if start_idx >= len(lines):
                return f"Error: start_line_one_indexed ({start_line_one_indexed}) exceeds file length ({len(lines)})", False

            end_idx = min(end_idx, len(lines) - 1)

            # Add line numbers to the selected lines
            numbered_lines = [f"{i + 1}: {lines[i]}" for i in
                              range(start_idx, end_idx + 1)]

            return ''.join(numbered_lines), True

    except Exception as e:
        return f"Error reading file: {str(e)}", False


def insert_file(target_file: str, content: str, line_number: int = None) -> \
Tuple[str, bool]:
    """
    Write or insert content to a target file.

    Args:
        target_file: Path to the file to modify
        content: The content to write or insert into the file
        line_number: Line number to insert at (1-indexed). If None, replace entire file.

    Returns:
        Tuple of (result message, success status)
    """
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(target_file)),
                    exist_ok=True)

        file_exists = os.path.exists(target_file)

        # Complete file replacement or new file creation
        if line_number is None:
            if file_exists:
                os.remove(target_file)
                operation = "replaced"
            else:
                operation = "created"

            # Create the file with new content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully {operation} {target_file}", True

        # Insert at specific line
        else:
            if not file_exists:
                # If file doesn't exist but line_number is specified, create it with empty lines
                lines = [''] * max(0, line_number - 1)
                operation = "created and inserted into"
            else:
                # Read existing content
                with open(target_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                operation = "inserted into"

            # Ensure line_number is valid
            if line_number < 1:
                return "Error: Line number must be at least 1", False

            # Calculate insert position with 1-indexed to 0-indexed conversion
            position = line_number - 1

            # If position is beyond the end, pad with newlines
            while len(lines) < position:
                lines.append('\n')

            # Insert content at specified position
            if position == len(lines):
                # Add at the end (may need newline if last line doesn't end with one)
                if lines and not lines[-1].endswith('\n'):
                    lines[-1] += '\n'
                lines.append(content)
            else:
                # Split the line at the insertion point if it exists
                lines.insert(position, content)

            # Write the updated content
            with open(target_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            return f"Successfully {operation} {target_file} at line {line_number}", True

    except Exception as e:
        return f"Error inserting file: {str(e)}", False


def delete_file(target_file: str) -> Tuple[str, bool]:
    """
    Remove a file from the file system.
    
    Args:
        target_file: Path to the file to delete
    
    Returns:
        Tuple of (result message, success status)
    """
    try:
        if not os.path.exists(target_file):
            logger.warning(f"File {target_file} does not exist")
            return f"File {target_file} does not exist", False
        
        os.remove(target_file)
        logger.info(f"Successfully deleted {target_file}")
        return f"Successfully deleted {target_file}", True
            
    except Exception as e:
        error_msg = f"Error deleting file: {str(e)}"
        logger.error(error_msg)
        return error_msg, False


def remove_file(target_file: str, start_line: int = None,
                end_line: int = None) -> Tuple[str, bool]:
    """
    Remove content from a file based on line numbers.
    At least one of start_line or end_line must be specified.

    Args:
        target_file: Path to the file to modify
        start_line: Starting line number to remove (1-indexed)
        end_line: Ending line number to remove (1-indexed, inclusive)
                  If None, removes to the end of the file

    Returns:
        Tuple of (result message, success status)
    """
    try:
        # Check if file exists
        if not os.path.exists(target_file):
            logger.error(f"File {target_file} does not exist")
            return f"Error: File {target_file} does not exist", False

        # Require at least one of start_line or end_line to be specified
        if start_line is None and end_line is None:
            logger.error(
                "At least one of start_line or end_line must be specified")
            return "Error: At least one of start_line or end_line must be specified", False

        # Read the file content
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Validate line numbers
        if start_line is not None and start_line < 1:
            logger.error("start_line must be at least 1")
            return "Error: start_line must be at least 1", False

        if end_line is not None and end_line < 1:
            logger.error("end_line must be at least 1")
            return "Error: end_line must be at least 1", False

        if start_line is not None and end_line is not None and start_line > end_line:
            logger.error("start_line must be less than or equal to end_line")
            return "Error: start_line must be less than or equal to end_line", False

        # Adjust for 1-indexed to 0-indexed
        start_idx = start_line - 1 if start_line is not None else 0
        end_idx = end_line - 1 if end_line is not None else len(lines) - 1

        # Don't report error if start_line is beyond file length
        # Just return success with a message indicating no lines were removed
        if start_idx >= len(lines):
            logger.info(
                f"No lines removed: start_line ({start_line}) exceeds file length ({len(lines)})")
            return f"No lines removed: start_line ({start_line}) exceeds file length ({len(lines)})", True

        # If end_line goes beyond file length, just remove to the end of the file
        end_idx = min(end_idx, len(lines) - 1)

        # Remove the specified lines
        del lines[start_idx:end_idx + 1]

        # Write the updated content back to the file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # Prepare message based on what was removed
        if start_line is None:
            message = f"Successfully removed lines 1 to {end_line} from {target_file}"
        elif end_line is None:
            message = f"Successfully removed lines {start_line} to end from {target_file}"
        else:
            message = f"Successfully removed lines {start_line} to {end_line} from {target_file}"

        logger.info(message)
        return message, True

    except Exception as e:
        error_msg = f"Error removing content: {str(e)}"
        logger.error(error_msg)
        return error_msg, False


def replace_file(target_file: str, start_line: int, end_line: int,
                 content: str) -> Tuple[str, bool]:
    """
    Replace content in a file between specified line numbers.

    Args:
        target_file: Path to the file to modify
        start_line: Starting line number to replace (1-indexed)
        end_line: Ending line number to replace (1-indexed, inclusive)
        content: The new content to replace the specified lines with

    Returns:
        Tuple of (result message, success status)
    """

    try:
        # Check if file exists
        if not os.path.exists(target_file):
            return f"Error: File {target_file} does not exist", False

        # Validate line numbers
        if start_line < 1:
            return "Error: start_line must be at least 1", False

        if end_line < 1:
            return "Error: end_line must be at least 1", False

        if start_line > end_line:
            return "Error: start_line must be less than or equal to end_line", False

        # First, remove the specified lines
        remove_result, remove_success = remove_file(target_file, start_line,
                                                    end_line)

        if not remove_success:
            return f"Error during remove step: {remove_result}", False

        # Then, insert the new content at the start line
        insert_result, insert_success = insert_file(target_file, content,
                                                    start_line)

        if not insert_success:
            return f"Error during insert step: {insert_result}", False

        return f"Successfully replaced lines {start_line} to {end_line} in {target_file}", True

    except Exception as e:
        return f"Error replacing content: {str(e)}", False


def _build_tree_str(items: List[Dict[str, Any]], prefix: str = "",
                    is_last: bool = True, show_all: bool = True) -> str:
    """
    Helper function to build a tree-style string representation of the directory structure.
    Only shows one level of directories and limits files shown per directory.
    """
    tree_str = ""
    # Split items into directories and files
    dirs = [item for item in items if item["type"] == "directory"]
    files = [item for item in items if item["type"] == "file"]

    # Process directories first
    for i, item in enumerate(dirs):
        is_last_item = i == len(dirs) == 0 and len(files) == 0
        connector = "└──" if is_last_item else "├──"
        tree_str += f"{prefix}{connector} {item['name']}/\n"

        # For directories, just show count of contents
        if "children" in item:
            child_dirs = sum(
                1 for c in item["children"] if c["type"] == "directory")
            child_files = sum(
                1 for c in item["children"] if c["type"] == "file")
            next_prefix = prefix + ("    " if is_last_item else "│   ")
            if child_dirs > 0 or child_files > 0:
                summary = []
                if child_dirs > 0:
                    summary.append(
                        f"{child_dirs} director{'y' if child_dirs == 1 else 'ies'}")
                if child_files > 0:
                    summary.append(
                        f"{child_files} file{'s' if child_files != 1 else ''}")
                tree_str += f"{next_prefix}└── [{', '.join(summary)}]\n"

    # Then process files
    if files:
        for i, item in enumerate(files[:10]):
            is_last_item = i == len(files) - 1 if (
                        len(files) <= 10 or i == 9) else False
            connector = "└──" if is_last_item else "├──"
            size_str = f" ({item['size'] / 1024:.1f} KB)" if item.get("size",
                                                                      0) > 0 else ""
            tree_str += f"{prefix}{connector} {item['name']}{size_str}\n"

        # If there are more than 10 files, show ellipsis
        if len(files) > 10:
            tree_str += f"{prefix}└── ... ({len(files) - 10} more files)\n"

    return tree_str


def list_dir(relative_workspace_path: str) -> Tuple[bool, str]:
    """
    List contents of a directory (one level only).

    Args:
        relative_workspace_path: Path to list contents of, relative to the workspace root

    Returns:
        Tuple of (success status, tree visualization string)
    """

    def _list_dir_recursive(path: str, depth: int = 0) -> List[Dict[str, Any]]:
        items = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_dir = os.path.isdir(item_path)

                item_info = {
                    "name": item,
                    "path": item_path,
                    "type": "directory" if is_dir else "file"
                }

                if not is_dir:
                    try:
                        item_info["size"] = os.path.getsize(item_path)
                    except:
                        item_info["size"] = 0
                elif depth < 1:  # Only recurse one level
                    # Recursively list directory contents
                    item_info["children"] = _list_dir_recursive(item_path,
                                                                depth + 1)

                items.append(item_info)

            # Sort: directories first, then files (alphabetically within each group)
            items.sort(
                key=lambda x: (0 if x["type"] == "directory" else 1, x["name"]))

        except Exception as e:
            pass
        return items

    try:
        path = os.path.normpath(relative_workspace_path)

        if not os.path.exists(path):
            return False, ""

        if not os.path.isdir(path):
            return False, ""

        items = _list_dir_recursive(path)
        tree_str = _build_tree_str(items)

        return True, tree_str

    except Exception as e:
        return False, ""
