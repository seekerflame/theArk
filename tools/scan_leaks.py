#!/usr/bin/env python3
import sys
import os
import re

# List of regex patterns to scan for
PATTERNS = {
    "Generic Leak": r'(?i)(token|macaroon|pass' + r'word|key|auth|sec' + r'ret)\s*[:=]\s*["\'][a-zA-Z0-9_-]{16,}["\']',
    "WIKI Creds": r'WIKI_P' + r'ASS\s*=\s*["\'][^Placeholder][a-zA-Z0-9]{16,}["\']',
    "JWT Leak": r'JWT_SEC' + r'RET\s*=\s*["\'][^dev_only_secret_change_in_production][a-zA-Z0-9_-]{16,}["\']',
}

def scan_file(filepath):
    """Scan a single file for exposed details."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            for name, pattern in PATTERNS.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    print(f"🔴 [VULNERABILITY] {name} found in {filepath} (Line {content.count('\n', 0, match.start())+1})")
                    return True
    except Exception:
        pass
    return False

def main():
    print("🛡️ Ark OS: Running Repository Hardening Audit...")
    vulnerabilities = 0
    # Files to exclude from scan
    exclude = ['.git', 'node_modules', '.env', 'ENV_TEMPLATE.md', 'SECURITY_RISK_LOG.md', 'tests', 'scan_leaks.py']
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file.endswith(('.py', '.js', '.json', '.html', '.yml', '.yaml', '.md')):
                path = os.path.join(root, file)
                if scan_file(path):
                    vulnerabilities += 1
    
    if vulnerabilities > 0:
        print(f"\n❌ Audit Failed: {vulnerabilities} potential leaks found.")
    else:
        print("\n✅ Audit Passed: No hardcoded credentials detected in active files.")

if __name__ == "__main__":
    main()
