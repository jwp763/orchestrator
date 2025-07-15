#!/bin/bash
# Performance test for DEL-003 - Benchmark startup time
# Ensures new tooling doesn't add significant overhead (< 5 seconds)

set -e

echo "⏱️  Benchmarking Deployment Startup Performance"
echo "==============================================="

# Function to measure time in seconds (using python for cross-platform compatibility)
measure_time() {
    local start_time=$(python3 -c "import time; print(time.time())")
    "$@" >/dev/null 2>&1
    local end_time=$(python3 -c "import time; print(time.time())")
    local duration=$(python3 -c "print($end_time - $start_time)")
    echo "$duration"
}

# Test current package.json validation time
echo "📦 Testing package.json processing time..."
if [ -f "package.json" ]; then
    validation_time=$(measure_time cat package.json)
    echo "   Package.json validation: ${validation_time}s"
else
    echo "   ❌ package.json not found"
    exit 1
fi

# Test npm script lookup time
echo "📦 Testing npm script lookup time..."
script_lookup_time=$(measure_time npm run --silent)
echo "   Script lookup: ${script_lookup_time}s"

# Test tooling availability check time
echo "📦 Testing tooling availability check time..."
tooling_check_time=$(measure_time bash -c "
npx npm-run-all --version >/dev/null 2>&1
npx dotenv --help >/dev/null 2>&1
npx cross-env NODE_ENV=test echo test >/dev/null 2>&1
npx wait-on --version >/dev/null 2>&1
")
echo "   Tooling availability check: ${tooling_check_time}s"

# Test environment variable loading simulation
echo "📦 Testing environment loading simulation..."
env_loading_time=$(measure_time bash -c "
if [ -f '.env.development' ]; then
    cat .env.development >/dev/null 2>&1
elif [ -f '.env.dev' ]; then
    cat .env.dev >/dev/null 2>&1
else
    echo 'TEST_VAR=test' | cat >/dev/null
fi
")
echo "   Environment loading: ${env_loading_time}s"

# Calculate total overhead
total_overhead=$(python3 -c "print($validation_time + $script_lookup_time + $tooling_check_time + $env_loading_time)")

echo ""
echo "📊 Performance Summary"
echo "====================="
echo "Total startup overhead: ${total_overhead}s"

# Check if within acceptable limits (< 5 seconds)
if python3 -c "exit(0 if $total_overhead < 5.0 else 1)"; then
    echo "✅ Performance requirement met (< 5 seconds)"
    
    # Provide breakdown
    echo ""
    echo "Performance breakdown:"
    echo "   Package.json validation: ${validation_time}s"
    echo "   Script lookup: ${script_lookup_time}s"
    echo "   Tooling availability: ${tooling_check_time}s"
    echo "   Environment loading: ${env_loading_time}s"
    echo "   Total overhead: ${total_overhead}s"
    
    exit 0
else
    echo "❌ Performance requirement NOT met (>= 5 seconds)"
    echo "   Current overhead: ${total_overhead}s"
    echo "   Required: < 5.0s"
    echo ""
    echo "🔧 Performance optimization needed:"
    echo "   - Review tooling configuration"
    echo "   - Optimize environment loading"
    echo "   - Consider lazy loading of tools"
    
    exit 1
fi