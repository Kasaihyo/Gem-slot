#\!/usr/bin/env python3
"""Run tests to ensure compatibility with Python 3.12."""

import sys
import subprocess
import os

def check_python_version():
    """Ensure we're running Python 3.12+."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 12):
        print("ERROR: Python 3.12 or higher is required")
        sys.exit(1)
    
    print("✓ Python version check passed")

def run_tests():
    """Run the test suite."""
    print("\nRunning tests...")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def check_imports():
    """Check that all modules can be imported."""
    print("\nChecking imports...")
    
    modules = [
        "simulator.config",
        "simulator.core.rng",
        "simulator.core.symbol",
        "simulator.core.grid",
        "simulator.core.union_find",
        "simulator.core.clusters"
    ]
    
    for module in modules:
        try:
            exec(f"import {module}")
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    
    return True

def main():
    """Main test runner."""
    print("=== Python 3.12 Compatibility Test ===\n")
    
    # Check Python version
    check_python_version()
    
    # Check imports
    if not check_imports():
        print("\n❌ Import check failed")
        sys.exit(1)
    
    print("\n✓ All imports successful")
    
    # Run tests
    if not run_tests():
        print("\n❌ Tests failed")
        sys.exit(1)
    
    print("\n✅ All tests passed\!")

if __name__ == "__main__":
    main()
EOF < /dev/null