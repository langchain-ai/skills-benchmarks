"""Test environment setup and teardown utilities for Claude Code testing."""

import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def check_claude_available() -> bool:
    """Check if Claude Code CLI is available.

    Returns:
        True if claude command is available, False otherwise
    """
    result = subprocess.run(
        ["which", "claude"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def setup_test_environment(work_dir: Optional[Path] = None) -> Path:
    """Set up a test environment directory.

    Creates an isolated temporary directory for test safety.
    Optionally copies files from a work_dir if provided.

    Args:
        work_dir: Optional directory to copy test data from

    Returns:
        Path to temporary test directory

    Raises:
        RuntimeError: If Claude Code CLI is not available
    """
    if not check_claude_available():
        raise RuntimeError(
            "Claude Code CLI not found. Please install it with: npm install -g @anthropic-ai/claude-code"
        )

    temp_dir = Path(tempfile.mkdtemp(prefix="claude_test_"))
    print(f"Setting up test environment in {temp_dir}...")

    # If work_dir is provided and has data files, copy them
    if work_dir and work_dir.exists():
        # Copy any test data files (but not hidden files or .venv)
        for item in work_dir.iterdir():
            if not item.name.startswith('.') and item.name != '.venv':
                if item.is_file():
                    shutil.copy2(item, temp_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, temp_dir / item.name)
        print(f"Copied test data from {work_dir}")

    print("✓ Test environment ready")
    return temp_dir


def cleanup_test_environment(test_dir: Path):
    """Clean up temporary test directory.

    Args:
        test_dir: Test directory to clean up
    """
    # Check if it's a temp directory (starts with system temp dir or contains "claude_test_")
    temp_indicators = [
        tempfile.gettempdir() in str(test_dir),
        'claude_test_' in str(test_dir)
    ]

    if not any(temp_indicators):
        print(f"Not cleaning up {test_dir} (not a temp directory)")
        return

    if test_dir.exists():
        print(f"Cleaning up {test_dir}...")
        shutil.rmtree(test_dir)
        print("✓ Cleaned up")


def copy_test_data(source_file: Path, test_dir: Path):
    """Copy a test data file to the test directory.

    Args:
        source_file: Source file to copy
        test_dir: Target test directory
    """
    if source_file.exists():
        shutil.copy2(source_file, test_dir / source_file.name)
        print(f"✓ Copied {source_file.name} to test directory")
