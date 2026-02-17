"""Testing scaffold for Claude Code skill benchmarks.

Structure:
- scaffold/shell/   - Language-agnostic shell scripts (source of truth)
- scaffold/python/  - Python wrappers and pytest utilities
- scaffold/tasks.py - Task loader for self-contained benchmark tasks

Usage:
    from scaffold import Treatment, NoiseTask, Validator
    from scaffold.python import ExperimentLogger, parse_output, extract_events
    from scaffold.tasks import load_task, list_tasks
"""

# Re-export task utilities
# Re-export from scaffold.python for convenience
from .python import (
    MetricsCollector,
    # Schema
    NoiseTask,
    NoiseTaskValidator,
    OutputQualityValidator,
    PythonFileValidator,
    SkillInvokedValidator,
    Treatment,
    # Validation
    Validator,
    build_docker_image,
    check_claude_available,
    check_docker_available,
    evaluate_with_schema,
    get_eval_model,
    get_field,
    get_nested_field,
    normalize_score,
    read_json_file,
    retry_with_backoff,
    run_claude_in_docker,
    run_in_docker,
    run_node_in_docker,
    run_python_in_docker,
    # Utils
    run_shell,
)
from .tasks import Task, TaskConfig, list_tasks, load_task

# Re-export validation utilities
from .validation import (
    compose_validators,
    run_validators,
    validate_file_exists,
    validate_function_decorated,
    validate_no_pattern,
    validate_pattern,
    validate_python_tracing,
    validate_typescript_tracing,
)

__all__ = [
    # Tasks
    "Task",
    "TaskConfig",
    "load_task",
    "list_tasks",
    # Validation functions
    "validate_file_exists",
    "validate_pattern",
    "validate_no_pattern",
    "validate_function_decorated",
    "validate_python_tracing",
    "validate_typescript_tracing",
    "compose_validators",
    "run_validators",
    # Schema
    "NoiseTask",
    "Treatment",
    # Validation
    "Validator",
    "SkillInvokedValidator",
    "PythonFileValidator",
    "NoiseTaskValidator",
    "MetricsCollector",
    "OutputQualityValidator",
    # Utils
    "run_shell",
    "check_docker_available",
    "check_claude_available",
    "build_docker_image",
    "run_in_docker",
    "run_python_in_docker",
    "run_node_in_docker",
    "run_claude_in_docker",
    "retry_with_backoff",
    "read_json_file",
    "get_field",
    "get_nested_field",
    "normalize_score",
    "get_eval_model",
    "evaluate_with_schema",
]
