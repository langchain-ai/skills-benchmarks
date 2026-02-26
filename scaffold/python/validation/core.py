"""Core validation utilities.

Basic utilities for file and pattern validation that can be composed together.
"""

import json
import re
from collections.abc import Callable
from pathlib import Path

# Type alias for validator functions
ValidatorFn = Callable[[Path, dict], tuple[list[str], list[str]]]


def load_outputs(path: str = "_outputs.json") -> dict:
    """Load the outputs dict serialized by make_execution_validator.

    Returns empty dict if file not found (e.g. running outside factory).
    """
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def validate_file_exists(test_dir: Path, filepath: str) -> tuple[list[str], list[str]]:
    """Check that a file exists.

    Args:
        test_dir: Test working directory
        filepath: Relative path to file

    Returns:
        (passed, failed) lists
    """
    path = test_dir / filepath
    if path.exists():
        return [f"File exists: {filepath}"], []
    return [], [f"File missing: {filepath}"]


def validate_pattern(
    filepath: Path,
    pattern: str,
    description: str,
    flags: int = 0,
) -> tuple[list[str], list[str]]:
    """Check that a file contains a regex pattern.

    Args:
        filepath: Path to file
        pattern: Regex pattern to search for
        description: Human-readable description of what we're checking
        flags: Regex flags (e.g., re.MULTILINE)

    Returns:
        (passed, failed) lists
    """
    if not filepath.exists():
        return [], [f"{description}: file not found ({filepath.name})"]

    content = filepath.read_text()
    if re.search(pattern, content, flags):
        return [description], []
    return [], [f"Missing: {description}"]


def validate_no_pattern(
    filepath: Path,
    pattern: str,
    description: str,
    flags: int = 0,
) -> tuple[list[str], list[str]]:
    """Check that a file does NOT contain a regex pattern.

    Args:
        filepath: Path to file
        pattern: Regex pattern that should NOT be present
        description: Human-readable description of what we're checking
        flags: Regex flags

    Returns:
        (passed, failed) lists
    """
    if not filepath.exists():
        return [], [f"{description}: file not found ({filepath.name})"]

    content = filepath.read_text()
    if re.search(pattern, content, flags):
        return [], [f"Unexpected: {description}"]
    return [f"No {description}"], []


def compose_validators(*validators: ValidatorFn) -> ValidatorFn:
    """Compose multiple validator functions into one.

    Args:
        *validators: Validator functions to compose

    Returns:
        A single validator function that runs all validators
    """

    def composed(test_dir: Path, outputs: dict) -> tuple[list[str], list[str]]:
        all_passed, all_failed = [], []
        for validator in validators:
            passed, failed = validator(test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)
        return all_passed, all_failed

    return composed


def run_validators(
    validators: list[ValidatorFn],
    test_dir: Path,
    outputs: dict,
) -> tuple[list[str], list[str]]:
    """Run a list of validator functions.

    Args:
        validators: List of validator functions
        test_dir: Test working directory
        outputs: Additional outputs dict

    Returns:
        Combined (passed, failed) lists
    """
    all_passed, all_failed = [], []
    for validator in validators:
        passed, failed = validator(test_dir, outputs)
        all_passed.extend(passed)
        all_failed.extend(failed)
    return all_passed, all_failed


def validate_starter_skill_first(
    outputs: dict,
) -> tuple[list[str], list[str]]:
    """Check that langchain-oss-primer or framework-selection was invoked first.

    Skipped (informational) when:
    - No skills were invoked (e.g. CONTROL treatment)
    - Treatment is ALL_MAIN_SKILLS (starter skills not included in that treatment)
    """
    # Skip for ALL_MAIN_SKILLS — starter skills are not part of that treatment
    treatment_name = (outputs or {}).get("treatment_name", "")
    if treatment_name == "ALL_MAIN_SKILLS":
        return ["Note: starter skill check skipped (ALL_MAIN_SKILLS)"], []

    events = outputs.get("events", {}) if outputs else {}
    skills_invoked = events.get("skills_invoked", [])

    # No skills invoked at all (e.g. CONTROL treatment) — nothing to check
    if not skills_invoked:
        return ["Note: no skills invoked"], []

    starter_skills = {"langchain-oss-primer", "framework-selection"}

    if skills_invoked[0] in starter_skills:
        return [f"Starter skill invoked first: {skills_invoked[0]}"], []

    first = skills_invoked[0]
    invoked_starters = [s for s in skills_invoked if s in starter_skills]
    if invoked_starters:
        starters = ", ".join(invoked_starters)
        return [], [
            f"Starter skill not invoked first: first was '{first}', starters invoked later: {starters}"
        ]
    return [], [
        f"Starter skill not invoked: first skill was '{first}' (expected langchain-oss-primer or framework-selection)"
    ]


def validate_skill_invoked(
    outputs: dict,
    skill_name: str,
    required: bool = False,
) -> tuple[list[str], list[str]]:
    """Check if a skill was invoked during the task.

    This is typically informational (required=False) to track skill usage.

    Args:
        outputs: Outputs dict containing events
        skill_name: Name of the skill to check (e.g., "langchain-agents")
        required: If True, failing to invoke the skill is an error

    Returns:
        (passed, failed) lists
    """
    events = outputs.get("events", {}) if outputs else {}
    skills_invoked = events.get("skills_invoked", [])

    if skill_name in skills_invoked:
        return [f"Invoked {skill_name} skill"], []
    elif required:
        return [], [f"Did NOT invoke {skill_name} skill"]
    else:
        return [f"Note: did not invoke {skill_name}"], []


# Noise task configurations
NOISE_TASK_PROMPTS = {
    "docker_patterns": "Create a Dockerfile for a Node.js application with multi-stage build, non-root user, and health check. Save to Dockerfile.nodejs.",
    "react_components": "Create a React component that fetches and displays user data using hooks (useState, useEffect), with loading/error states in TypeScript. Save to UserProfile.tsx.",
    "api_docs": "Create an OpenAPI spec for a simple user API with GET /users, POST /users, proper schemas, and error responses. Save to openapi.yaml.",
}

# Noise task deliverable files
NOISE_TASK_DELIVERABLES = {
    "docker_patterns": "Dockerfile.nodejs",
    "react_components": "UserProfile.tsx",
    "api_docs": "openapi.yaml",
}


def get_noise_task_prompts(noise_tasks: list[str]) -> list[str]:
    """Get prompts for noise tasks by name.

    Args:
        noise_tasks: List of noise task names (e.g., ["docker_patterns", "react_components"])

    Returns:
        List of prompt strings for the specified tasks
    """
    return [NOISE_TASK_PROMPTS[name] for name in noise_tasks if name in NOISE_TASK_PROMPTS]


def validate_noise_outputs(
    noise_tasks: list[str],
    test_dir: Path = None,
) -> tuple[list[str], list[str]]:
    """Validate that noise task deliverables were created."""
    passed, failed = [], []
    test_dir = test_dir or Path(".")

    for task_name in noise_tasks:
        deliverable = NOISE_TASK_DELIVERABLES.get(task_name)
        if not deliverable:
            continue

        path = test_dir / deliverable
        if path.exists():
            passed.append(f"Noise: {deliverable} created")
        else:
            failed.append(f"Noise: {deliverable} NOT created")

    return passed, failed
