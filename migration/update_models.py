#!/usr/bin/env python3
"""
Helper script to update Pydantic models to v2 syntax
Usage: python update_models.py <directory>
"""

import os
import re
import argparse
from typing import List, Dict

# Common patterns to search for
PATTERNS = {
    "validator": {
        "search": r"@validator\(['\"](.*?)['\"](.*?)\)",
        "replace": r"@field_validator(['\"]\\1['\"]\2)"
    },
    "config_class": {
        "search": r"class Config:([^}]*?)",
        "replace": r"model_config = ConfigDict(\1)"
    },
    "dict_method": {
        "search": r"\.dict\(",
        "replace": r".model_dump("
    },
    "orm_mode": {
        "search": r"orm_mode\s*=\s*True",
        "replace": r"from_attributes=True"
    }
}

def update_file(file_path: str) -> Dict[str, int]:
    """Update a Python file with Pydantic v2 syntax"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    counts = {pattern: 0 for pattern in PATTERNS}
    
    # Add required imports if needed
    if "from pydantic import " in content and "ConfigDict" not in content:
        content = re.sub(
            r"from pydantic import (.*)",
            r"from pydantic import \1, ConfigDict",
            content
        )
    
    # Apply search and replace patterns
    for pattern_name, pattern_info in PATTERNS.items():
        matches = re.findall(pattern_info["search"], content)
        counts[pattern_name] = len(matches)
        content = re.sub(pattern_info["search"], pattern_info["replace"], content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return counts

def find_pydantic_files(directory: str) -> List[str]:
    """Find Python files that likely contain Pydantic models"""
    pydantic_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            
            # Read the file to check for Pydantic usage
            with open(file_path, 'r') as f:
                content = f.read()
                
            if "from pydantic import " in content and "BaseModel" in content:
                pydantic_files.append(file_path)
    
    return pydantic_files

def main():
    parser = argparse.ArgumentParser(description="Update Pydantic models to v2 syntax")
    parser.add_argument("directory", help="Directory to recursively search for Pydantic models")
    args = parser.parse_args()
    
    print(f"Searching for Pydantic models in {args.directory}...")
    
    files = find_pydantic_files(args.directory)
    print(f"Found {len(files)} files with Pydantic models")
    
    for file_path in files:
        print(f"\nUpdating {file_path}...")
        counts = update_file(file_path)
        
        for pattern, count in counts.items():
            if count > 0:
                print(f"  - Updated {count} instances of {pattern}")
    
    print("\nDone! Please review the changes manually to ensure correctness.")

if __name__ == "__main__":
    main() 