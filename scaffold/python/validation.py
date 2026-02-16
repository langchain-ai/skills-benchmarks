"""Validators for experiment results."""

import ast
from abc import ABC, abstractmethod
from pathlib import Path

from .utils import evaluate_with_schema, run_python_in_docker


class Validator(ABC):
    """Base validator. Returns (passed: List[str], failed: List[str])."""

    @abstractmethod
    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        pass


class SkillInvokedValidator(Validator):
    """Check if a skill was invoked."""

    def __init__(self, skill_name: str, required: bool = True):
        self.skill_name, self.required = skill_name, required

    def validate(self, events: dict, test_dir: Path, outputs: dict = None):
        invoked = self.skill_name in events.get("skills_invoked", [])
        if invoked:
            return [f"Invoked {self.skill_name} skill"], []
        elif self.required:
            return [], [f"Did NOT invoke {self.skill_name} skill"]
        return [f"Note: did not invoke {self.skill_name}"], []


class PythonFileValidator(Validator):
    """Validate Python file existence, syntax, patterns, and optionally run it."""

    def __init__(
        self,
        filename: str,
        label: str = None,
        required: dict[str, str] = None,
        forbidden: dict[str, str] = None,
        any_of: dict[str, str] = None,
        run_file: bool = False,
        require_all: bool = False,
        run_args: list[str] = None,
        output_patterns: dict[str, str] = None,
        min_output_lines: int = 0,
    ):
        self.filename, self.label = filename, label or filename
        self.required, self.forbidden, self.any_of = required or {}, forbidden or {}, any_of or {}
        self.run_file, self.require_all, self.run_args = run_file, require_all, run_args or []
        self.output_patterns, self.min_output_lines = output_patterns or {}, min_output_lines

    def validate(self, events: dict, test_dir: Path, outputs: dict = None):
        passed, failed = [], []
        file_path = test_dir / self.filename

        if not file_path.exists():
            return [], [f"{self.label}: file not created"]

        content = file_path.read_text()
        passed.append(f"{self.label}: created")

        # Required patterns
        if self.required:
            found = [(p, d) for p, d in self.required.items() if p in content]
            missing = [(p, d) for p, d in self.required.items() if p not in content]
            if self.require_all:
                failed.extend(f"{self.label}: missing {d}" for _, d in missing)
                if found:
                    passed.append(f"{self.label}: {', '.join(d for _, d in found[:3])}")
            elif found:
                passed.append(f"{self.label}: {', '.join(d for _, d in found[:3])}")
            else:
                failed.append(f"{self.label}: missing required patterns")

        # Any-of patterns
        if self.any_of:
            found = [(p, d) for p, d in self.any_of.items() if p in content]
            if found:
                passed.append(f"{self.label}: {found[0][1]}")
            else:
                failed.append(
                    f"{self.label}: missing (need one of: {', '.join(d for _, d in self.any_of.items())})"
                )

        # Forbidden patterns
        for pattern, desc in self.forbidden.items():
            if pattern in content:
                failed.append(f"{self.label}: {desc}")

        # Syntax check
        try:
            ast.parse(content)
            passed.append(f"{self.label}: valid syntax")
        except SyntaxError as e:
            return passed, failed + [f"{self.label}: syntax error line {e.lineno}"]

        # Run file
        if self.run_file:
            success, output = (
                outputs[self.filename][:2]
                if outputs and self.filename in outputs
                else run_python_in_docker(test_dir, self.filename, args=self.run_args)
            )
            if success:
                passed.append(f"{self.label}: runs successfully")
                lines = len([line for line in output.strip().split("\n") if line.strip()])
                if self.min_output_lines and lines < self.min_output_lines:
                    failed.append(
                        f"{self.label}: only {lines} lines (need {self.min_output_lines})"
                    )
                elif self.min_output_lines:
                    passed.append(f"{self.label}: {lines} lines output")
                output_lower = output.lower()
                for pattern, desc in self.output_patterns.items():
                    match = pattern.lower() in output_lower
                    (passed if match else failed).append(
                        f"{self.label}: output {'has' if match else 'missing'} {desc}"
                    )
            else:
                failed.append(f"{self.label}: {output[:150]}")

        return passed, failed


class NoiseTaskValidator(Validator):
    """Validate noise task output files were created."""

    def __init__(self, output_files: list[str]):
        self.output_files = output_files

    def validate(self, events: dict, test_dir: Path, outputs: dict = None):
        passed, failed = [], []
        for f in self.output_files:
            (passed if (test_dir / f).exists() else failed).append(
                f"Noise: {f} {'created' if (test_dir / f).exists() else 'NOT created'}"
            )
        return passed, failed


class MetricsCollector(Validator):
    """Collect metrics (always passes)."""

    def __init__(self, output_files: list[str] = None):
        self.output_files = output_files or []

    def validate(self, events: dict, test_dir: Path, outputs: dict = None):
        passed = [
            f"Turns: {events.get('num_turns', 0) or 0}",
            f"Duration: {events.get('duration_seconds', 0) or 0:.0f}s",
            f"Tool calls: {len(events.get('tool_calls', []))}",
        ]
        deprecated = ["create_sql_agent", "AgentExecutor", "initialize_agent"]
        dep_count = sum(
            1
            for tc in events.get("tool_calls", [])
            if tc.get("tool") in ("Write", "Edit")
            and any(d in str(tc.get("input", {})) for d in deprecated)
        )
        if dep_count:
            passed.append(f"Deprecated attempts: {dep_count}")
        return passed, []


class OutputQualityValidator(Validator):
    """Use LLM to evaluate output quality."""

    def __init__(
        self,
        filename: str,
        label: str,
        task_description: str,
        expected_behavior: str,
        run_args: list[str] = None,
    ):
        self.filename, self.label = filename, label
        self.task_description, self.expected_behavior = task_description, expected_behavior
        self.run_args = run_args or []

    def validate(self, events: dict, test_dir: Path, outputs: dict = None):
        passed, failed = [], []
        if not (test_dir / self.filename).exists():
            return [], [f"{self.label}: file not created"]

        if outputs and self.filename in outputs:
            success, output, duration = outputs[self.filename]
        else:
            success, output = run_python_in_docker(test_dir, self.filename, args=self.run_args)
            duration = None

        if not success:
            return [], [f"{self.label}: runtime error - {output[:100]}"]

        dur_str = f" in {duration:.1f}s" if duration else ""
        passed.append(f"{self.label}: produced output ({len(output)} chars{dur_str})")

        prompt = f"""Evaluate this program output.
Task: {self.task_description}
Expected: {self.expected_behavior}
Output:
```
{output[:3000]}
```
Does this demonstrate the expected behavior?"""

        result = evaluate_with_schema(prompt)
        passed.append(
            f"{self.label} quality [{'GOOD' if result['pass'] else 'LOW'}]: {result['reason']}"
        )
        return passed, failed
