"""Test environment setup and skill construction.

Library usage:
    from scaffold.setup import setup_test_environment, cleanup_test_environment
    from scaffold.setup import verify_environment
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from .utils import check_docker_available, check_claude_available


# =============================================================================
# VERIFICATION
# =============================================================================

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
    if not os.getenv("ANTHROPIC_API_KEY"):
        errors.append("ANTHROPIC_API_KEY not set (required for Claude Code in Docker)")
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


def write_skill(test_dir: Path, skill_name: str, content: str, scripts_dir: Path = None) -> Path:
    """Write skill content to .claude/skills/ directory.

    Args:
        test_dir: Test directory root
        skill_name: Name of the skill (e.g., "langsmith-trace")
        content: SKILL.md content
        scripts_dir: Optional path to directory containing scripts to copy

    Returns:
        Path to the SKILL.md file
    """
    skill_dir = test_dir / ".claude" / "skills" / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)

    # Copy scripts if provided
    if scripts_dir and scripts_dir.exists():
        dest_scripts = skill_dir / "scripts"
        if scripts_dir.is_dir():
            shutil.copytree(scripts_dir, dest_scripts, dirs_exist_ok=True)
            print(f"  Copied scripts to {skill_name}/scripts/")
        else:
            # Single file
            dest_scripts.mkdir(parents=True, exist_ok=True)
            shutil.copy2(scripts_dir, dest_scripts / scripts_dir.name)

    return skill_file


# =============================================================================
# NOISE TASKS SETUP
# =============================================================================

NOISE_TASKS = {
    "docker-patterns": {
        "prompt": (
            "Create a Dockerfile for a Node.js application with multi-stage build, "
            "non-root user, and health check. Save to Dockerfile.nodejs."
        ),
        "output": "Dockerfile.nodejs",
    },
    "react-components": {
        "prompt": (
            "Create a React component that fetches and displays user data using hooks "
            "(useState, useEffect), with loading/error states in TypeScript. Save to UserProfile.tsx."
        ),
        "output": "UserProfile.tsx",
    },
    "api-docs": {
        "prompt": (
            "Create an OpenAPI spec for a simple user API with GET /users, POST /users, "
            "proper schemas, and error responses. Save to openapi.yaml."
        ),
        "output": "openapi.yaml",
    },
}


def get_noise_prompt(name: str) -> str:
    """Get the prompt for a noise task."""
    return NOISE_TASKS[name]["prompt"]


def get_noise_output(name: str) -> str:
    """Get the expected output file for a noise task."""
    return NOISE_TASKS[name]["output"]


def get_noise_skill_content(skill_name: str) -> str:
    """Read content of a noise skill from skill_constructs/noise/."""
    noise_dir = Path(__file__).parent.parent / "skill_constructs" / "noise"
    dir_name = skill_name.replace("-", "_")
    skill_file = noise_dir / dir_name / "SKILL.md"
    return skill_file.read_text() if skill_file.exists() else ""


def setup_test_context(
    test_dir: Path,
    skills: dict = None,
    claude_md: str = None,
    environment_dir: Path = None,
) -> None:
    """Setup test directory with .claude/ containing skills and CLAUDE.md.

    Args:
        test_dir: Test working directory
        skills: Dict mapping skill names to section lists, e.g.
                {"langchain-agents": [HEADER, BODY], "other-skill": [SECTIONS]}
        claude_md: Content for CLAUDE.md (None = no CLAUDE.md)
        environment_dir: Path to environment directory (contains Dockerfile, requirements.txt, etc.)
    """
    claude_dir = test_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)

    if claude_md:
        (claude_dir / "CLAUDE.md").write_text(claude_md)
        print(f"✓ Created CLAUDE.md ({len(claude_md)} chars)")
    else:
        print("⚠ No CLAUDE.md content provided")

    # Create each skill
    if skills:
        for skill_name, skill_config in skills.items():
            if skill_config:
                # Support both formats:
                # 1. List of sections (legacy): {"skill-name": [section1, section2]}
                # 2. Dict with sections and scripts: {"skill-name": {"sections": [...], "scripts_dir": Path}}
                if isinstance(skill_config, dict):
                    sections = skill_config.get("sections", [])
                    scripts_dir = skill_config.get("scripts_dir")
                else:
                    sections = skill_config
                    scripts_dir = None

                if sections:
                    content = build_skill(sections)
                    write_skill(test_dir, skill_name, content, scripts_dir=scripts_dir)

    # Copy environment files (Dockerfile, requirements.txt, test data, etc.)
    if environment_dir and environment_dir.exists():
        for item in environment_dir.iterdir():
            dest = test_dir / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)
        print(f"✓ Copied environment from {environment_dir.name}/")


