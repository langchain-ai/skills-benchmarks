"""Shared fixtures and utilities for all script tests."""

import subprocess
from pathlib import Path


def run_python_script(
    script_path: Path, args: list[str], timeout: int = 30
) -> subprocess.CompletedProcess:
    """Run a Python script and return the result."""
    cmd = ["python", str(script_path)] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def run_ts_script(
    script_path: Path, args: list[str], timeout: int = 30
) -> subprocess.CompletedProcess:
    """Run a TypeScript script using npx tsx and return the result."""
    cmd = ["npx", "tsx", str(script_path)] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
