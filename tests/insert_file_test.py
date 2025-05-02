import os
from typing import Tuple



if __name__ == "__main__":
    # Test insert_file with a temporary file
    temp_file = "temp_insert_test.txt"
    
    # Test creating a new file (complete replacement)
    new_content = "This is a test file.\nCreated for testing purposes."
    insert_result, insert_success = insert_file(temp_file, new_content)
    print(f"Create file result: {insert_result}, success: {insert_success}")
    
    # Verify the file was created
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            content = f.read()
        print(f"File content:\n{content}")
    else:
        print("Error: File was not created")
    
    # Test inserting at a specific line
    insert_content = "This line was inserted at position 2.\n"
    insert_result, insert_success = insert_file(temp_file, insert_content, line_number=2)
    print(f"\nInsert at line 2 result: {insert_result}, success: {insert_success}")
    
    # Verify the insertion
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            content = f.read()
        print(f"Updated file content:\n{content}")
    else:
        print("Error: File does not exist")
    
    # Test inserting at the end (beyond current length)
    insert_content = "This line was inserted at the end.\n"
    insert_result, insert_success = insert_file(temp_file, insert_content, line_number=10)
    print(f"\nInsert at line 10 result: {insert_result}, success: {insert_success}")
    
    # Verify the insertion
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            content = f.read()
        print(f"Updated file content:\n{content}")
    else:
        print("Error: File does not exist")
    
    # Clean up - delete the temporary file
    try:
        os.remove(temp_file)
        print(f"\nSuccessfully deleted {temp_file}")
    except Exception as e:
        print(f"Error deleting file: {str(e)}") 