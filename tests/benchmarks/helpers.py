"""Shared fixtures for benchmark tests.

Includes noise task definitions for distractor experiments.
"""

from pathlib import Path

from scaffold import NoiseTask
from skills.parser import load_skill

# =============================================================================
# NOISE SKILLS
# =============================================================================

NOISE_SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "noise"

# Map noise task names to their skill directory names (underscores in filesystem)
_SKILL_DIR_MAP = {
    "docker-patterns": "docker_patterns",
    "react-components": "react_components",
    "api-docs": "api_docs",
}


def load_noise_skill(name: str) -> list[str]:
    """Load skill sections for a noise task.

    Args:
        name: Noise task name (e.g., "docker-patterns")

    Returns:
        List of skill section content strings
    """
    dir_name = _SKILL_DIR_MAP.get(name, name.replace("-", "_"))
    skill_dir = NOISE_SKILLS_DIR / dir_name
    skill = load_skill(skill_dir)
    return skill["all"]


def get_noise_skills(names: list[str]) -> dict[str, list[str]]:
    """Get skills dict for multiple noise tasks.

    Args:
        names: List of noise task names

    Returns:
        Dict mapping skill names to their section lists
    """
    return {name: load_noise_skill(name) for name in names}


# =============================================================================
# NOISE TASKS
# =============================================================================

NOISE_TASKS = {
    "docker-patterns": {
        "prompt": "Create a Dockerfile for a Node.js application with multi-stage build, non-root user, and health check. Save to Dockerfile.nodejs.",
        "output": "Dockerfile.nodejs",
    },
    "react-components": {
        "prompt": "Create a React component that fetches and displays user data using hooks (useState, useEffect), with loading/error states in TypeScript. Save to UserProfile.tsx.",
        "output": "UserProfile.tsx",
    },
    "api-docs": {
        "prompt": "Create an OpenAPI spec for a simple user API with GET /users, POST /users, proper schemas, and error responses. Save to openapi.yaml.",
        "output": "openapi.yaml",
    },
}


def get_noise_task(name: str) -> NoiseTask:
    """Get a noise task by name."""
    data = NOISE_TASKS[name]
    return NoiseTask(prompt=data["prompt"], deliverables=[data["output"]])


def get_noise_tasks(names: list[str]) -> list[NoiseTask]:
    """Get multiple noise tasks by name."""
    return [get_noise_task(n) for n in names]
