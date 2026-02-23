"""Task loader for self-contained benchmark tasks.

Each task is a directory containing:
- instruction.md: Task prompt with {variable} placeholders
- task.toml: Task metadata (name, description, difficulty, template vars, validators)
- environment/: Docker context (Dockerfile, source code)
- validation/: Validator implementations
- data/: Test data and ground truth (optional)

Usage:
    from scaffold.python.tasks import load_task, list_tasks

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


TASKS_DIR = Path(__file__).parent.parent.parent / "tasks"


@dataclass
class DataHandler:
    """A data handler triggered by file pattern match."""

    pattern: str  # Glob pattern relative to task data dir (e.g., "trace_*.jsonl")
    handler: str  # Handler name (e.g., "upload_traces")


@dataclass
class SetupConfig:
    """Setup configuration for a task.

    Defines data handlers and template variables that are computed at test time.
    """

    # Data handlers triggered by pattern matches
    data_handlers: list[DataHandler] = field(default_factory=list)

    # Template variables with format strings (can use {run_id})
    template_vars: dict[str, str] = field(default_factory=dict)


@dataclass
class TaskConfig:
    """Configuration loaded from task.toml."""

    name: str
    description: str
    difficulty: str = "medium"
    category: str = ""
    tags: list[str] = field(default_factory=list)

    # Description of what Claude has access to in this task environment
    environment_description: str = ""

    # Default treatments to test with this task
    default_treatments: list[str] = field(default_factory=list)

    # Template variables required for instruction.md
    template_required: list[str] = field(default_factory=list)

    # Environment settings
    dockerfile: str = "Dockerfile"
    timeout_sec: int = 900

    # Validators to run
    validators: list[str] = field(default_factory=list)

    # Setup configuration
    setup: SetupConfig = field(default_factory=SetupConfig)


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

    @property
    def default_treatments(self) -> list[str]:
        return self.config.default_treatments

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
        """Load function-based validators from the task's validation module(s).

        Discovers all files matching *validators*.py in the validation/ directory
        and collects their VALIDATORS lists.

        Returns:
            Combined list of validator functions from all validator modules

        Raises:
            ImportError: If a validation module cannot be loaded
        """
        if not self.validation_dir.exists():
            return []

        # Find all validator files (validators.py, custom_validators.py, etc.)
        validator_files = sorted(self.validation_dir.glob("*validators*.py"))
        if not validator_files:
            return []

        all_validators = []
        for validators_path in validator_files:
            module_name = f"tasks.{self.name}.validation.{validators_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, validators_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load validators from {validators_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Collect VALIDATORS list from this module
            if hasattr(module, "VALIDATORS"):
                all_validators.extend(module.VALIDATORS)

        return all_validators


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
    setup_data = toml_data.get("setup", {})

    # Parse setup config
    data_handlers = [
        DataHandler(pattern=d["pattern"], handler=d["handler"]) for d in setup_data.get("data", [])
    ]
    setup = SetupConfig(
        data_handlers=data_handlers,
        template_vars=setup_data.get("template_vars", {}),
    )

    config = TaskConfig(
        name=metadata.get("name", name),
        description=metadata.get("description", ""),
        difficulty=metadata.get("difficulty", "medium"),
        category=metadata.get("category", ""),
        tags=metadata.get("tags", []),
        environment_description=environment.get("description", ""),
        default_treatments=metadata.get("default_treatments", []),
        template_required=template.get("required", []),
        dockerfile=environment.get("dockerfile", "Dockerfile"),
        timeout_sec=environment.get("timeout_sec", 900),
        validators=validation.get("validators", []),
        setup=setup,
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
