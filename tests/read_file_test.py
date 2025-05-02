import os
from typing import Tuple, Optional



if __name__ == "__main__":
    # Create a path to the dummy text file
    dummy_file = "dummy_text.txt"
    
    # Test if dummy file exists
    if not os.path.exists(dummy_file):
        print(f"Dummy file {dummy_file} not found. Please create it first.")
        exit(1)
    
    # Test reading entire file with just the target file
    content, success = read_file(dummy_file)
    print(f"Read entire file with default parameters: success={success}")
    print(f"Content preview: {content[:150]}..." if len(content) > 150 else f"Content: {content}")
    
    # Test reading entire file explicitly
    content, success = read_file(dummy_file, should_read_entire_file=True)
    print(f"\nRead entire file explicitly: success={success}")
    print(f"Content preview: {content[:150]}..." if len(content) > 150 else f"Content: {content}")
    
    # Test reading specific lines
    content, success = read_file(dummy_file, 2, 4)
    print(f"\nRead lines 2-4: success={success}")
    print(f"Content:\n{content}")
    
    # Test reading with invalid parameters
    content, success = read_file(dummy_file, 0, 5)
    print(f"\nRead with invalid start line: success={success}")
    print(f"Message: {content}")
    
    # Test reading non-existent file
    content, success = read_file("non_existent_file.txt")
    print(f"\nRead non-existent file: success={success}")
    print(f"Message: {content}") 