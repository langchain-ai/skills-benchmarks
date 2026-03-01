"""Test script for ls-lang-tracing validation.

Checks tracing patterns, language syntax, and code execution for both
Python and TypeScript files. Also validates LangSmith traces and skill
script usage.
"""

import re
import subprocess
import sys

from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import check_skill_scripts
from scaffold.python.validation.tracing import check_langsmith_trace

REQUIRED_FUNCTIONS = [
    "classify_intent",
    "extract_entities",
    "generate_response",
    "handle_support_request",
]


def check_python_tracing(runner: TestRunner):
    """Check Python LangSmith tracing patterns."""
    filepath = runner.artifacts[0]
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        runner.failed(f"Python: {filepath} not found")
        return

    if re.search(r"from\s+langsmith\s+import\s+.*traceable", content, re.IGNORECASE):
        runner.passed("Python: imports traceable")
    else:
        runner.failed("Python: missing 'from langsmith import traceable'")

    if re.search(r"from\s+langsmith\.wrappers\s+import\s+wrap_openai", content, re.IGNORECASE):
        runner.passed("Python: imports wrap_openai")
    else:
        runner.failed("Python: missing 'from langsmith.wrappers import wrap_openai'")

    if re.search(r"wrap_openai\s*\(\s*OpenAI\s*\(\s*\)\s*\)", content):
        runner.passed("Python: wraps OpenAI client")
    else:
        runner.failed("Python: missing 'wrap_openai(OpenAI())'")

    if REQUIRED_FUNCTIONS:
        traced, untraced = [], []
        for func in REQUIRED_FUNCTIONS:
            pattern = rf"@traceable[^@]*def\s+{func}\s*\("
            if re.search(pattern, content, re.DOTALL):
                traced.append(func)
            elif re.search(rf"def\s+{func}\s*\(", content):
                untraced.append(func)
        if traced:
            runner.passed(f"Python: traced {len(traced)} functions ({', '.join(traced)})")
        if untraced:
            runner.failed(f"Python: missing @traceable on: {', '.join(untraced)}")


def _to_camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def check_typescript_tracing(runner: TestRunner):
    """Check TypeScript LangSmith tracing patterns."""
    filepath = runner.artifacts[1]
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        runner.failed(f"TypeScript: {filepath} not found")
        return

    if re.search(
        r'import\s+\{[^}]*traceable[^}]*\}\s+from\s+["\']langsmith/traceable["\']', content
    ):
        runner.passed("TypeScript: imports traceable")
    else:
        runner.failed("TypeScript: missing 'import { traceable } from \"langsmith/traceable\"'")

    if re.search(
        r'import\s+\{[^}]*wrapOpenAI[^}]*\}\s+from\s+["\']langsmith/wrappers["\']', content
    ):
        runner.passed("TypeScript: imports wrapOpenAI")
    else:
        runner.failed("TypeScript: missing 'import { wrapOpenAI } from \"langsmith/wrappers\"'")

    if re.search(r"wrapOpenAI\s*\(\s*new\s+OpenAI\s*\(\s*\)\s*\)", content):
        runner.passed("TypeScript: wraps OpenAI client")
    else:
        runner.failed("TypeScript: missing 'wrapOpenAI(new OpenAI())'")

    if REQUIRED_FUNCTIONS:
        traced, untraced = [], []
        for func in REQUIRED_FUNCTIONS:
            camel = _to_camel_case(func)
            patterns = [
                rf"const\s+{camel}\s*=\s*traceable\s*\(",
                rf"const\s+{func}\s*=\s*traceable\s*\(",
                rf'name\s*:\s*["\']{func}["\']',
            ]
            if any(re.search(p, content) for p in patterns):
                traced.append(func)
            else:
                func_patterns = [
                    rf"(const|let|function)\s+{camel}\s*[=\(]",
                    rf"async\s+function\s+{camel}\s*\(",
                ]
                if any(re.search(p, content) for p in func_patterns):
                    untraced.append(func)
        if traced:
            runner.passed(f"TypeScript: traced {len(traced)} functions ({', '.join(traced)})")
        if untraced:
            runner.failed(f"TypeScript: missing traceable() on: {', '.join(untraced)}")


def check_language_syntax(runner: TestRunner):
    """Check that files use correct language (no mixing)."""
    py_file = runner.artifacts[0]
    ts_file = runner.artifacts[1]

    ts_only = [
        (re.compile(r":\s*(string|number|boolean|Promise<)"), "TypeScript type annotation"),
        (re.compile(r"^(const|let)\s+\w+\s*=", re.MULTILINE), "TypeScript const/let"),
        (re.compile(r"async\s+\([^)]*\)\s*=>"), "TypeScript async arrow"),
    ]
    py_only = [
        (re.compile(r"^def\s+\w+\s*\(", re.MULTILINE), "Python def"),
        (re.compile(r"^@\w+", re.MULTILINE), "Python decorator"),
    ]

    try:
        py_content = open(py_file).read()
        ts_found = [d for p, d in ts_only if p.search(py_content)]
        if ts_found:
            runner.failed(f"Python: contains TypeScript syntax ({len(ts_found)} patterns)")
        else:
            runner.passed("Python: correct syntax")
    except FileNotFoundError:
        pass

    try:
        ts_content = open(ts_file).read()
        py_found = [d for p, d in py_only if p.search(ts_content)]
        if py_found:
            runner.failed(f"TypeScript: contains Python syntax ({len(py_found)} patterns)")
        else:
            runner.passed("TypeScript: correct syntax")
    except FileNotFoundError:
        pass


def check_execution(runner: TestRunner):
    """Check that both files execute without errors."""
    py_file = runner.artifacts[0]
    ts_file = runner.artifacts[1]

    try:
        r = subprocess.run([sys.executable, py_file], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            runner.passed(f"Python: {py_file} executes successfully")
        else:
            runner.failed(f"Python: execution failed ({(r.stderr or r.stdout)[:100]})")
    except Exception as e:
        runner.failed(f"Python: execution error ({str(e)[:80]})")

    # TypeScript execution via npx tsx
    try:
        r = subprocess.run(["npx", "tsx", ts_file], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            runner.passed(f"TypeScript: {ts_file} executes successfully")
        else:
            runner.failed(f"TypeScript: execution failed ({(r.stderr or r.stdout)[:100]})")
    except Exception as e:
        runner.failed(f"TypeScript: execution error ({str(e)[:80]})")


def check_trace(runner: TestRunner):
    """Validate that a trace was created in LangSmith."""
    from pathlib import Path

    p, f = check_langsmith_trace(
        Path("."),
        runner.context,
        trace_id_file="trace_id.txt",
        expected_functions=REQUIRED_FUNCTIONS,
    )
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


def check_scripts(runner: TestRunner):
    """Track which skill scripts Claude used (informational)."""
    events = runner.context.get("events", {}) if runner.context else {}
    p, f = check_skill_scripts(runner.context, events)
    for msg in p:
        runner.passed(msg)
    for msg in f:
        runner.failed(msg)


if __name__ == "__main__":
    TestRunner.run(
        [
            check_python_tracing,
            check_typescript_tracing,
            check_language_syntax,
            check_execution,
            check_trace,
            check_scripts,
        ]
    )
