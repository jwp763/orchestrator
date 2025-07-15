#!/bin/bash
# Tooling validation script for DEL-003
# Validates that all required deployment tooling is correctly installed and configured

set -e

echo "🔍 Validating Modern Deployment Tooling"
echo "========================================"

VALIDATION_ERRORS=()

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a package is in package.json
package_in_json() {
    if [ -f "package.json" ]; then
        grep -q "\"$1\"" package.json
    else
        return 1
    fi
}

# Validate npm-run-all
echo "🔧 Validating npm-run-all..."
if command_exists npm-run-all; then
    echo "  ✅ npm-run-all command available globally"
    
    # Test basic functionality
    if npm-run-all --version >/dev/null 2>&1; then
        echo "  ✅ npm-run-all version check passed"
    else
        VALIDATION_ERRORS+=("npm-run-all version check failed")
    fi
    
    # Test parallel execution capability
    if npm-run-all --help | grep -q "parallel"; then
        echo "  ✅ npm-run-all supports parallel execution"
    else
        VALIDATION_ERRORS+=("npm-run-all parallel support not found")
    fi
elif npx npm-run-all --version >/dev/null 2>&1; then
    echo "  ✅ npm-run-all available via npx"
    
    # Test parallel execution capability via npx
    if npx npm-run-all --help | grep -q "parallel"; then
        echo "  ✅ npm-run-all supports parallel execution"
    else
        VALIDATION_ERRORS+=("npm-run-all parallel support not found")
    fi
else
    VALIDATION_ERRORS+=("npm-run-all command not found")
fi

if package_in_json "npm-run-all"; then
    echo "  ✅ npm-run-all found in package.json"
else
    VALIDATION_ERRORS+=("npm-run-all not in package.json")
fi

# Validate dotenv-cli
echo "🔧 Validating dotenv-cli..."
if command_exists dotenv; then
    echo "  ✅ dotenv-cli command available"
    
    # Test basic functionality
    if dotenv --version >/dev/null 2>&1; then
        echo "  ✅ dotenv-cli version check passed"
    else
        VALIDATION_ERRORS+=("dotenv-cli version check failed")
    fi
    
    # Test environment file loading capability
    if dotenv --help | grep -q "\-e"; then
        echo "  ✅ dotenv-cli supports environment file loading"
    else
        VALIDATION_ERRORS+=("dotenv-cli environment file support not found")
    fi
else
    VALIDATION_ERRORS+=("dotenv-cli command not found")
fi

if package_in_json "dotenv-cli"; then
    echo "  ✅ dotenv-cli found in package.json"
else
    VALIDATION_ERRORS+=("dotenv-cli not in package.json")
fi

# Validate cross-env
echo "🔧 Validating cross-env..."
if command_exists cross-env; then
    echo "  ✅ cross-env command available globally"
    
    # Test cross-platform environment variable setting
    if cross-env NODE_ENV=test echo "test" >/dev/null 2>&1; then
        echo "  ✅ cross-env environment variable setting works"
    else
        VALIDATION_ERRORS+=("cross-env environment variable setting failed")
    fi
elif npx cross-env NODE_ENV=test echo "test" >/dev/null 2>&1; then
    echo "  ✅ cross-env available via npx"
    echo "  ✅ cross-env environment variable setting works"
else
    VALIDATION_ERRORS+=("cross-env command not found")
fi

if package_in_json "cross-env"; then
    echo "  ✅ cross-env found in package.json"
else
    VALIDATION_ERRORS+=("cross-env not in package.json")
fi

# Validate wait-on
echo "🔧 Validating wait-on..."
if command_exists wait-on; then
    echo "  ✅ wait-on command available globally"
    
    # Test basic functionality
    if wait-on --version >/dev/null 2>&1; then
        echo "  ✅ wait-on version check passed"
    else
        VALIDATION_ERRORS+=("wait-on version check failed")
    fi
    
    # Test help output for expected features
    if wait-on --help | grep -q "tcp:"; then
        echo "  ✅ wait-on supports TCP port waiting"
    else
        VALIDATION_ERRORS+=("wait-on TCP support not found")
    fi
elif npx wait-on --version >/dev/null 2>&1; then
    echo "  ✅ wait-on available via npx"
    
    # Test help output for expected features via npx
    if npx wait-on --help | grep -q "tcp:"; then
        echo "  ✅ wait-on supports TCP port waiting"
    else
        VALIDATION_ERRORS+=("wait-on TCP support not found")
    fi
else
    VALIDATION_ERRORS+=("wait-on command not found")
fi

if package_in_json "wait-on"; then
    echo "  ✅ wait-on found in package.json"
else
    VALIDATION_ERRORS+=("wait-on not in package.json")
fi

# Validate package.json structure
echo "🔧 Validating package.json structure..."
if [ -f "package.json" ]; then
    echo "  ✅ package.json exists"
    
    # Check if devDependencies section exists
    if grep -q "devDependencies" package.json; then
        echo "  ✅ devDependencies section found"
    else
        VALIDATION_ERRORS+=("devDependencies section not found in package.json")
    fi
    
    # Check if scripts section exists
    if grep -q "scripts" package.json; then
        echo "  ✅ scripts section found"
    else
        VALIDATION_ERRORS+=("scripts section not found in package.json")
    fi
else
    VALIDATION_ERRORS+=("package.json file not found")
fi

# Validate Node.js and npm versions
echo "🔧 Validating Node.js environment..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js version: $NODE_VERSION"
    
    # Check if Node.js version is recent enough (v16+)
    if node -e "process.exit(process.version.match(/^v(\d+)/)[1] >= 16 ? 0 : 1)"; then
        echo "  ✅ Node.js version is compatible (v16+)"
    else
        VALIDATION_ERRORS+=("Node.js version is too old (requires v16+)")
    fi
else
    VALIDATION_ERRORS+=("Node.js not found")
fi

if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo "  ✅ npm version: $NPM_VERSION"
else
    VALIDATION_ERRORS+=("npm not found")
fi

echo ""
echo "📊 Validation Results"
echo "===================="

if [ ${#VALIDATION_ERRORS[@]} -eq 0 ]; then
    echo "✅ All validations passed! Modern deployment tooling is properly installed and configured."
    echo ""
    echo "🎉 Ready to proceed with deployment improvements!"
    echo "   - npm-run-all: Service orchestration"
    echo "   - dotenv-cli: Environment variable management"
    echo "   - cross-env: Cross-platform compatibility"
    echo "   - wait-on: Service dependency management"
    exit 0
else
    echo "❌ ${#VALIDATION_ERRORS[@]} validation error(s) found:"
    for error in "${VALIDATION_ERRORS[@]}"; do
        echo "   - $error"
    done
    echo ""
    echo "🔧 To fix these issues:"
    echo "   1. Ensure Node.js v16+ is installed"
    echo "   2. Run: npm install --save-dev npm-run-all dotenv-cli cross-env wait-on"
    echo "   3. Verify package.json has proper structure"
    echo "   4. Re-run this validation script"
    exit 1
fi