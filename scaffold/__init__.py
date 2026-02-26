"""Testing scaffold for Claude Code skill benchmarks.

Structure:
- scaffold/shell/   - Language-agnostic shell scripts (source of truth)
- scaffold/python/  - Python wrappers, pytest utilities, task/treatment loaders
- scaffold/typescript/ - TypeScript equivalents for parity

Usage:
    from scaffold import Treatment, NoiseTask
    from scaffold.python.utils import make_execution_validator
    from scaffold.python.tasks import load_task, list_tasks
"""

# Re-export task utilities from python subpackage
# Re-export from scaffold.python for convenience
from .python import (
    NOISE_TASK_DELIVERABLES,
    NOISE_TASK_PROMPTS,
    # Schema
    NoiseTask,
    Treatment,
    # Validation helpers
    ValidatorFn,
    build_docker_image,
    check_claude_available,
    check_docker_available,
    compose_validators,
    evaluate_with_schema,
    extract_examples,
    find_evaluator_function,
    get_eval_model,
    get_field,
    get_langsmith_client,
    get_nested_field,
    get_noise_task_prompts,
    normalize_score,
    read_json_file,
    retry_with_backoff,
    run_claude_in_docker,
    run_node_in_docker,
    run_python_in_docker,
    make_execution_validator,
    run_eval_in_docker,
    # Utils
    run_shell,
    run_validators,
    safe_api_call,
    check_code_execution,
    check_dataset_structure,
    check_dataset_upload,
    check_evaluator_exists,
    check_evaluator_logic,
    check_evaluator_patterns,
    check_evaluator_syntax,
    check_evaluator_upload,
    check_file_exists,
    check_langsmith_trace,
    check_language_syntax,
    check_no_pattern,
    check_noise_outputs,
    check_pattern,
    check_python_execution,
    check_python_tracing,
    check_skill_invoked,
    check_skill_scripts,
    check_trajectory_accuracy,
    check_typescript_execution,
    check_typescript_tracing,
)
from .python.tasks import Task, TaskConfig, list_tasks, load_task
from .python.treatments import (
    TreatmentConfig,
    build_treatment_skills,
    get_task_treatment_names,
    list_treatments,
    load_task_treatments,
    load_treatment,
    load_treatments,
    load_treatments_yaml,
)

__all__ = [
    # Tasks
    "Task",
    "TaskConfig",
    "load_task",
    "list_tasks",
    # Treatments
    "TreatmentConfig",
    "build_treatment_skills",
    "get_task_treatment_names",
    "list_treatments",
    "load_task_treatments",
    "load_treatment",
    "load_treatments",
    "load_treatments_yaml",
    # Schema
    "NoiseTask",
    "Treatment",
    # Validation helpers
    "ValidatorFn",
    "compose_validators",
    "run_validators",
    "check_file_exists",
    "check_pattern",
    "check_no_pattern",
    "check_python_tracing",
    "check_typescript_tracing",
    "check_language_syntax",
    "check_code_execution",
    "check_python_execution",
    "check_typescript_execution",
    "check_langsmith_trace",
    "check_evaluator_upload",
    "check_dataset_structure",
    "check_dataset_upload",
    "check_trajectory_accuracy",
    "check_evaluator_exists",
    "check_evaluator_syntax",
    "check_evaluator_patterns",
    "check_evaluator_logic",
    "check_skill_invoked",
    "check_noise_outputs",
    "check_skill_scripts",
    "get_noise_task_prompts",
    "NOISE_TASK_DELIVERABLES",
    "NOISE_TASK_PROMPTS",
    "get_langsmith_client",
    "safe_api_call",
    "extract_examples",
    "find_evaluator_function",
    # Utils
    "run_shell",
    "check_docker_available",
    "check_claude_available",
    "build_docker_image",
    "run_in_docker",
    "run_python_in_docker",
    "make_execution_validator",
    "make_output_validator",
    "run_eval_in_docker",
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
