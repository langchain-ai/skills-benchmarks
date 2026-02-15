"""Testing scaffold for Claude Code skill benchmarks."""

from .utils import (
    # Retry
    retry_with_backoff,
    # CLI checks
    check_docker_available, check_claude_available,
    # Docker
    build_docker_image, run_in_docker, run_python_in_docker, run_claude_in_docker,
    # Parsing helpers
    read_json_file, get_field, get_nested_field, normalize_score, extract_score,
    # Model evaluation
    get_eval_model, evaluate_with_schema,
)
from .runner import (
    TestResult,
    WorkItem, run_single, run_parallel, create_work_items,
    run_experiment, print_summary,
)
from .setup import (
    verify_environment,
    setup_test_environment, cleanup_test_environment,
    build_skill, write_skill, setup_test_context,
    NOISE_TASKS, get_noise_prompt, get_noise_output, get_noise_skill_content,
)
from .config import Treatment
from .validation import (
    Validator,
    SkillInvokedValidator, PythonFileValidator, NoiseTaskValidator,
    MetricsCollector, OutputQualityValidator,
)
from .logging import (
    ExperimentLogger, TreatmentResult, ReportColumn,
    bool_column, quality_column, default_columns,
    parse_output, extract_events, strip_ansi,
    save_events, save_raw, save_report,
)

__all__ = [
    # Utils (retry, docker, checks, parsing, model eval)
    'retry_with_backoff',
    'check_docker_available', 'check_claude_available',
    'build_docker_image', 'run_in_docker', 'run_python_in_docker', 'run_claude_in_docker',
    'read_json_file', 'get_field', 'get_nested_field', 'normalize_score', 'extract_score',
    'get_eval_model', 'evaluate_with_schema',
    # Runner (parallel execution)
    'TestResult',
    'WorkItem', 'run_single', 'run_parallel', 'create_work_items',
    'run_experiment', 'print_summary',
    # Setup
    'verify_environment',
    'setup_test_environment', 'cleanup_test_environment',
    'build_skill', 'write_skill', 'setup_test_context',
    'NOISE_TASKS', 'get_noise_prompt', 'get_noise_output', 'get_noise_skill_content',
    # Config
    'Treatment',
    # Validators
    'Validator',
    'SkillInvokedValidator', 'PythonFileValidator', 'NoiseTaskValidator',
    'MetricsCollector', 'OutputQualityValidator',
    # Logging
    'ExperimentLogger', 'TreatmentResult', 'ReportColumn',
    'bool_column', 'quality_column', 'default_columns',
    'parse_output', 'extract_events', 'strip_ansi',
    'save_events', 'save_raw', 'save_report',
]
