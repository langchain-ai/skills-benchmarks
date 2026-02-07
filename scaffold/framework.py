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
            skills={"my-skill": [HEADER, EXAMPLES]},
            validators=[
                PythonFileValidator("output.py", required={"pattern": "desc"}),
            ],
        ),
    }
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import ast
import subprocess
import sys
import os

from .model import evaluate_with_schema
from .runner import run_python_in_docker
from .setup import check_docker_available, get_noise_prompt, get_noise_output


# =============================================================================
# SHARED UTILITIES
# =============================================================================

def run_python_file(test_dir: Path, filename: str, run_args: List[str] = None, timeout: int = 180) -> Tuple[bool, str]:
    """Run a Python file, using Docker if Dockerfile exists, otherwise local Python.

    Returns (success, output) tuple.
    """
    run_args = run_args or []
    dockerfile = test_dir / "Dockerfile"

    # Use Docker if available and Dockerfile exists
    if dockerfile.exists() and check_docker_available():
        return run_python_in_docker(test_dir, filename, timeout=timeout)

    # Fall back to local Python
    try:
        cmd = [sys.executable, str(test_dir / filename)] + run_args
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=str(test_dir), env=os.environ.copy(),
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)


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

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        """Validate Python file.

        Args:
            events: Parsed events from Claude's execution
            test_dir: Directory containing test files
            outputs: Pre-captured outputs {filename: (success, output, duration_s)}
        """
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
            # Use pre-captured output if available
            if outputs and self.filename in outputs:
                success, output, _ = outputs[self.filename]
            else:
                success, output = run_python_file(test_dir, self.filename, self.run_args)

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
        passed.append(f"Turns: {events.get('num_turns', 0) or 0}")
        duration = events.get('duration_seconds', 0) or 0
        passed.append(f"Duration: {duration:.0f}s")

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

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None):
        """Validate output quality.

        Args:
            events: Parsed events from Claude's execution
            test_dir: Directory containing test files
            outputs: Pre-captured outputs {filename: (success, output, duration_s)}
                        If provided, uses cached output instead of running again.
        """
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"{self.label}: file not created")
            return passed, failed

        # Use pre-captured output if available, otherwise run
        if outputs and self.filename in outputs:
            success, output, duration = outputs[self.filename]
        else:
            success, output = run_python_file(test_dir, self.filename, self.run_args)
            duration = None

        if not success:
            failed.append(f"{self.label}: runtime error - {output[:100]}")
            return passed, failed

        if len(output.strip()) < 50:
            failed.append(f"{self.label}: output too short ({len(output)} chars)")
            return passed, failed

        duration_str = f" in {duration:.1f}s" if duration else ""
        passed.append(f"{self.label}: produced output ({len(output)} chars{duration_str})")

        # Use LLM to evaluate output quality (tracked as score, not pass/fail)
        eval_result = self._evaluate_output(output)
        quality_status = "GOOD" if eval_result["pass"] else "LOW"
        passed.append(f"{self.label} quality [{quality_status}]: {eval_result['reason']}")

        return passed, failed

    def _evaluate_output(self, output: str) -> dict:
        """Use LLM to evaluate if output is meaningful."""
        # Truncate output if too long
        output_sample = output[:3000] if len(output) > 3000 else output

        prompt = f"""Evaluate this program output.

Task: {self.task_description}
Expected behavior: {self.expected_behavior}

Actual output:
```
{output_sample}
```

Does this output demonstrate the expected behavior?"""

        return evaluate_with_schema(prompt)


# =============================================================================
# EXPERIMENT CONFIG
# =============================================================================

@dataclass
class Treatment:
    """Configuration for a single experiment.

    Example:
        Treatment(
            description="Test with multiple skills",
            skills={
                "langchain-agents": [HEADER, BODY, EXAMPLES],
                "docker-patterns": [DOCKER_SECTIONS],
            },
            claude_md=CLAUDE_MD_CONTENT,
            validators=[...],
        )
    """

    description: str
    skills: Dict[str, List[str]] = field(default_factory=dict)  # {skill_name: [sections]}
    claude_md: Optional[str] = None
    noise_tasks: List[str] = field(default_factory=list)
    validators: List[Validator] = field(default_factory=list)

    def get_files_to_run(self) -> List[str]:
        """Get list of files that need to be run (from validators that execute code)."""
        files = []
        for v in self.validators:
            if isinstance(v, OutputQualityValidator):
                files.append(v.filename)
            elif isinstance(v, PythonFileValidator) and v.run_file:
                files.append(v.filename)
        # Remove duplicates while preserving order
        return list(dict.fromkeys(files))

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

    def validate(self, events: dict, test_dir: Path, outputs: Dict[str, tuple] = None) -> tuple[List[str], List[str]]:
        """Run all validators and return (passed, failed) lists.

        Args:
            events: Parsed events from Claude's execution
            test_dir: Directory containing test files
            outputs: Pre-captured outputs {filename: (success, output, duration_s)}
        """
        all_passed, all_failed = [], []

        # Run configured validators
        for validator in self.validators:
            # Pass outputs to validators that support it
            if isinstance(validator, (OutputQualityValidator, PythonFileValidator)):
                passed, failed = validator.validate(events, test_dir, outputs)
            else:
                passed, failed = validator.validate(events, test_dir)
            all_passed.extend(passed)
            all_failed.extend(failed)

        # Auto-validate noise tasks if present
        if self.noise_tasks:
            passed, failed = NoiseTaskValidator(self.noise_tasks).validate(events, test_dir)
            all_passed.extend(passed)
            all_failed.extend(failed)

        return all_passed, all_failed


