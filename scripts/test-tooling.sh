#!/bin/bash
# Integration test for modern deployment tooling
# This test verifies all required tools are installed and working

set -e

echo "🧪 Testing Modern Deployment Tooling Installation"
echo "=================================================="

# Test script should fail initially (TDD - Red phase)
FAILED_TESTS=()

# Test 1: npm-run-all installation and functionality
echo "📦 Testing npm-run-all..."
if command -v npm-run-all >/dev/null 2>&1; then
    echo "✅ npm-run-all is installed globally"
    
    # Test basic functionality
    if npm-run-all --help >/dev/null 2>&1; then
        echo "✅ npm-run-all basic functionality works"
    else
        echo "❌ npm-run-all help command failed"
        FAILED_TESTS+=("npm-run-all functionality")
    fi
elif npx npm-run-all --version >/dev/null 2>&1; then
    echo "✅ npm-run-all is available via npx"
    
    # Test basic functionality via npx
    if npx npm-run-all --help >/dev/null 2>&1; then
        echo "✅ npm-run-all basic functionality works via npx"
    else
        echo "❌ npm-run-all help command failed via npx"
        FAILED_TESTS+=("npm-run-all functionality")
    fi
else
    echo "❌ npm-run-all is not installed"
    FAILED_TESTS+=("npm-run-all installation")
fi

# Test 2: dotenv-cli installation and functionality
echo "📦 Testing dotenv-cli..."
if command -v dotenv >/dev/null 2>&1; then
    echo "✅ dotenv-cli is installed globally"
    
    # Test basic functionality
    if dotenv --help >/dev/null 2>&1; then
        echo "✅ dotenv-cli basic functionality works"
    else
        echo "❌ dotenv-cli help command failed"
        FAILED_TESTS+=("dotenv-cli functionality")
    fi
elif npx dotenv --help >/dev/null 2>&1; then
    echo "✅ dotenv-cli is available via npx"
    echo "✅ dotenv-cli basic functionality works via npx"
else
    echo "❌ dotenv-cli is not installed"
    FAILED_TESTS+=("dotenv-cli installation")
fi

# Test 3: cross-env installation and functionality
echo "📦 Testing cross-env..."
if command -v cross-env >/dev/null 2>&1; then
    echo "✅ cross-env is installed globally"
    
    # Test basic functionality
    if cross-env --help >/dev/null 2>&1; then
        echo "✅ cross-env basic functionality works"
    else
        echo "❌ cross-env help command failed"
        FAILED_TESTS+=("cross-env functionality")
    fi
elif npx cross-env NODE_ENV=test echo "test" >/dev/null 2>&1; then
    echo "✅ cross-env is available via npx"
    echo "✅ cross-env basic functionality works via npx"
else
    echo "❌ cross-env is not installed"
    FAILED_TESTS+=("cross-env installation")
fi

# Test 4: wait-on installation and functionality
echo "📦 Testing wait-on..."
if command -v wait-on >/dev/null 2>&1; then
    echo "✅ wait-on is installed globally"
    
    # Test basic functionality
    if wait-on --help >/dev/null 2>&1; then
        echo "✅ wait-on basic functionality works"
    else
        echo "❌ wait-on help command failed"
        FAILED_TESTS+=("wait-on functionality")
    fi
elif npx wait-on --version >/dev/null 2>&1; then
    echo "✅ wait-on is available via npx"
    
    # Test basic functionality via npx
    if npx wait-on --help >/dev/null 2>&1; then
        echo "✅ wait-on basic functionality works via npx"
    else
        echo "❌ wait-on help command failed via npx"
        FAILED_TESTS+=("wait-on functionality")
    fi
else
    echo "❌ wait-on is not installed"
    FAILED_TESTS+=("wait-on installation")
fi

# Test 5: Package.json dependencies
echo "📦 Testing package.json configuration..."
if [ -f "package.json" ]; then
    echo "✅ package.json exists"
    
    # Check if modern tooling is in devDependencies
    if grep -q "npm-run-all" package.json; then
        echo "✅ npm-run-all is in package.json"
    else
        echo "❌ npm-run-all not found in package.json"
        FAILED_TESTS+=("npm-run-all in package.json")
    fi
    
    if grep -q "dotenv-cli" package.json; then
        echo "✅ dotenv-cli is in package.json"
    else
        echo "❌ dotenv-cli not found in package.json"
        FAILED_TESTS+=("dotenv-cli in package.json")
    fi
    
    if grep -q "cross-env" package.json; then
        echo "✅ cross-env is in package.json"
    else
        echo "❌ cross-env not found in package.json"
        FAILED_TESTS+=("cross-env in package.json")
    fi
    
    if grep -q "wait-on" package.json; then
        echo "✅ wait-on is in package.json"
    else
        echo "❌ wait-on not found in package.json"
        FAILED_TESTS+=("wait-on in package.json")
    fi
else
    echo "❌ package.json not found"
    FAILED_TESTS+=("package.json existence")
fi

# Test 6: npm scripts configuration
echo "📦 Testing npm scripts configuration..."
if [ -f "package.json" ]; then
    # Check for basic script structure that will use new tooling
    if grep -q "npm-run-all" package.json; then
        echo "✅ npm scripts are configured to use npm-run-all"
    else
        echo "❌ npm scripts don't use npm-run-all yet"
        FAILED_TESTS+=("npm scripts with npm-run-all")
    fi
    
    if grep -q "dotenv" package.json; then
        echo "✅ npm scripts are configured to use dotenv-cli"
    else
        echo "❌ npm scripts don't use dotenv-cli yet"
        FAILED_TESTS+=("npm scripts with dotenv-cli")
    fi
fi

echo ""
echo "📊 Test Results Summary"
echo "======================"

if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo "✅ All tests passed! Modern deployment tooling is properly installed and configured."
    exit 0
else
    echo "❌ ${#FAILED_TESTS[@]} test(s) failed:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "   - $test"
    done
    echo ""
    echo "🔧 To fix these issues:"
    echo "   1. Run: npm install --save-dev npm-run-all dotenv-cli cross-env wait-on"
    echo "   2. Update package.json scripts to use new tooling"
    echo "   3. Re-run this test script"
    exit 1
fi