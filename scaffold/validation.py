"""Validation framework for experiment results.

Provides the Validator base class and common validators:
- SkillInvokedValidator: Check if a skill was invoked
- PythonFileValidator: Validate Python file existence, syntax, and patterns
- NoiseTaskValidator: Validate noise tasks were completed
- MetricsCollector: Collect metrics (always passes)
- OutputQualityValidator: Use LLM to evaluate output quality
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import ast
import subprocess
import sys
import os

from .utils import evaluate_with_schema, check_docker_available
from .setup import get_noise_output


def run_python_file(test_dir: Path, filename: str, run_args: List[str] = None, timeout: int = 300) -> Tuple[bool, str]:
    """Run a Python file, using Docker if available, otherwise local Python."""
    from .utils import run_python_in_docker

    run_args = run_args or []
    dockerfile = test_dir / "Dockerfile"

    if dockerfile.exists() and check_docker_available():
        return run_python_in_docker(test_dir, filename, timeout=timeout)

    try:
        cmd = [sys.executable, str(test_dir / filename)] + run_args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                                cwd=str(test_dir), env=os.environ.copy())
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"timeout ({timeout}s)"
    except Exception as e:
        return False, str(e)


# =============================================================================
# VALIDATORS
# =============================================================================

class Validator(ABC):
    """Base class for experiment validators.

    Validators receive:
    - events: Parsed events from Claude's execution
    - test_dir: Directory containing test files
    - outputs: {filename: (success, output, duration)} from ground truth phase
    """

    @abstractmethod
    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        """Validate the experiment. Returns (passed, failed) check lists."""
        pass


class SkillInvokedValidator(Validator):
    """Check if a skill was invoked."""

    def __init__(self, skill_name: str, required: bool = True):
        self.skill_name = skill_name
        self.required = required

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None):
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

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"{self.label}: file not created")
            return passed, failed

        content = file_path.read_text()
        passed.append(f"{self.label}: created")

        # Check required patterns
        if self.required:
            found = [(p, d) for p, d in self.required.items() if p in content]
            missing = [(p, d) for p, d in self.required.items() if p not in content]

            if self.require_all:
                for _, desc in missing:
                    failed.append(f"{self.label}: missing {desc}")
                if found:
                    passed.append(f"{self.label}: {', '.join(d for _, d in found[:3])}")
            else:
                if found:
                    passed.append(f"{self.label}: {', '.join(d for _, d in found[:3])}")
                else:
                    failed.append(f"{self.label}: missing required patterns")

        # Check any_of patterns
        if self.any_of:
            found = [(p, d) for p, d in self.any_of.items() if p in content]
            if found:
                passed.append(f"{self.label}: {found[0][1]}")
            else:
                expected = ", ".join(d for _, d in self.any_of.items())
                failed.append(f"{self.label}: missing (need one of: {expected})")

        # Check forbidden patterns
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

        # Run file if requested
        if self.run_file:
            if outputs and self.filename in outputs:
                success, output, _ = outputs[self.filename]
            else:
                success, output = run_python_file(test_dir, self.filename, self.run_args)

            if success:
                passed.append(f"{self.label}: runs successfully")
                output_lines = len([l for l in output.strip().split('\n') if l.strip()])
                if self.min_output_lines > 0:
                    if output_lines >= self.min_output_lines:
                        passed.append(f"{self.label}: {output_lines} lines output")
                    else:
                        failed.append(f"{self.label}: only {output_lines} lines (need {self.min_output_lines})")
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

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None):
        passed, failed = [], []
        for task_name in self.noise_tasks:
            if task_name in events.get("skills_invoked", []):
                passed.append(f"Invoked {task_name} skill")
            else:
                failed.append(f"Did NOT invoke {task_name} skill")

            output_file = get_noise_output(task_name)
            if (test_dir / output_file).exists():
                passed.append(f"Noise: {output_file} created")
            else:
                failed.append(f"Noise: {output_file} NOT created")
        return passed, failed


class MetricsCollector(Validator):
    """Collect metrics (always passes)."""

    def __init__(self, output_files: List[str] = None):
        self.output_files = output_files or []

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None):
        passed = []
        passed.append(f"Turns: {events.get('num_turns', 0) or 0}")
        passed.append(f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s")
        passed.append(f"Tool calls: {len(events.get('tool_calls', []))}")

        # Check for deprecated patterns
        deprecated = ["create_sql_agent", "AgentExecutor", "initialize_agent"]
        dep_count = sum(1 for tc in events.get("tool_calls", [])
                        if tc.get("tool") in ("Write", "Edit")
                        and any(d in str(tc.get("input", {})) for d in deprecated))
        if dep_count > 0:
            passed.append(f"Deprecated attempts: {dep_count}")
        return passed, []


class OutputQualityValidator(Validator):
    """Use LLM to evaluate output quality."""

    def __init__(self, filename: str, label: str, task_description: str, expected_behavior: str, run_args: List[str] = None):
        self.filename = filename
        self.label = label
        self.task_description = task_description
        self.expected_behavior = expected_behavior
        self.run_args = run_args or []

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            failed.append(f"{self.label}: file not created")
            return passed, failed

        if outputs and self.filename in outputs:
            success, output, duration = outputs[self.filename]
        else:
            success, output = run_python_file(test_dir, self.filename, self.run_args)
            duration = None

        if not success:
            failed.append(f"{self.label}: runtime error - {output[:100]}")
            return passed, failed
            
        dur_str = f" in {duration:.1f}s" if duration else ""
        passed.append(f"{self.label}: produced output ({len(output)} chars{dur_str})")

        # LLM evaluation
        sample = output[:3000] if len(output) > 3000 else output
        prompt = f"""Evaluate this program output.

Task: {self.task_description}
Expected: {self.expected_behavior}

Output:
```
{sample}
```

Does this demonstrate the expected behavior?"""

        result = evaluate_with_schema(prompt)
        status = "GOOD" if result["pass"] else "LOW"
        passed.append(f"{self.label} quality [{status}]: {result['reason']}")

        return passed, failed
