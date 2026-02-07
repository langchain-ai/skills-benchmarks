"""Test environment setup and teardown."""

import tempfile
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


def check_claude_available() -> bool:
    return subprocess.run(["which", "claude"], capture_output=True).returncode == 0


def setup_test_environment(work_dir: Path = None) -> Path:
    """Create isolated temp directory for test. Optionally copy files from work_dir."""
    if not check_claude_available():
        raise RuntimeError("Claude Code CLI not found")

    temp_dir = Path(tempfile.mkdtemp(prefix="claude_test_"))
    print(f"Setting up test environment in {temp_dir}...")

    if work_dir and work_dir.exists():
        for item in work_dir.iterdir():
            if not item.name.startswith('.') and item.name != '.venv':
                dest = temp_dir / item.name
                (shutil.copytree if item.is_dir() else shutil.copy2)(item, dest)
        print(f"Copied test data from {work_dir}")

    print("✓ Test environment ready")
    return temp_dir


def cleanup_test_environment(test_dir: Path):
    """Clean up temp test directory (with safety check)."""
    if not any([tempfile.gettempdir() in str(test_dir), 'claude_test_' in str(test_dir)]):
        print(f"Not cleaning up {test_dir} (not a temp directory)")
        return
    if test_dir.exists():
        print(f"Cleaning up {test_dir}...")
        shutil.rmtree(test_dir)
        print("✓ Cleaned up")


def copy_test_data(source_file: Path, test_dir: Path):
    """Copy a test data file to the test directory."""
    if source_file.exists():
        shutil.copy2(source_file, test_dir / source_file.name)
        print(f"✓ Copied {source_file.name} to test directory")
