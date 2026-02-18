"""Task loader for self-contained benchmark tasks.

Each task is a directory containing:
- instruction.md: Task prompt with {variable} placeholders
- task.toml: Task metadata (name, description, difficulty, template vars, validators)
- environment/: Docker context (Dockerfile, source code)
- validation/: Validator implementations
- data/: Test data and ground truth (optional)

Usage:
    from scaffold.tasks import load_task, list_tasks

    task = load_task("ls-evaluator")
    prompt = task.render_prompt(py_dataset="ds-py", ts_dataset="ds-ts", run_id="abc123")
    validators = task.load_validators()
"""

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python < 3.11


TASKS_DIR = Path(__file__).parent.parent / "tasks"


@dataclass
class TaskConfig:
    """Configuration loaded from task.toml."""

    name: str
    description: str
    difficulty: str = "medium"
    category: str = ""
    tags: list[str] = field(default_factory=list)

    # Template variables required for instruction.md
    template_required: list[str] = field(default_factory=list)

    # Environment settings
    dockerfile: str = "Dockerfile"
    timeout_sec: int = 900

    # Validators to run
    validators: list[str] = field(default_factory=list)


@dataclass
class Task:
    """A self-contained benchmark task."""

    path: Path
    config: TaskConfig
    instruction_template: str

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def environment_dir(self) -> Path:
        return self.path / "environment"

    @property
    def validation_dir(self) -> Path:
        return self.path / "validation"

    @property
    def data_dir(self) -> Path:
        return self.path / "data"

    def render_prompt(self, **kwargs: Any) -> str:
        """Render the instruction template with provided variables.

        Args:
            **kwargs: Template variables (e.g., run_id, py_dataset, ts_dataset)

        Returns:
            Rendered prompt string

        Raises:
            KeyError: If a required template variable is missing
        """
        missing = set(self.config.template_required) - set(kwargs.keys())
        if missing:
            raise KeyError(f"Missing required template variables: {missing}")
        return self.instruction_template.format(**kwargs)

    def load_validators(self) -> list:
        """Load function-based validators from the task's validation module.

        Returns:
            List of validator functions from VALIDATORS in validators.py

        Raises:
            ImportError: If validation module cannot be loaded
        """
        validators_path = self.validation_dir / "validators.py"
        if not validators_path.exists():
            return []

        module_name = f"tasks.{self.name}.validation.validators"
        spec = importlib.util.spec_from_file_location(module_name, validators_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load validators from {validators_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Return the VALIDATORS list
        if hasattr(module, "VALIDATORS"):
            return list(module.VALIDATORS)

        return []


def load_task(name: str, tasks_dir: Path | None = None) -> Task:
    """Load a task by name.

    Args:
        name: Task directory name (e.g., "ls-evaluator")
        tasks_dir: Optional custom tasks directory

    Returns:
        Task object with config and instruction template
    """
    tasks_dir = tasks_dir or TASKS_DIR
    task_path = tasks_dir / name

    if not task_path.exists():
        raise FileNotFoundError(f"Task not found: {name} (looked in {tasks_dir})")

    # Load task.toml
    toml_path = task_path / "task.toml"
    if not toml_path.exists():
        raise FileNotFoundError(f"task.toml not found in {task_path}")

    with open(toml_path, "rb") as f:
        toml_data = tomllib.load(f)

    metadata = toml_data.get("metadata", {})
    template = toml_data.get("template", {})
    environment = toml_data.get("environment", {})
    validation = toml_data.get("validation", {})

    config = TaskConfig(
        name=metadata.get("name", name),
        description=metadata.get("description", ""),
        difficulty=metadata.get("difficulty", "medium"),
        category=metadata.get("category", ""),
        tags=metadata.get("tags", []),
        template_required=template.get("required", []),
        dockerfile=environment.get("dockerfile", "Dockerfile"),
        timeout_sec=environment.get("timeout_sec", 900),
        validators=validation.get("validators", []),
    )

    # Load instruction.md
    instruction_path = task_path / "instruction.md"
    if not instruction_path.exists():
        raise FileNotFoundError(f"instruction.md not found in {task_path}")

    instruction_template = instruction_path.read_text()

    return Task(path=task_path, config=config, instruction_template=instruction_template)


def list_tasks(tasks_dir: Path | None = None) -> list[str]:
    """List available task names.

    Args:
        tasks_dir: Optional custom tasks directory

    Returns:
        List of task directory names
    """
    tasks_dir = tasks_dir or TASKS_DIR
    if not tasks_dir.exists():
        return []

    return sorted(
        d.name
        for d in tasks_dir.iterdir()
        if d.is_dir() and (d / "task.toml").exists() and (d / "instruction.md").exists()
    )
