#!/usr/bin/env python3
"""Script to publish connectlife-cloud package to PyPI."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
import re

def get_version():
    """Get version from pyproject.toml or setup.py."""
    script_dir = Path(__file__).parent
    
    # Try pyproject.toml first
    pyproject_path = script_dir / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    
    # Fallback to setup.py
    setup_path = script_dir / "setup.py"
    if setup_path.exists():
        with open(setup_path, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    
    return None

def clean_build_dirs(script_dir):
    """Clean previous build directories (cross-platform)."""
    dirs_to_remove = ["build", "dist"]
    patterns_to_remove = ["*.egg-info"]
    
    for dir_name in dirs_to_remove:
        dir_path = script_dir / dir_name
        if dir_path.exists():
            print(f"Removing {dir_path}...")
            shutil.rmtree(dir_path)
    
    # Remove egg-info directories
    for egg_info in script_dir.glob("*.egg-info"):
        if egg_info.is_dir():
            print(f"Removing {egg_info}...")
            shutil.rmtree(egg_info)

def check_and_upgrade_tools():
    """Check and upgrade build tools to avoid metadata issues."""
    print("\n🔧 Checking build tools...")
    tools = ["setuptools>=65.0", "wheel>=0.37.0", "twine>=4.0.0", "build>=0.10.0", "packaging>=21.0"]
    print("Upgrading build tools to ensure compatibility...")
    run_command("python -m pip install --upgrade " + " ".join(tools), check=False)
    print("✅ Build tools ready")

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"\n❌ Error: Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result

def main():
    """Main function to publish the package."""
    parser = argparse.ArgumentParser(description="Publish connectlife-cloud package to PyPI")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to PyPI test repository (testpypi)"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip twine check before upload"
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Skip cleaning previous builds"
    )
    args = parser.parse_args()
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Check if we're in the right directory
    if not (script_dir / "setup.py").exists() and not (script_dir / "pyproject.toml").exists():
        print("❌ Error: setup.py or pyproject.toml not found.")
        print("Please run this script from the connectlife_cloud directory.")
        sys.exit(1)
    
    # Get version
    version = get_version()
    if not version:
        print("❌ Error: Could not determine package version.")
        sys.exit(1)
    
    print(f"\n📦 Package: connectlife-cloud")
    print(f"📌 Version: {version}")
    print(f"📁 Directory: {script_dir}")
    
    # Check and upgrade build tools
    check_and_upgrade_tools()
    
    # Clean previous builds
    if not args.skip_clean:
        print("\n🧹 Cleaning previous builds...")
        clean_build_dirs(script_dir)
    else:
        print("\n⏭️  Skipping clean (--skip-clean specified)")
    
    # Build the package
    print("\n🔨 Building package...")
    run_command("python -m build", cwd=script_dir)
    
    # Check the package
    if not args.skip_check:
        print("\n✅ Checking package...")
        run_command("python -m twine check dist/*", cwd=script_dir)
    else:
        print("\n⏭️  Skipping check (--skip-check specified)")
    
    # Determine upload command
    package_pattern = f"dist/connectlife_cloud-{version}*"
    repository = "--repository testpypi" if args.test else ""
    
    if args.test:
        print(f"\n🚀 Uploading to PyPI test repository...")
        print(f"   Pattern: {package_pattern}")
        upload_cmd = f"python -m twine upload {repository} {package_pattern}"
    else:
        print(f"\n🚀 Uploading to production PyPI...")
        print(f"   Pattern: {package_pattern}")
        upload_cmd = f"python -m twine upload {package_pattern}"
    
    # Confirm before production upload
    if not args.test:
        print("\n⚠️  WARNING: You are about to upload to PRODUCTION PyPI!")
        response = input("Continue? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("❌ Upload cancelled.")
            sys.exit(0)
    
    # Upload to PyPI
    run_command(upload_cmd, cwd=script_dir)
    
    print(f"\n{'='*60}")
    print("✅ Package uploaded successfully!")
    print(f"{'='*60}")
    if args.test:
        print("\nTo upload to production PyPI, run:")
        print(f"  python publish.py")
    else:
        print(f"\nPackage is now available on PyPI!")
        print(f"Install with: pip install connectlife-cloud=={version}")

if __name__ == "__main__":
    main()
