#!/usr/bin/env python3
"""
DEL-007 RED Phase Test Runner
Runs all TDD RED phase tests to verify they fail as expected.
These tests are designed to drive implementation of DEL-007.
"""

import sys
import subprocess
from pathlib import Path

def run_red_phase_tests():
    """Run all RED phase tests and report results."""
    print("🔴 DEL-007 TDD RED PHASE TEST RUNNER")
    print("=" * 50)
    print("Running all RED phase tests to verify they fail as expected.")
    print("These tests will drive the GREEN phase implementation.")
    print()
    
    test_files = [
        "test_validation_script.py",
        "test_setup_script.py", 
        "test_validation_integration.py",
        "test_validation_performance.py",
        "test_validation_security.py"
    ]
    
    results = {}
    total_tests = 0
    total_failures = 0
    
    for test_file in test_files:
        print(f"Running {test_file}...")
        print("-" * 30)
        
        try:
            # Run pytest on individual test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--no-header",
                "--quiet"
            ], 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
            )
            
            results[test_file] = {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            # Count tests and failures from output
            stdout_lines = result.stdout.split('\n')
            for line in stdout_lines:
                if 'failed' in line and 'passed' in line:
                    # Parse pytest summary line like "5 failed, 0 passed in 0.12s"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'failed':
                            try:
                                failures = int(parts[i-1])
                                total_failures += failures
                            except (ValueError, IndexError):
                                pass
                        elif part == 'passed':
                            try:
                                passed = int(parts[i-1])
                                total_tests += passed
                            except (ValueError, IndexError):
                                pass
                elif 'FAILED' in line or 'ERROR' in line:
                    total_tests += 1
                    if result.returncode != 0:
                        total_failures += 1
            
            print(f"✅ {test_file} completed (exit code: {result.returncode})")
            
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            results[test_file] = {'error': str(e)}
        
        print()
    
    print("🔴 RED PHASE SUMMARY")
    print("=" * 30)
    print(f"Test files run: {len(test_files)}")
    print(f"Expected result: ALL TESTS SHOULD FAIL")
    print(f"(This proves tests are driving implementation)")
    print()
    
    for test_file, result in results.items():
        if 'error' in result:
            print(f"❌ {test_file}: ERROR - {result['error']}")
        elif result['returncode'] != 0:
            print(f"🔴 {test_file}: FAILED (as expected)")
        else:
            print(f"🟢 {test_file}: PASSED (unexpected - check implementation)")
    
    print()
    print("📋 NEXT STEPS:")
    print("1. All tests should be failing (RED phase complete)")
    print("2. Proceed to GREEN phase: implement minimal functionality")
    print("3. Make tests pass one by one")
    print("4. Refactor and optimize in REFACTOR phase")
    print()
    
    # RED phase should have failures - that's the point!
    if total_failures > 0:
        print(f"✅ RED phase complete: {total_failures} tests failing as expected")
        print("🟢 Ready to proceed to GREEN phase implementation")
    else:
        print("⚠️  Warning: No test failures detected")
        print("   Either tests are not comprehensive enough")
        print("   Or implementation already exists")
    
    return results

if __name__ == '__main__':
    results = run_red_phase_tests()
    
    # Exit with success even if tests fail (RED phase expectation)
    sys.exit(0)