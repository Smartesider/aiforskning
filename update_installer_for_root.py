#!/usr/bin/env python3
"""Script to update the installer for root compatibility"""

import re

def update_installer():
    """Update install-advanced.sh to support root execution"""
    with open('install-advanced.sh', 'r') as f:
        content = f.read()
    
    # Replace sudo commands with run_privileged (excluding those in strings and comments)
    # This is a simplified replacement - we'll exclude lines that are:
    # 1. In echo statements (quotes)
    # 2. In comments starting with #
    
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        # Skip lines that are comments or echo statements
        stripped = line.strip()
        if stripped.startswith('#') or 'echo' in line and '"' in line:
            updated_lines.append(line)
            continue
            
        # Replace sudo with run_privileged for actual commands
        if 'sudo ' in line and not line.strip().startswith('#'):
            # Replace sudo followed by space with run_privileged
            updated_line = re.sub(r'\bsudo\s+', 'run_privileged ', line)
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)
    
    # Write back
    with open('install-advanced.sh', 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Updated installer for root compatibility")

if __name__ == '__main__':
    update_installer()
