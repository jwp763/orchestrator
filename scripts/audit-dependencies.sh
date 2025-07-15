#!/bin/bash
# Security audit script for DEL-003
# Audits new deployment tooling dependencies for vulnerabilities

set -e

echo "🔒 Security Audit for Modern Deployment Tooling"
echo "================================================"

AUDIT_FAILURES=()

# Check if npm audit is available
if ! command -v npm >/dev/null 2>&1; then
    echo "❌ npm not found - cannot perform security audit"
    exit 1
fi

echo "🔍 Running npm audit..."
if npm audit --json > /tmp/audit-results.json 2>/dev/null; then
    echo "✅ npm audit completed successfully"
    
    # Check for high and critical vulnerabilities
    HIGH_VULNS=$(cat /tmp/audit-results.json | jq -r '.metadata.vulnerabilities.high // 0' 2>/dev/null || echo "0")
    CRITICAL_VULNS=$(cat /tmp/audit-results.json | jq -r '.metadata.vulnerabilities.critical // 0' 2>/dev/null || echo "0")
    
    echo "   Critical vulnerabilities: $CRITICAL_VULNS"
    echo "   High vulnerabilities: $HIGH_VULNS"
    
    if [ "$CRITICAL_VULNS" -gt 0 ]; then
        AUDIT_FAILURES+=("$CRITICAL_VULNS critical vulnerabilities found")
    fi
    
    if [ "$HIGH_VULNS" -gt 0 ]; then
        AUDIT_FAILURES+=("$HIGH_VULNS high vulnerabilities found")
    fi
    
    # Clean up
    rm -f /tmp/audit-results.json
else
    echo "⚠️  npm audit failed or returned warnings"
    # Try without --json for readable output
    echo "Running simplified audit..."
    if npm audit 2>&1 | grep -q "vulnerabilities"; then
        AUDIT_FAILURES+=("npm audit found vulnerabilities (check manually)")
    fi
fi

# Check specific packages for known issues
echo ""
echo "🔍 Checking specific package security..."

PACKAGES=("npm-run-all" "dotenv-cli" "cross-env" "wait-on")

for package in "${PACKAGES[@]}"; do
    echo "   Checking $package..."
    
    # Check if package exists in package.json
    if [ -f "package.json" ] && grep -q "\"$package\"" package.json; then
        echo "     ✅ $package found in package.json"
        
        # Get package version if possible
        if command -v npm >/dev/null 2>&1; then
            VERSION=$(npm list "$package" --depth=0 2>/dev/null | grep "$package" | sed 's/.*@//' | sed 's/ .*//' || echo "unknown")
            echo "     📦 Version: $VERSION"
        fi
    else
        echo "     ⚠️  $package not found in package.json"
    fi
done

# Check for package-lock.json integrity
echo ""
echo "🔍 Checking package-lock.json integrity..."
if [ -f "package-lock.json" ]; then
    echo "   ✅ package-lock.json exists"
    
    # Check if it's valid JSON
    if jq . package-lock.json >/dev/null 2>&1; then
        echo "   ✅ package-lock.json is valid JSON"
    else
        AUDIT_FAILURES+=("package-lock.json is invalid JSON")
    fi
    
    # Check if lock file is up to date
    if npm ls >/dev/null 2>&1; then
        echo "   ✅ package-lock.json is consistent with package.json"
    else
        AUDIT_FAILURES+=("package-lock.json may be inconsistent with package.json")
    fi
else
    echo "   ⚠️  package-lock.json not found (recommended for security)"
fi

# Check Node.js version for security
echo ""
echo "🔍 Checking Node.js security..."
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo "   📦 Node.js version: $NODE_VERSION"
    
    # Extract major version number
    MAJOR_VERSION=$(echo "$NODE_VERSION" | sed 's/v//' | cut -d. -f1)
    
    # Check if it's a supported LTS version (18, 20, or newer)
    if [ "$MAJOR_VERSION" -ge 18 ]; then
        echo "   ✅ Node.js version is supported and receives security updates"
    elif [ "$MAJOR_VERSION" -ge 16 ]; then
        echo "   ⚠️  Node.js version is older but still supported"
    else
        AUDIT_FAILURES+=("Node.js version is outdated and may have security vulnerabilities")
    fi
else
    AUDIT_FAILURES+=("Node.js not found")
fi

# Check npm version for security
if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm --version)
    echo "   📦 npm version: $NPM_VERSION"
    
    # Extract major version
    NPM_MAJOR=$(echo "$NPM_VERSION" | cut -d. -f1)
    
    if [ "$NPM_MAJOR" -ge 8 ]; then
        echo "   ✅ npm version is recent and secure"
    else
        AUDIT_FAILURES+=("npm version is outdated")
    fi
fi

# Check for .npmrc configuration security
echo ""
echo "🔍 Checking npm configuration security..."
if [ -f ".npmrc" ]; then
    echo "   📦 .npmrc file found"
    
    # Check for insecure registry configurations
    if grep -q "http://" .npmrc 2>/dev/null; then
        AUDIT_FAILURES+=(".npmrc contains insecure HTTP registry URLs")
    else
        echo "   ✅ .npmrc appears secure (no HTTP registries)"
    fi
else
    echo "   ✅ No .npmrc file (using npm defaults)"
fi

echo ""
echo "📊 Security Audit Results"
echo "========================="

if [ ${#AUDIT_FAILURES[@]} -eq 0 ]; then
    echo "✅ Security audit passed! No critical security issues found."
    echo ""
    echo "🔒 Security recommendations:"
    echo "   - Keep dependencies updated regularly"
    echo "   - Run 'npm audit' periodically"
    echo "   - Consider using 'npm audit fix' for automatic fixes"
    echo "   - Review package-lock.json changes in pull requests"
    
    exit 0
else
    echo "❌ Security audit found ${#AUDIT_FAILURES[@]} issue(s):"
    for failure in "${AUDIT_FAILURES[@]}"; do
        echo "   - $failure"
    done
    echo ""
    echo "🔧 Security remediation steps:"
    echo "   1. Run 'npm audit fix' to automatically fix issues"
    echo "   2. Manually review and update vulnerable packages"
    echo "   3. Update Node.js and npm to latest LTS versions"
    echo "   4. Re-run this security audit"
    
    exit 1
fi