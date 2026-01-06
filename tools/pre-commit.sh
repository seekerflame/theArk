#!/bin/bash
# Pre-commit hook to prevent secret exposure
# Install: cp pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

echo "🔒 Security scan running..."

# Patterns that should NEVER be committed
FORBIDDEN_PATTERNS=(
    "rnd_[a-zA-Z0-9]"
    "sk_live_"
    "sk_test_"
    "RENDER_API_KEY="
    "JWT_SECRET="
    "password.*=.*['\"]"
    "secret.*=.*['\"]"
)

# Files to check
FILES=$(git diff --cached --name-only --diff-filter=ACM)

FOUND=0

for file in $FILES; do
    if [[ -f "$file" ]]; then
        for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
            if grep -qE "$pattern" "$file" 2>/dev/null; then
                echo "❌ BLOCKED: Secret pattern found in $file"
                echo "   Pattern: $pattern"
                FOUND=1
            fi
        done
    fi
done

if [ $FOUND -eq 1 ]; then
    echo ""
    echo "⛔ COMMIT BLOCKED - Secrets detected!"
    echo "Remove secrets and use environment variables instead."
    echo ""
    exit 1
fi

echo "✅ No secrets detected. Commit allowed."
exit 0
