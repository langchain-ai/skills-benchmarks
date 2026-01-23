"""
Testing scaffold for Claude Code skill benchmarks.

Components:
- runner: Execute Claude Code and capture events
- capture: Parse and analyze tool call events
- setup: Test environment setup/cleanup
"""

from .runner import run_test, run_comparison, ContextMode, TestResult
from .capture import extract_events, did_read, did_create, tool_count
from .setup import setup_test_environment, cleanup_test_environment

__all__ = [
    'run_test', 'run_comparison', 'ContextMode', 'TestResult',
    'extract_events', 'did_read', 'did_create', 'tool_count',
    'setup_test_environment', 'cleanup_test_environment',
]
