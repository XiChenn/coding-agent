import os
from typing import Tuple

from coding_agent.config import DEFAULT_WORKING_DIR
from coding_agent.logger import setup_logger

# Configure logging
logger = setup_logger("file_operations")



if __name__ == "__main__":
    # Test remove_file with a temporary file
    temp_file = os.path.join(DEFAULT_WORKING_DIR, "temp_remove_test.txt")

    # Ensure directory exists
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)
    
    # Create a test file with numbered lines
    try:
        with open(temp_file, 'w') as f:
            for i in range(1, 11):
                f.write(f"This is line {i} of the test file.\n")
        logger.info(f"Created test file with 10 lines: {temp_file}")
    except Exception as e:
        logger.error(f"Error creating test file: {str(e)}")
        exit(1)
    
    # Show the initial content
    with open(temp_file, 'r') as f:
        content = f.read()
    logger.info(f"Initial file content:\n{content}")
    
    # Test removing specific lines (3-5)
    remove_result, remove_success = remove_file(temp_file, 3, 5)
    logger.info(f"Remove lines 3-5 result: {remove_result}, success: {remove_success}")
    
    # Show the updated content
    with open(temp_file, 'r') as f:
        content = f.read()
    logger.info(f"Updated file content:\n{content}")
    
    # Test removing lines from the start to a specific line
    remove_result, remove_success = remove_file(temp_file, None, 2)
    logger.info(f"\nRemove lines 1-2 result: {remove_result}, success: {remove_success}")
    
    # Show the updated content
    with open(temp_file, 'r') as f:
        content = f.read()
    logger.info(f"Updated file content:\n{content}")
    
    # Test removing lines from a specific line to the end
    remove_result, remove_success = remove_file(temp_file, 3, None)
    logger.info(f"\nRemove lines 3 to end result: {remove_result}, success: {remove_success}")
    
    # Show the updated content
    with open(temp_file, 'r') as f:
        content = f.read()
    logger.info(f"Updated file content:\n{content}")
    
    # Test attempting to delete the entire file (should fail now)
    remove_result, remove_success = remove_file(temp_file)
    logger.info(f"\nAttempt to delete entire file result: {remove_result}, success: {remove_success}")
    
    # Clean up - manually delete the test file
    try:
        os.remove(temp_file)
        logger.info(f"\nManually deleted {temp_file} for cleanup")
    except Exception as e:
        logger.info(f"Error deleting file: {str(e)}")