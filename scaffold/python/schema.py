"""Python schema for skill benchmarks.

Provides the NoiseTask and Treatment dataclasses for defining experimental conditions.
"""

from dataclasses import dataclass, field
from pathlib import Path


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

