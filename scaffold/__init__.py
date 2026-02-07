"""Testing scaffold for Claude Code skill benchmarks."""

from .runner import (
    TestResult,
    build_docker_image, run_in_docker, run_python_in_docker,
    WorkItem, run_single, run_parallel, create_work_items,
)
from .setup import (
    check_docker_available, verify_environment,
    setup_test_environment, cleanup_test_environment,
    build_skill, write_skill, setup_test_context,
    NOISE_TASKS, get_noise_prompt, get_noise_output, get_noise_skill_content,
)
from .framework import (
    Treatment, Validator,
    SkillInvokedValidator, PythonFileValidator, NoiseTaskValidator,
    MetricsCollector, OutputQualityValidator,
)
from .model import (
    EVAL_MODEL, get_eval_model, evaluate_with_schema,
)
from .logging import (
    ExperimentLogger, TreatmentResult, ReportColumn,
    bool_column, quality_column, default_columns,
    parse_output, extract_events, strip_ansi,
    save_events, save_raw, save_report,
)

__all__ = [
    # Runner (Docker utilities + parallel execution)
    'TestResult',
    'build_docker_image', 'run_in_docker', 'run_python_in_docker',
    'WorkItem', 'run_single', 'run_parallel', 'create_work_items',
    # Setup
    'check_docker_available', 'verify_environment',
    'setup_test_environment', 'cleanup_test_environment',
    'build_skill', 'write_skill', 'setup_test_context',
    'NOISE_TASKS', 'get_noise_prompt', 'get_noise_output', 'get_noise_skill_content',
    # Framework
    'Treatment', 'Validator',
    'SkillInvokedValidator', 'PythonFileValidator', 'NoiseTaskValidator',
    'MetricsCollector', 'OutputQualityValidator',
    # Model
    'EVAL_MODEL', 'get_eval_model', 'evaluate_with_schema',
    # Logging
    'ExperimentLogger', 'TreatmentResult', 'ReportColumn',
    'bool_column', 'quality_column', 'default_columns',
    'parse_output', 'extract_events', 'strip_ansi',
    'save_events', 'save_raw', 'save_report',
]
