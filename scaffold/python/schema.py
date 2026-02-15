"""Python schema for skill benchmarks.

Provides the NoiseTask and Treatment dataclasses for defining experimental conditions.

Example:
    from scaffold import Treatment, NoiseTask, PythonFileValidator
    from tests.noise import get_tasks

    TREATMENTS = {
        "BASELINE": Treatment(
            description="Test with skill",
            skills={"my-skill": [HEADER, EXAMPLES]},
            validators=[PythonFileValidator("output.py", required={"pattern": "desc"})],
        ),
        "WITH_NOISE": Treatment(
            description="Test with noise tasks",
            noise_tasks=get_tasks(["docker-patterns", "react-components"]),
        ),
    }
"""

from dataclasses import dataclass, field
from pathlib import Path

from .validation import NoiseTaskValidator, OutputQualityValidator, PythonFileValidator, Validator


@dataclass
class NoiseTask:
    """A distractor task with a prompt and expected deliverables."""

    prompt: str
    deliverables: list[str]  # Files this task should create


@dataclass
class Treatment:
    """Configuration for a single experiment."""

    description: str
    skills: dict[str, list[str]] = field(default_factory=dict)
    claude_md: str | None = None
    noise_tasks: list[NoiseTask] = field(default_factory=list)
    validators: list[Validator] = field(default_factory=list)

    def get_files_to_run(self) -> list[str]:
        """Get list of files that validators need to run."""
        files = []
        for v in self.validators:
            if isinstance(v, OutputQualityValidator):
                files.append(v.filename)
            elif isinstance(v, PythonFileValidator) and v.run_file:
                files.append(v.filename)
        return list(dict.fromkeys(files))

    def build_prompt(self, base_prompt: str, task2_prompt: str = None) -> str:
        """Build experiment prompt, inserting noise tasks if present."""
        if not self.noise_tasks:
            if task2_prompt:
                return f"Complete these tasks in order:\n\n1. {base_prompt}\n\n2. {task2_prompt}"
            return base_prompt

        parts = [f"1. {base_prompt}"]
        for i, task in enumerate(self.noise_tasks, start=2):
            parts.append(f"{i}. {task.prompt}")
        if task2_prompt:
            parts.append(f"{len(parts) + 1}. {task2_prompt}")

        return "Complete these tasks in order:\n\n" + "\n\n".join(parts)

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        """Run all validators and return (passed, failed) lists."""
        all_passed, all_failed = [], []

        for validator in self.validators:
            passed, failed = validator.validate(events, test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)

        if self.noise_tasks:
            expected_files = [f for t in self.noise_tasks for f in t.deliverables]
            passed, failed = NoiseTaskValidator(expected_files).validate(events, test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)

        return all_passed, all_failed
