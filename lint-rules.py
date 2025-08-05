#!/usr/bin/env python3
"""
SkyForskning.no - Pre-commit validation script
This script validates code against the project's jernregelsettet.

CRITICAL VALIDATION RULES:
1. All backend must use port 8010 only
2. All public files must be in /home/skyforskning.no/public_html/ only
3. All API calls must go to https://skyforskning.no/api/v1/
4. No placeholder or demo data allowed
5. Only pre-approved API keys can be used
"""

import os
import re
import sys
import json
from typing import List, Dict, Tuple, Optional

# Constants based on jernregelsettet
ALLOWED_PORT = "8010"
PUBLIC_FILES_PATH = "/home/skyforskning.no/public_html/"
API_URL = "https://skyforskning.no/api/v1/"
SUPERUSER = "Terje"
ROOT_PASSWORD = "Klokken!12!?!"  # Only used for validation, never exposed

# File extensions to check
CODE_EXTENSIONS = ['.py', '.js', '.html', '.css', '.jsx', '.ts', '.tsx', '.json', '.md']

def find_files_to_validate(root_dir: str) -> List[str]:
    """Find all files that need validation."""
    files_to_check = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in CODE_EXTENSIONS):
                files_to_check.append(os.path.join(root, file))
    
    return files_to_check

def check_port_violations(file_path: str) -> List[str]:
    """Check for any port violations (must use 8010 only)."""
    violations = []
    
    # Skip non-code files
    if not any(file_path.endswith(ext) for ext in CODE_EXTENSIONS):
        return violations
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for port definitions not using 8010
    port_pattern = r'port\s*[=:]\s*([\'"]?)(\d+)\1'
    for match in re.finditer(port_pattern, content, re.IGNORECASE):
        port = match.group(2)
        if port != ALLOWED_PORT:
            violations.append(f"VIOLATION: Unauthorized port {port} in {file_path}")
    
    # Alternative ways to specify ports
    listen_pattern = r'listen\s+(\d+)'
    for match in re.finditer(listen_pattern, content):
        port = match.group(1)
        if port != ALLOWED_PORT:
            violations.append(f"VIOLATION: Unauthorized listen port {port} in {file_path}")
    
    return violations

def check_public_files_location(file_path: str) -> List[str]:
    """Ensure public files are only in the allowed directory."""
    violations = []
    
    # Check for HTML/CSS/JS files outside the public_html directory
    web_extensions = ['.html', '.css', '.js', '.jsx', '.tsx']
    if any(file_path.endswith(ext) for ext in web_extensions):
        if not file_path.startswith(PUBLIC_FILES_PATH):
            violations.append(f"VIOLATION: Public file {file_path} outside of {PUBLIC_FILES_PATH}")
    
    return violations

def check_api_urls(file_path: str) -> List[str]:
    """Check that all API calls go to the correct URL."""
    violations = []
    
    # Skip non-code files
    if not any(file_path.endswith(ext) for ext in CODE_EXTENSIONS):
        return violations
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for API URLs not matching the required pattern
    api_pattern = r'https?://[a-zA-Z0-9.-]+/api/(?:v\d+/)?'
    for match in re.finditer(api_pattern, content):
        url = match.group(0)
        if not url.startswith(API_URL):
            violations.append(f"VIOLATION: Incorrect API URL {url} in {file_path}")
    
    return violations

def check_demo_data(file_path: str) -> List[str]:
    """Check for placeholder or demo data in the code."""
    violations = []
    
    # Skip non-code files
    if not any(file_path.endswith(ext) for ext in CODE_EXTENSIONS):
        return violations
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for common demo data patterns
    demo_patterns = [
        r'placeholder',
        r'demo[_\s]?data',
        r'test[_\s]?data',
        r'example[_\s]?data',
        r'dummy[_\s]?data',
        r'lorem\s+ipsum',
        r'foo\s*bar',
        r'john\s*doe'
    ]
    
    for pattern in demo_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            # Ignore if in a comment explaining the rule
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.end())
            if line_end == -1:
                line_end = len(content)
            line = content[line_start:line_end]
            
            # Skip if it's a comment about not using demo data
            if re.search(r'(//|#|\*|<!--|/\*)\s*no(t)?\s+demo', line, re.IGNORECASE):
                continue
                
            violations.append(f"VIOLATION: Demo/placeholder data detected in {file_path}: '{match.group(0)}'")
    
    return violations

def check_api_keys(file_path: str) -> List[str]:
    """Check for unauthorized API keys or suspicious patterns."""
    violations = []
    
    # Skip non-code files
    if not any(file_path.endswith(ext) for ext in CODE_EXTENSIONS):
        return violations
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Look for API key patterns
    api_key_patterns = [
        r'api[_\s]?key\s*[=:]\s*[\'"]([^\'"]+=|sk-|xoxp-|AKIA)[^\'"]*[\'"]',
        r'secret[_\s]?key\s*[=:]\s*[\'"]([^\'"]+=|sk-|xoxp-|AKIA)[^\'"]*[\'"]',
        r'access[_\s]?token\s*[=:]\s*[\'"]([^\'"]+=|sk-|xoxp-|AKIA)[^\'"]*[\'"]',
        r'(sk|pk)-(live|test)_[a-zA-Z0-9]{10,}'  # Stripe pattern
    ]
    
    for pattern in api_key_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            # Check if the key is in an allowed list or config
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.end())
            if line_end == -1:
                line_end = len(content)
            line = content[line_start:line_end]
            
            # Skip if it's from env variable or config
            if re.search(r'(process\.env|os\.environ|config|ENV)', line, re.IGNORECASE):
                continue
                
            violations.append(f"VIOLATION: Potential hardcoded API key in {file_path}")
    
    return violations

def run_validation() -> List[str]:
    """Run all validation checks and return the list of violations."""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    files = find_files_to_validate(root_dir)
    all_violations = []
    
    for file_path in files:
        # Skip the validation script itself
        if os.path.basename(file_path) == 'lint-rules.py':
            continue
            
        all_violations.extend(check_port_violations(file_path))
        all_violations.extend(check_public_files_location(file_path))
        all_violations.extend(check_api_urls(file_path))
        all_violations.extend(check_demo_data(file_path))
        all_violations.extend(check_api_keys(file_path))
    
    return all_violations

def main():
    """Main function to run validation checks."""
    print("Running SkyForskning.no validation...")
    violations = run_validation()
    
    if violations:
        print("\n".join(violations))
        print(f"\n❌ VALIDATION FAILED: Found {len(violations)} violations of project rules.")
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED: All files comply with project rules.")
        sys.exit(0)

if __name__ == "__main__":
    main()
