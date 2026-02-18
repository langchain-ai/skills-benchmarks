"""Testing scaffold for Claude Code skill benchmarks.

Structure:
- scaffold/shell/   - Language-agnostic shell scripts (source of truth)
- scaffold/python/  - Python wrappers, pytest utilities, task/treatment loaders
- scaffold/typescript/ - TypeScript equivalents for parity

Usage:
    from scaffold import Treatment, NoiseTask, Validator
    from scaffold.python import ExperimentLogger, parse_output, extract_events
    from scaffold.python.tasks import load_task, list_tasks
    from scaffold.python.treatments import load_task_treatments, build_treatment_skills

    # Function-based validators (preferred)
    from scaffold import validate_python_tracing, validate_code_execution
"""

# Re-export task utilities from python subpackage
from .python.tasks import Task, TaskConfig, list_tasks, load_task
from .python.treatments import (
    TreatmentConfig,
    build_treatment_skills,
    get_task_treatment_names,
    list_treatments,
    load_task_treatments,
    load_treatment,
    load_treatments_yaml,
)

# Re-export from scaffold.python for convenience
from .python import (
    # Schema
    NoiseTask,
    Treatment,
    # Class-based validators (legacy)
    Validator,
    SkillInvokedValidator,
    PythonFileValidator,
    NoiseTaskValidator,
    MetricsCollector,
    OutputQualityValidator,
    # Function-based validators (preferred)
    ValidatorFn,
    compose_validators,
    run_validators,
    validate_file_exists,
    validate_pattern,
    validate_no_pattern,
    validate_python_tracing,
    validate_typescript_tracing,
    validate_language_syntax,
    validate_code_execution,
    validate_python_execution,
    validate_typescript_execution,
    validate_langsmith_trace,
    validate_evaluator_upload,
    validate_dataset_structure,
    validate_dataset_upload,
    validate_trajectory_accuracy,
    validate_evaluator_exists,
    validate_evaluator_syntax,
    validate_evaluator_patterns,
    validate_evaluator_logic,
    validate_skill_invoked,
    validate_noise_outputs,
    validate_skill_scripts,
    get_noise_task_prompts,
    NOISE_TASK_DELIVERABLES,
    NOISE_TASK_PROMPTS,
    get_langsmith_client,
    safe_api_call,
    extract_examples,
    find_evaluator_function,
    # Utils
    run_shell,
    check_docker_available,
    check_claude_available,
    build_docker_image,
    run_in_docker,
    run_python_in_docker,
    run_node_in_docker,
    run_claude_in_docker,
    retry_with_backoff,
    read_json_file,
    get_field,
    get_nested_field,
    normalize_score,
    get_eval_model,
    evaluate_with_schema,
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
    "load_treatments_yaml",
    # Schema
    "NoiseTask",
    "Treatment",
    # Class-based validators (legacy)
    "Validator",
    "SkillInvokedValidator",
    "PythonFileValidator",
    "NoiseTaskValidator",
    "MetricsCollector",
    "OutputQualityValidator",
    # Function-based validators (preferred)
    "ValidatorFn",
    "compose_validators",
    "run_validators",
    "validate_file_exists",
    "validate_pattern",
    "validate_no_pattern",
    "validate_python_tracing",
    "validate_typescript_tracing",
    "validate_language_syntax",
    "validate_code_execution",
    "validate_python_execution",
    "validate_typescript_execution",
    "validate_langsmith_trace",
    "validate_evaluator_upload",
    "validate_dataset_structure",
    "validate_dataset_upload",
    "validate_trajectory_accuracy",
    "validate_evaluator_exists",
    "validate_evaluator_syntax",
    "validate_evaluator_patterns",
    "validate_evaluator_logic",
    "validate_skill_invoked",
    "validate_noise_outputs",
    "validate_skill_scripts",
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
