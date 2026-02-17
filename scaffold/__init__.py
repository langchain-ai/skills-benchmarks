"""Testing scaffold for Claude Code skill benchmarks.

Structure:
- scaffold/shell/   - Language-agnostic shell scripts (source of truth)
- scaffold/python/  - Python wrappers and pytest utilities

Usage:
    from scaffold import Treatment, NoiseTask, Validator
    from scaffold.python import ExperimentLogger, parse_output, extract_events
    from tests.noise import get_task, get_tasks
"""

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

__all__ = [
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
