#!/usr/bin/env python3
"""
run.py - Zero-setup execution wrapper for img-to-img-zipper

This wrapper handles complete environment setup:
- Creates virtual environment if it doesn't exist
- Activates the virtual environment
- Installs/updates dependencies from requirements.txt
- Runs the main entry point

Usage: python3 run.py
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Execute the script with automatic environment setup."""
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    python_executable = venv_path / "bin" / "python3"
    pip_executable = venv_path / "bin" / "pip"

    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✓ Virtual environment created")

    # Install/update dependencies
    print("Installing dependencies...")
    subprocess.run(
        [str(pip_executable), "install", "-q", "-r", "requirements.txt"], check=True
    )
    print("✓ Dependencies installed")

    # Run the main script
    print("\nStarting img-to-img-zipper...\n")
    subprocess.run([str(python_executable), "-m", "src.main"], check=True)


if __name__ == "__main__":
    main()
