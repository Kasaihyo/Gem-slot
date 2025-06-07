#!/usr/bin/env python3
"""Simple test runner for the project."""

import sys
import subprocess


def main():
    """Run all tests."""
    print("Running Esqueleto Explosivo 3 Tests...")
    print("=" * 50)
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short"
    ])
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())