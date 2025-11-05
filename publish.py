#!/usr/bin/env python3
"""Script to publish connectlife-cloud package to PyPI."""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    """Main function to publish the package."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Check if we're in the right directory
    if not (script_dir / "setup.py").exists():
        print("Error: setup.py not found. Please run this script from the connectlife_cloud directory.")
        sys.exit(1)
    
    # Clean previous builds
    print("Cleaning previous builds...")
    run_command("rm -rf build/ dist/ *.egg-info/", cwd=script_dir)
    
    # Build the package
    print("Building package...")
    run_command("python -m build", cwd=script_dir)
    
    # Check the package
    print("Checking package...")
    run_command("python -m twine check dist/*", cwd=script_dir)
    
    # Upload to PyPI (test first)
    print("Uploading to PyPI test...")
    run_command("python -m twine upload --repository testpypi dist/*", cwd=script_dir)
    
    print("Package uploaded to PyPI test successfully!")
    print("To upload to production PyPI, run:")
    print("python -m twine upload dist/*")

if __name__ == "__main__":
    main()
