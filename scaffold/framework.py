"""Experiment framework for skill benchmarks.

This module provides everything needed to define and run treatments:
- Treatment: defines a specific experimental condition
- Validators: check if the treatment succeeded
- Noise tasks: distractor tasks to test skill retention

Example usage:
    from scaffold import Treatment, PythonFileValidator, MetricsCollector

    TREATMENTS = {
        "BASELINE": Treatment(
            description="Test with skill",
            sections=MY_SECTIONS,
            validators=[
                PythonFileValidator("output.py", required={"pattern": "desc"}),
            ],
        ),
    }
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Callable
import ast


# =============================================================================
# NOISE TASKS
# =============================================================================

NOISE_TASKS = {
    "docker-patterns": {
        "prompt": (
            "Create a Dockerfile for a Node.js application with multi-stage build, "
            "non-root user, and health check. Save to Dockerfile."
        ),
        "output": "Dockerfile",
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
    noise_dir = Path(__file__).parent.parent.parent / "skill_constructs" / "noise"
    dir_name = skill_name.replace("-", "_")
    skill_file = noise_dir / dir_name / "SKILL.md"
    return skill_file.read_text() if skill_file.exists() else ""


# =============================================================================
# VALIDATORS
# =============================================================================

class Validator(ABC):
    """Base class for experiment validators."""

    @abstractmethod
    def validate(self, events: dict, test_dir: Path) -> tuple[List[str], List[str]]:
        """Validate the experiment. Returns (passed, failed) check lists."""
        pass


class SkillInvokedValidator(Validator):
    """Check if a skill was invoked."""

    def __init__(self, skill_name: str, required: bool = True):
        self.skill_name = skill_name
        self.required = required

    def validate(self, events: dict, test_dir: Path):
        passed, failed = [], []
        invoked = self.skill_name in events.get("skills_invoked", [])

        if invoked:
            passed.append(f"Invoked {self.skill_name} skill")
        elif self.required:
            failed.append(f"Did NOT invoke {self.skill_name} skill")
        else:
            passed.append(f"Note: did not invoke {self.skill_name}")

        return passed, failed


class PythonFileValidator(Validator):
    """Validate a Python file exists, has valid syntax, and matches patterns."""

    def __init__(
        self,
        filename: str,
        label: str = None,
        required: Dict[str, str] = None,
        forbidden: Dict[str, str] = None,
        any_of: Dict[str, str] = None,
        run_file: bool = False,
        require_all: bool = False,
        run_args: List[str] = None,
        output_patterns: Dict[str, str] = None,
        min_output_lines: int = 0,
    ):
        """
        Args:
            filename: File to validate
            label: Display label (defaults to filename)
            required: {pattern: description} - patterns that should be present in code
            forbidden: {pattern: description} - none can be present in code
            any_of: {pattern: description} - at least ONE of these must be present
            run_file: Whether to try running the file
            require_all: If True, ALL required patterns must be present.
                        If False (default), at least one must be present.
            run_args: Arguments to pass when running the file
            output_patterns: {pattern: description} - patterns to check in stdout
            min_output_lines: Minimum lines of output expected
        """
        self.filename = filename
        self.label = label or filename
        self.required = required or {}
        self.forbidden = forbidden or {}
        self.any_of = any_of or {}
        self.run_file = run_file
        self.require_all = require_all
        self.run_args = run_args or []
        self.output_patterns = output_patterns or {}
        self.min_output_lines = min_output_lines

    def _run_file(self, test_dir: Path) -> tuple[bool, str]:
        """Run the file, using Docker if Dockerfile exists, otherwise local Python."""
        from scaffold.runner import run_python_in_docker, check_docker_available

        dockerfile = test_dir / "Dockerfile"

        # Use Docker if available and Dockerfile exists
        if dockerfile.exists() and check_docker_available():
            return run_python_in_docker(test_dir, self.filename, timeout=120)

        # Fall back to local Python
        import subprocess
        import sys
        import os

        try:
            cmd = [sys.executable, str(test_dir / self.filename)] + self.run_args
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120,
                cwd=str(test_dir), env=os.environ.copy(),
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "timeout (120s)"
        except Exception as e:
            return False, str(e)

    def validate(self, events: dict, test_dir: Path):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"{self.label}: file not created")
            return passed, failed

        content = file_path.read_text()
        passed.append(f"{self.label}: created")

        # Check required patterns in code
        if self.required:
            found = [(pat, desc) for pat, desc in self.required.items() if pat in content]
            missing = [(pat, desc) for pat, desc in self.required.items() if pat not in content]

            if self.require_all:
                # ALL patterns must be present
                if missing:
                    for pat, desc in missing:
                        failed.append(f"{self.label}: missing {desc}")
                if found:
                    passed.append(f"{self.label}: {', '.join(d for _, d in found[:3])}")
            else:
                # At least ONE pattern must be present
                if found:
                    passed.append(f"{self.label}: {', '.join(d for _, d in found[:3])}")
                else:
                    failed.append(f"{self.label}: missing required patterns")

        # Check any_of patterns (at least ONE must be present)
        if self.any_of:
            found = [(pat, desc) for pat, desc in self.any_of.items() if pat in content]
            if found:
                passed.append(f"{self.label}: {found[0][1]}")
            else:
                # List what was expected
                expected = ", ".join(desc for _, desc in self.any_of.items())
                failed.append(f"{self.label}: missing import (need one of: {expected})")

        # Check forbidden patterns in code
        for pattern, desc in self.forbidden.items():
            if pattern in content:
                failed.append(f"{self.label}: {desc}")

        # Syntax check
        try:
            ast.parse(content)
            passed.append(f"{self.label}: valid syntax")
        except SyntaxError as e:
            failed.append(f"{self.label}: syntax error line {e.lineno}")
            return passed, failed

        # Optional: run the file and validate output
        if self.run_file:
            success, output = self._run_file(test_dir)

            if success:
                passed.append(f"{self.label}: runs successfully")

                # Check minimum output lines
                output_lines = len([l for l in output.strip().split('\n') if l.strip()])
                if self.min_output_lines > 0:
                    if output_lines >= self.min_output_lines:
                        passed.append(f"{self.label}: {output_lines} lines output")
                    else:
                        failed.append(f"{self.label}: only {output_lines} lines (need {self.min_output_lines})")

                # Check output patterns
                for pattern, desc in self.output_patterns.items():
                    if pattern.lower() in output.lower():
                        passed.append(f"{self.label}: output has {desc}")
                    else:
                        failed.append(f"{self.label}: output missing {desc}")
            else:
                failed.append(f"{self.label}: {output[:150]}")

        return passed, failed


class NoiseTaskValidator(Validator):
    """Validate noise tasks were completed."""

    def __init__(self, noise_tasks: List[str]):
        self.noise_tasks = noise_tasks

    def validate(self, events: dict, test_dir: Path):
        passed, failed = [], []

        for task_name in self.noise_tasks:
            # Check skill was invoked
            if task_name in events.get("skills_invoked", []):
                passed.append(f"Invoked {task_name} skill")
            else:
                failed.append(f"Did NOT invoke {task_name} skill")

            # Check output file exists
            output_file = get_noise_output(task_name)
            if (test_dir / output_file).exists():
                passed.append(f"Noise: {output_file} created")
            else:
                failed.append(f"Noise: {output_file} NOT created")

        return passed, failed


class MetricsCollector(Validator):
    """Collect metrics (always passes, adds info to passed list)."""

    def __init__(self, output_files: List[str] = None):
        self.output_files = output_files or []

    def validate(self, events: dict, test_dir: Path):
        passed = []

        # Basic metrics
        passed.append(f"Turns: {events.get('num_turns', 0)}")
        passed.append(f"Duration: {events.get('duration_seconds', 0):.0f}s")

        # Tool calls
        tool_calls = events.get("tool_calls", [])
        passed.append(f"Tool calls: {len(tool_calls)}")

        # Deprecated pattern attempts
        deprecated = ["create_sql_agent", "AgentExecutor", "initialize_agent"]
        dep_count = sum(
            1 for tc in tool_calls
            if tc.get("tool") in ("Write", "Edit")
            and any(d in str(tc.get("input", {})) for d in deprecated)
        )
        if dep_count > 0:
            passed.append(f"Deprecated attempts: {dep_count}")

        return passed, []


class OutputQualityValidator(Validator):
    """Use LLM to evaluate if output is meaningful and correct."""

    def __init__(
        self,
        filename: str,
        label: str,
        task_description: str,
        expected_behavior: str,
        run_args: List[str] = None,
    ):
        """
        Args:
            filename: Python file to run
            label: Display label
            task_description: What the code should do
            expected_behavior: What good output looks like
            run_args: Arguments to pass when running
        """
        self.filename = filename
        self.label = label
        self.task_description = task_description
        self.expected_behavior = expected_behavior
        self.run_args = run_args or []

    def validate(self, events: dict, test_dir: Path):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"{self.label}: file not created")
            return passed, failed

        # Run the file (uses Docker if available)
        success, output = self._run_file(test_dir)

        # Save Docker output to logs
        self._save_docker_output(output, success)

        if not success:
            failed.append(f"{self.label}: runtime error - {output[:100]}")
            return passed, failed

        if len(output.strip()) < 50:
            failed.append(f"{self.label}: output too short ({len(output)} chars)")
            return passed, failed

        passed.append(f"{self.label}: produced output ({len(output)} chars)")

        # Use LLM to evaluate output quality
        eval_result = self._evaluate_output(output)
        if eval_result["pass"]:
            passed.append(f"{self.label}: {eval_result['reason']}")
        else:
            failed.append(f"{self.label}: {eval_result['reason']}")

        return passed, failed

    def _save_docker_output(self, output: str, success: bool):
        """Save Docker execution output to logs/docker/ directory."""
        from scaffold.runner import save_log, LOGS_DIR

        status = "success" if success else "error"
        safe_name = self.filename.replace(".py", "").replace("/", "_")
        save_log(output, LOGS_DIR / "docker", safe_name, f"_{status}.txt")

    def _run_file(self, test_dir: Path) -> tuple[bool, str]:
        """Run the file, using Docker if Dockerfile exists, otherwise local Python."""
        from scaffold.runner import run_python_in_docker, check_docker_available

        dockerfile = test_dir / "Dockerfile"

        # Use Docker if available and Dockerfile exists
        if dockerfile.exists() and check_docker_available():
            return run_python_in_docker(test_dir, self.filename, timeout=120)

        # Fall back to local Python
        import subprocess
        import sys
        import os

        try:
            cmd = [sys.executable, str(test_dir / self.filename)] + self.run_args
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120,
                cwd=str(test_dir), env=os.environ.copy(),
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, "timeout (120s)"
        except Exception as e:
            return False, str(e)

    def _evaluate_output(self, output: str) -> dict:
        """Use LLM to evaluate if output is meaningful."""
        from .model import evaluate_with_json

        # Truncate output if too long
        output_sample = output[:3000] if len(output) > 3000 else output

        prompt = f"""Evaluate this program output. Task: {self.task_description}

Expected behavior: {self.expected_behavior}

Actual output:
```
{output_sample}
```

Does this output demonstrate the expected behavior? Reply with ONLY a JSON object:
{{"pass": true/false, "reason": "brief explanation (max 10 words)"}}"""

        return evaluate_with_json(prompt)


# =============================================================================
# EXPERIMENT CONFIG
# =============================================================================

@dataclass
class Treatment:
    """Configuration for a single experiment."""

    description: str
    sections: Optional[List[str]] = None  # Skill sections (None = no skill)
    claude_md: Optional[str] = None       # CLAUDE.md content
    noise_tasks: List[str] = field(default_factory=list)
    validators: List[Validator] = field(default_factory=list)

    def build_prompt(self, base_prompt: str, task2_prompt: str = None) -> str:
        """Build experiment prompt, inserting noise tasks if present."""
        if not self.noise_tasks:
            if task2_prompt:
                return f"Complete these tasks in order:\n\n1. {base_prompt}\n\n2. {task2_prompt}"
            return base_prompt

        # Insert noise tasks between main tasks
        noise_prompts = [get_noise_prompt(t) for t in self.noise_tasks]
        parts = [f"1. {base_prompt}"]
        for i, noise in enumerate(noise_prompts, start=2):
            parts.append(f"{i}. {noise}")
        if task2_prompt:
            parts.append(f"{len(parts) + 1}. {task2_prompt}")

        return "Complete these tasks in order:\n\n" + "\n\n".join(parts)

    def validate(self, events: dict, test_dir: Path) -> tuple[List[str], List[str]]:
        """Run all validators and return (passed, failed) lists."""
        all_passed, all_failed = [], []

        # Run configured validators
        for validator in self.validators:
            passed, failed = validator.validate(events, test_dir)
            all_passed.extend(passed)
            all_failed.extend(failed)

        # Auto-validate noise tasks if present
        if self.noise_tasks:
            passed, failed = NoiseTaskValidator(self.noise_tasks).validate(events, test_dir)
            all_passed.extend(passed)
            all_failed.extend(failed)

        return all_passed, all_failed


# =============================================================================
# HELPERS FOR CREATING COMMON VALIDATOR SETS
# =============================================================================

def langchain_skill_validator(required: bool = True) -> SkillInvokedValidator:
    """Validator for langchain-agents skill invocation."""
    return SkillInvokedValidator("langchain-agents", required=required)


def python_files_validator(
    filenames: List[str],
    required: Dict[str, str] = None,
    forbidden: Dict[str, str] = None,
    run_files: bool = False,
) -> List[PythonFileValidator]:
    """Create validators for multiple Python files with same patterns."""
    return [
        PythonFileValidator(
            f, label=f"Agent {i+1}",
            required=required, forbidden=forbidden, run_file=run_files
        )
        for i, f in enumerate(filenames)
    ]


def metrics_collector(filenames: List[str]) -> MetricsCollector:
    """Create metrics collector for given output files."""
    return MetricsCollector(filenames)
