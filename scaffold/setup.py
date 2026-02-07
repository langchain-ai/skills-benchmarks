"""Test environment setup, verification, and skill construction.

Library usage:
    from scaffold.setup import setup_test_environment, cleanup_test_environment
    from scaffold.setup import verify_environment
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")


# =============================================================================
# VERIFICATION
# =============================================================================

def check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_claude_available() -> bool:
    """Check if Claude Code CLI is available."""
    try:
        result = subprocess.run(["claude", "--version"], capture_output=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def verify_environment(environment_dir: Path, required_files: List[str] = None):
    """Verify Docker, Claude CLI, and environment files are available.

    Args:
        environment_dir: Path to environment directory
        required_files: List of required file names (default: Dockerfile, requirements.txt)

    Raises:
        RuntimeError: If any required component is missing
    """
    errors = []

    # Check Claude CLI
    if not check_claude_available():
        errors.append("Claude Code CLI not found. Install from: https://claude.ai/code")

    # Check Docker
    if not check_docker_available():
        errors.append("Docker not available. Install Docker Desktop or Docker Engine.")

    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("OPENAI_API_KEY not set (required for generated agents)")

    # Check environment directory
    if not environment_dir.exists():
        errors.append(f"Environment directory not found: {environment_dir}")
    else:
        required = required_files or ["Dockerfile", "requirements.txt"]
        missing = [f for f in required if not (environment_dir / f).exists()]
        if missing:
            errors.append(f"Missing environment files: {', '.join(missing)}")

    if errors:
        print("Environment verification failed:")
        for error in errors:
            print(f"  - {error}")
        raise RuntimeError("Environment verification failed")

    print("✓ Environment verified (Docker, Claude CLI, API keys)")


# =============================================================================
# TEST ENVIRONMENT
# =============================================================================

def setup_test_environment(work_dir: Path = None) -> Path:
    """Create isolated temp directory for test. Optionally copy files from work_dir."""
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


# =============================================================================
# SKILL CONSTRUCTION
# =============================================================================

def build_skill(sections: List[str]) -> str:
    """Assemble skill from list of section strings."""
    return "\n\n".join(s for s in sections if s and s.strip())


def write_skill(test_dir: Path, skill_name: str, content: str) -> Path:
    """Write skill content to .claude/skills/ directory."""
    skill_dir = test_dir / ".claude" / "skills" / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)
    return skill_file


def setup_test_context(
    test_dir: Path,
    sections: List[str] = None,
    claude_md: str = None,
    skill_name: str = "langchain-agents",
    environment_dir: Path = None,
) -> None:
    """Setup test directory with .claude/ containing skills and CLAUDE.md.

    Args:
        test_dir: Test working directory
        sections: List of section strings to assemble into skill (None = no skill)
        claude_md: Content for CLAUDE.md (None = no CLAUDE.md)
        skill_name: Name for the skill directory
        environment_dir: Path to environment directory (contains Dockerfile, requirements.txt, etc.)
    """
    claude_dir = test_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    if claude_md:
        (claude_dir / "CLAUDE.md").write_text(claude_md)

    # Only create skill if sections provided
    if sections:
        content = build_skill(sections)
        write_skill(test_dir, skill_name, content)

    # Copy environment files (Dockerfile, requirements.txt, test data, etc.)
    if environment_dir and environment_dir.exists():
        for item in environment_dir.iterdir():
            dest = test_dir / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)
        print(f"✓ Copied environment from {environment_dir.name}/")


# =============================================================================
# CLEANUP UTILITIES
# =============================================================================

def cleanup_test_files(test_dir: Path):
    """Clean up test artifact files from test directory."""
    patterns = [
        "agent_summary.txt", "test_*.txt", "test_*.json", "test_*.py",
        "sql_agent.py", "sql_agent_*.py",
        "research_agent.py", "research_agent_*.py",
        "search_agent.py",
    ]

    deleted_count = 0
    for pattern in patterns:
        for file in test_dir.glob(pattern):
            try:
                file.unlink()
                deleted_count += 1
                print(f"  Deleted: {file.name}")
            except Exception as e:
                print(f"  Could not delete {file.name}: {e}")

    if deleted_count == 0:
        print("  (no test files found)")


def cleanup_langsmith_assets():
    """Clean up test datasets from LangSmith."""
    try:
        from langsmith import Client
        client = Client()

        test_dataset_names = [
            "Test Dataset - DELETE ME",
            "Evaluator Test Dataset - DELETE ME"
        ]

        deleted_count = 0
        for dataset_name in test_dataset_names:
            try:
                datasets = list(client.list_datasets(dataset_name=dataset_name))
                for dataset in datasets:
                    client.delete_dataset(dataset_id=dataset.id)
                    deleted_count += 1
                    print(f"  Deleted dataset: {dataset.name}")
            except Exception as e:
                print(f"  Could not delete dataset '{dataset_name}': {e}")

        if deleted_count == 0:
            print("  (no test datasets found)")

    except Exception as e:
        print(f"  LangSmith cleanup failed: {e}")
