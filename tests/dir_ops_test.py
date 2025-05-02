import os
from typing import List, Dict, Any, Tuple



if __name__ == "__main__":
    # Test the list_dir function
    success, tree_str = list_dir("../..")
    print(f"Directory listing success: {success}")
    
    # Print tree visualization
    print("\nDirectory Tree:")
    print(tree_str) 