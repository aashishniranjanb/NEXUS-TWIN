"""
NEXUS-TWIN Automated Test Runner.
Executes all unit, contract, API, ML, and scenario engine tests across the project.
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("  Running NEXUS-TWIN Comprehensive Test Suite")
    print("=" * 60)

    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n[SUCCESS] All NEXUS-TWIN test suites passed cleanly!")
    else:
        print(f"\n[FAILURE] Test suite exited with status code {result.returncode}")

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
