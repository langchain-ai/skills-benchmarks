"""LangSmith tracing pattern validation for Python and TypeScript.

Validates that code has correct LangSmith tracing patterns:
- Imports (traceable, wrap_openai/wrapOpenAI)
- Client wrapping
- Function decorators/wrappers
- LangSmith API trace verification
"""

import re
from pathlib import Path

from scaffold.python.validation.langsmith import get_langsmith_client

# UUID pattern for trace IDs
UUID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)


def _to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def validate_python_tracing(
    test_dir: Path,
    filepath: str = "backend/sql_agent.py",
    required_functions: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate Python LangSmith tracing patterns.

    Checks:
    - Imports traceable from langsmith
    - Imports wrap_openai from langsmith.wrappers
    - Wraps OpenAI client with wrap_openai()
    - Required functions have @traceable decorator

    Args:
        test_dir: Test working directory
        filepath: Relative path to Python file
        required_functions: Function names that must have @traceable

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []
    path = test_dir / filepath

    if not path.exists():
        return [], [f"Python: {filepath} not found"]

    content = path.read_text()

    # Check imports
    if re.search(r"from\s+langsmith\s+import\s+.*traceable", content, re.IGNORECASE):
        passed.append("Python: imports traceable")
    else:
        failed.append("Python: missing 'from langsmith import traceable'")

    if re.search(r"from\s+langsmith\.wrappers\s+import\s+wrap_openai", content, re.IGNORECASE):
        passed.append("Python: imports wrap_openai")
    else:
        failed.append("Python: missing 'from langsmith.wrappers import wrap_openai'")

    # Check client wrapping
    if re.search(r"wrap_openai\s*\(\s*OpenAI\s*\(\s*\)\s*\)", content):
        passed.append("Python: wraps OpenAI client")
    else:
        failed.append("Python: missing 'wrap_openai(OpenAI())'")

    # Check functions are decorated
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


def validate_typescript_tracing(
    test_dir: Path,
    filepath: str = "frontend/support_bot.ts",
    required_functions: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate TypeScript LangSmith tracing patterns.

    Checks:
    - Imports traceable from langsmith/traceable
    - Imports wrapOpenAI from langsmith/wrappers
    - Wraps OpenAI client with wrapOpenAI()
    - Required functions are wrapped with traceable()

    Args:
        test_dir: Test working directory
        filepath: Relative path to TypeScript file
        required_functions: Function names that must be wrapped with traceable()

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []
    path = test_dir / filepath

    if not path.exists():
        return [], [f"TypeScript: {filepath} not found"]

    content = path.read_text()

    # Check imports
    if re.search(r'import\s+\{[^}]*traceable[^}]*\}\s+from\s+["\']langsmith/traceable["\']', content):
        passed.append("TypeScript: imports traceable")
    else:
        failed.append("TypeScript: missing 'import { traceable } from \"langsmith/traceable\"'")

    if re.search(r'import\s+\{[^}]*wrapOpenAI[^}]*\}\s+from\s+["\']langsmith/wrappers["\']', content):
        passed.append("TypeScript: imports wrapOpenAI")
    else:
        failed.append("TypeScript: missing 'import { wrapOpenAI } from \"langsmith/wrappers\"'")

    # Check client wrapping
    if re.search(r"wrapOpenAI\s*\(\s*new\s+OpenAI\s*\(\s*\)\s*\)", content):
        passed.append("TypeScript: wraps OpenAI client")
    else:
        failed.append("TypeScript: missing 'wrapOpenAI(new OpenAI())'")

    # Check functions are wrapped
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


def validate_language_syntax(
    test_dir: Path,
    python_file: str = "backend/sql_agent.py",
    typescript_file: str = "frontend/support_bot.ts",
) -> tuple[list[str], list[str]]:
    """Validate that each file uses correct language syntax (no mixing).

    Checks that Python files don't have TypeScript patterns and vice versa.

    Args:
        test_dir: Test working directory
        python_file: Relative path to Python file
        typescript_file: Relative path to TypeScript file

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []

    # Python-only patterns (shouldn't appear in TypeScript)
    py_only_patterns = [
        (re.compile(r"^def\s+\w+\s*\(", re.MULTILINE), "Python def"),
        (re.compile(r"^@\w+", re.MULTILINE), "Python decorator"),
    ]

    # TypeScript-only patterns (shouldn't appear in Python)
    ts_only_patterns = [
        (re.compile(r":\s*(string|number|boolean|Promise<)"), "TypeScript type annotation"),
        (re.compile(r"^(const|let)\s+\w+\s*=", re.MULTILINE), "TypeScript const/let"),
        (re.compile(r"async\s+\([^)]*\)\s*=>"), "TypeScript async arrow"),
    ]

    # Check Python file doesn't have TypeScript patterns
    py_path = test_dir / python_file
    if py_path.exists():
        content = py_path.read_text()
        ts_found = [desc for pattern, desc in ts_only_patterns if pattern.search(content)]
        if ts_found:
            failed.append(f"Python: contains TypeScript syntax ({len(ts_found)} patterns)")
        else:
            passed.append("Python: correct syntax")

    # Check TypeScript file doesn't have Python patterns
    ts_path = test_dir / typescript_file
    if ts_path.exists():
        content = ts_path.read_text()
        py_found = [desc for pattern, desc in py_only_patterns if pattern.search(content)]
        if py_found:
            failed.append(f"TypeScript: contains Python syntax ({len(py_found)} patterns)")
        else:
            passed.append("TypeScript: correct syntax")

    return passed, failed


def validate_langsmith_trace(
    test_dir: Path,
    outputs: dict,
    trace_id_file: str = "trace_id.txt",
    expected_functions: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate that LangSmith traces were created correctly.

    Reads trace IDs from file and verifies:
    1. Traces exist in LangSmith
    2. Traces have child runs for traced functions
    3. Child run names match expected function names

    Args:
        test_dir: Test working directory
        outputs: Outputs dict (can store trace_ids and child_run_names)
        trace_id_file: Name of file containing trace ID(s)
        expected_functions: Optional list of expected traced function names

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []

    # Read trace ID from file
    trace_file = test_dir / trace_id_file
    if not trace_file.exists():
        failed.append(f"LangSmith: {trace_id_file} not found")
        return passed, failed

    content = trace_file.read_text().strip()
    if not content:
        failed.append(f"LangSmith: {trace_id_file} is empty")
        return passed, failed

    # Extract all UUIDs from the content
    trace_ids = UUID_PATTERN.findall(content)
    if not trace_ids:
        failed.append(f"LangSmith: no valid trace IDs found in {trace_id_file}")
        return passed, failed

    passed.append(f"LangSmith: found {len(trace_ids)} trace ID(s)")

    # Get LangSmith client
    client, error = get_langsmith_client()
    if not client:
        failed.append(f"LangSmith: client error: {error}")
        return passed, failed

    # Validate each trace
    all_child_names = []
    for trace_id in trace_ids:
        try:
            run = client.read_run(trace_id)
            passed.append(f"LangSmith: trace {trace_id[:8]}... exists (name: {run.name})")

            # Check run type
            if run.run_type == "chain":
                passed.append(f"LangSmith: {trace_id[:8]}... has run_type='chain'")

            # Check for child runs
            child_runs = list(client.list_runs(parent_run_id=trace_id, limit=20))
            if child_runs:
                child_names = [r.name for r in child_runs]
                all_child_names.extend(child_names)
                passed.append(f"LangSmith: {trace_id[:8]}... has {len(child_runs)} child runs")
            else:
                failed.append(f"LangSmith: {trace_id[:8]}... has no child runs")

        except Exception as e:
            failed.append(f"LangSmith: trace {trace_id[:8]}... error: {str(e)[:50]}")

    # Check for expected function names
    if expected_functions:
        # Include camelCase variants
        expected_set = set(expected_functions)
        for func in expected_functions:
            camel = "".join(
                word.title() if i > 0 else word for i, word in enumerate(func.split("_"))
            )
            expected_set.add(camel)

        found_funcs = [n for n in all_child_names if n in expected_set]
        if found_funcs:
            passed.append(f"LangSmith: found traced functions: {', '.join(set(found_funcs))}")

    # Store trace info in outputs
    if outputs is not None:
        outputs["trace_ids"] = trace_ids
        outputs["child_run_names"] = all_child_names

    return passed, failed
