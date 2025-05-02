if __name__ == "__main__":
    # Test delete_file with a temporary file
    temp_file = os.path.join(DEFAULT_WORKING_DIR, "temp_delete_test.txt")

    # Ensure directory exists
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

    # First create a test file
    try:
        with open(temp_file, 'w') as f:
            f.write("This is a test file for deletion testing.")
        logger.info(f"Created test file: {temp_file}")
    except Exception as e:
        logger.error(f"Error creating test file: {str(e)}")
        exit(1)

    # Test if file exists
    if os.path.exists(temp_file):
        logger.info(f"Test file exists: {temp_file}")
    else:
        logger.error(f"Error: Test file does not exist")
        exit(1)

    # Test deleting the file
    delete_result, delete_success = delete_file(temp_file)
    logger.info(f"Delete result: {delete_result}, success: {delete_success}")

    # Verify the file was deleted
    if not os.path.exists(temp_file):
        logger.info("File was successfully deleted")
    else:
        logger.error("Error: File was not deleted")

    # Test deleting a non-existent file
    delete_result, delete_success = delete_file("non_existent_file.txt")
    logger.info(
        f"Delete non-existent file result: {delete_result}, success: {delete_success}")
