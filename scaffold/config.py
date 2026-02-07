"""Experiment configuration for skill benchmarks.

Provides the Treatment dataclass for defining experimental conditions.

Example:
    from scaffold import Treatment, PythonFileValidator

    TREATMENTS = {
        "BASELINE": Treatment(
            description="Test with skill",
            skills={"my-skill": [HEADER, EXAMPLES]},
            validators=[PythonFileValidator("output.py", required={"pattern": "desc"})],
        ),
    }
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional

from .setup import get_noise_prompt
from .validation import Validator, NoiseTaskValidator, OutputQualityValidator, PythonFileValidator


@dataclass
class Treatment:
    """Configuration for a single experiment."""

    description: str
    skills: Dict[str, List[str]] = field(default_factory=dict)
    claude_md: Optional[str] = None
    noise_tasks: List[str] = field(default_factory=list)
    validators: List[Validator] = field(default_factory=list)

    def get_files_to_run(self) -> List[str]:
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

        noise_prompts = [get_noise_prompt(t) for t in self.noise_tasks]
        parts = [f"1. {base_prompt}"]
        for i, noise in enumerate(noise_prompts, start=2):
            parts.append(f"{i}. {noise}")
        if task2_prompt:
            parts.append(f"{len(parts) + 1}. {task2_prompt}")

        return "Complete these tasks in order:\n\n" + "\n\n".join(parts)

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> tuple[List[str], List[str]]:
        """Run all validators and return (passed, failed) lists."""
        all_passed, all_failed = [], []

        for validator in self.validators:
            passed, failed = validator.validate(events, test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)

        if self.noise_tasks:
            passed, failed = NoiseTaskValidator(self.noise_tasks).validate(events, test_dir, outputs)
            all_passed.extend(passed)
            all_failed.extend(failed)

        return all_passed, all_failed
