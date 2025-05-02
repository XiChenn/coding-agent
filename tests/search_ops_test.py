import os
import re
from typing import List, Dict, Any, Tuple, Optional



if __name__ == "__main__":
    # Test the grep search function
    print("Testing basic search for 'def' in Python files:")
    results, success = grep_search("def", include_pattern="*.py")
    print(f"Search success: {success}")
    print(f"Found {len(results)} matches")
    for result in results[:5]:  # Print first 5 results
        print(f"{result['file']}:{result['line_number']}: {result['content'][:50]}...")
        
    # Test case for searching CSS color patterns with regex
    print("\nTesting CSS color search with regex:")
    css_query = r"background-color|background:|backgroundColor|light blue|#add8e6|rgb\(173, 216, 230\)"
    css_results, css_success = grep_search(
        query=css_query,
        case_sensitive=False,
        include_pattern="*.css,*.html,*.js,*.jsx,*.ts,*.tsx"
    )
    print(f"Search success: {css_success}")
    print(f"Found {len(css_results)} matches")
    for result in css_results[:5]:
        print(f"{result['file']}:{result['line_number']}: {result['content'][:50]}...") 