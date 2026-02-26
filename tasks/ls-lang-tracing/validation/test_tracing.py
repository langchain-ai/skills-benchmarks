"""Test script for ls-lang-tracing validation.

Checks tracing patterns, language syntax, and code execution for both
Python and TypeScript files. Runs inside Docker via make_execution_validator.

Usage: python test_tracing.py <python_file> <typescript_file>
"""

import ast
import importlib.util
import json
import re
import subprocess
import sys

REQUIRED_FUNCTIONS = [
    "classify_intent",
    "extract_entities",
    "generate_response",
    "handle_support_request",
]


def check_python_tracing(filepath, required_functions):
    """Check Python LangSmith tracing patterns."""
    passed, failed = [], []
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        return [], [f"Python: {filepath} not found"]

    if re.search(r"from\s+langsmith\s+import\s+.*traceable", content, re.IGNORECASE):
        passed.append("Python: imports traceable")
    else:
        failed.append("Python: missing 'from langsmith import traceable'")

    if re.search(r"from\s+langsmith\.wrappers\s+import\s+wrap_openai", content, re.IGNORECASE):
        passed.append("Python: imports wrap_openai")
    else:
        failed.append("Python: missing 'from langsmith.wrappers import wrap_openai'")

    if re.search(r"wrap_openai\s*\(\s*OpenAI\s*\(\s*\)\s*\)", content):
        passed.append("Python: wraps OpenAI client")
    else:
        failed.append("Python: missing 'wrap_openai(OpenAI())'")

    if required_functions:
        traced, untraced = [], []
        for func in required_functions:
            pattern = rf"@traceable[^@]*def\s+{func}\s*\("
            if re.search(pattern, content, re.DOTALL):
                traced.append(func)
            elif re.search(rf"def\s+{func}\s*\(", content):
                untraced.append(func)
        if traced:
            passed.append(f"Python: traced {len(traced)} functions ({', '.join(traced)})")
        if untraced:
            failed.append(f"Python: missing @traceable on: {', '.join(untraced)}")

    return passed, failed


def _to_camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def check_typescript_tracing(filepath, required_functions):
    """Check TypeScript LangSmith tracing patterns."""
    passed, failed = [], []
    try:
        content = open(filepath).read()
    except FileNotFoundError:
        return [], [f"TypeScript: {filepath} not found"]

    if re.search(
        r'import\s+\{[^}]*traceable[^}]*\}\s+from\s+["\']langsmith/traceable["\']', content
    ):
        passed.append("TypeScript: imports traceable")
    else:
        failed.append("TypeScript: missing 'import { traceable } from \"langsmith/traceable\"'")

    if re.search(
        r'import\s+\{[^}]*wrapOpenAI[^}]*\}\s+from\s+["\']langsmith/wrappers["\']', content
    ):
        passed.append("TypeScript: imports wrapOpenAI")
    else:
        failed.append("TypeScript: missing 'import { wrapOpenAI } from \"langsmith/wrappers\"'")

    if re.search(r"wrapOpenAI\s*\(\s*new\s+OpenAI\s*\(\s*\)\s*\)", content):
        passed.append("TypeScript: wraps OpenAI client")
    else:
        failed.append("TypeScript: missing 'wrapOpenAI(new OpenAI())'")

    if required_functions:
        traced, untraced = [], []
        for func in required_functions:
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
            passed.append(f"TypeScript: traced {len(traced)} functions ({', '.join(traced)})")
        if untraced:
            failed.append(f"TypeScript: missing traceable() on: {', '.join(untraced)}")

    return passed, failed


def check_language_syntax(py_file, ts_file):
    """Check that files use correct language (no mixing)."""
    passed, failed = [], []

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
            failed.append(f"Python: contains TypeScript syntax ({len(ts_found)} patterns)")
        else:
            passed.append("Python: correct syntax")
    except FileNotFoundError:
        pass

    try:
        ts_content = open(ts_file).read()
        py_found = [d for p, d in py_only if p.search(ts_content)]
        if py_found:
            failed.append(f"TypeScript: contains Python syntax ({len(py_found)} patterns)")
        else:
            passed.append("TypeScript: correct syntax")
    except FileNotFoundError:
        pass

    return passed, failed


def check_execution(py_file, ts_file):
    """Check that both files execute without errors."""
    passed, failed = [], []

    try:
        r = subprocess.run(["python", py_file], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            passed.append(f"Python: {py_file} executes successfully")
        else:
            failed.append(f"Python: execution failed ({(r.stderr or r.stdout)[:100]})")
    except Exception as e:
        failed.append(f"Python: execution error ({str(e)[:80]})")

    # TypeScript execution via npx tsx
    try:
        r = subprocess.run(
            ["npx", "tsx", ts_file], capture_output=True, text=True, timeout=60
        )
        if r.returncode == 0:
            passed.append(f"TypeScript: {ts_file} executes successfully")
        else:
            failed.append(f"TypeScript: execution failed ({(r.stderr or r.stdout)[:100]})")
    except Exception as e:
        failed.append(f"TypeScript: execution error ({str(e)[:80]})")

    return passed, failed


def run_tests(py_file, ts_file):
    passed, failed = [], []

    for p, f in [
        check_python_tracing(py_file, REQUIRED_FUNCTIONS),
        check_typescript_tracing(ts_file, REQUIRED_FUNCTIONS),
        check_language_syntax(py_file, ts_file),
        check_execution(py_file, ts_file),
    ]:
        passed.extend(p)
        failed.extend(f)

    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_tracing.py <python_file> <typescript_file>")
        sys.exit(1)
    results = run_tests(sys.argv[1], sys.argv[2])
    print(json.dumps(results, indent=2))
    sys.exit(1 if results["failed"] else 0)
