"""Validators for LangSmith polyglot tracing benchmark."""

import ast
import json
import re
from pathlib import Path

from scaffold import Validator, run_node_in_docker, run_python_in_docker

# =============================================================================
# PATHS
# =============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
VALIDATION_DIR = Path(__file__).parent


def _get_langsmith_client():
    """Get LangSmith client."""
    try:
        from langsmith import Client

        return Client(), None
    except Exception as e:
        return None, str(e)


class TracingPatternValidator(Validator):
    """Validate that Claude added correct LangSmith tracing patterns to each function."""

    # Functions that must be traced
    REQUIRED_FUNCTIONS = [
        "classify_intent",
        "extract_entities",
        "lookup_order",
        "generate_response",
        "handle_support_request",  # main handler
    ]

    # Python tracing patterns
    PY_IMPORT_TRACEABLE = re.compile(r"from\s+langsmith\s+import\s+.*traceable", re.IGNORECASE)
    PY_IMPORT_WRAP = re.compile(r"from\s+langsmith\.wrappers\s+import\s+wrap_openai", re.IGNORECASE)
    PY_WRAP_CLIENT = re.compile(r"wrap_openai\s*\(\s*OpenAI\s*\(\s*\)\s*\)")
    PY_CHAIN_TYPE = re.compile(r'run_type\s*=\s*["\']chain["\']')

    # TypeScript tracing patterns
    TS_IMPORT_TRACEABLE = re.compile(
        r'import\s+\{[^}]*traceable[^}]*\}\s+from\s+["\']langsmith/traceable["\']', re.IGNORECASE
    )
    TS_IMPORT_WRAP = re.compile(
        r'import\s+\{[^}]*wrapOpenAI[^}]*\}\s+from\s+["\']langsmith/wrappers["\']', re.IGNORECASE
    )
    TS_WRAP_CLIENT = re.compile(r"wrapOpenAI\s*\(\s*new\s+OpenAI\s*\(\s*\)\s*\)")
    TS_CHAIN_TYPE = re.compile(r'run_type\s*:\s*["\']chain["\']')

    def __init__(
        self,
        python_file: str = "backend/support_bot.py",
        typescript_file: str = "frontend/support_bot.ts",
    ):
        self.python_file = python_file
        self.typescript_file = typescript_file

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Validate Python file
        py_path = test_dir / self.python_file
        if py_path.exists():
            py_passed, py_failed = self._validate_python(py_path)
            passed.extend(py_passed)
            failed.extend(py_failed)
        else:
            failed.append(f"Python: {self.python_file} not found")

        # Validate TypeScript file
        ts_path = test_dir / self.typescript_file
        if ts_path.exists():
            ts_passed, ts_failed = self._validate_typescript(ts_path)
            passed.extend(ts_passed)
            failed.extend(ts_failed)
        else:
            failed.append(f"TypeScript: {self.typescript_file} not found")

        return passed, failed

    def _validate_python(self, path: Path) -> tuple[list[str], list[str]]:
        """Validate Python tracing patterns."""
        passed, failed = [], []
        content = path.read_text()

        # Check imports
        if self.PY_IMPORT_TRACEABLE.search(content):
            passed.append("Python: imports traceable")
        else:
            failed.append("Python: missing 'from langsmith import traceable'")

        if self.PY_IMPORT_WRAP.search(content):
            passed.append("Python: imports wrap_openai")
        else:
            failed.append("Python: missing 'from langsmith.wrappers import wrap_openai'")

        # Check client wrapping
        if self.PY_WRAP_CLIENT.search(content):
            passed.append("Python: wraps OpenAI client")
        else:
            failed.append("Python: missing 'wrap_openai(OpenAI())'")

        # Check each function is decorated with @traceable
        traced_funcs, untraced_funcs = self._check_python_functions(content)
        if traced_funcs:
            passed.append(
                f"Python: traced {len(traced_funcs)} functions ({', '.join(traced_funcs)})"
            )
        if untraced_funcs:
            failed.append(f"Python: missing @traceable on: {', '.join(untraced_funcs)}")

        # Note: run_type='chain' is the default, so we don't require it explicitly

        return passed, failed

    def _check_python_functions(self, content: str) -> tuple[list[str], list[str]]:
        """Check which functions have @traceable decorator."""
        traced, untraced = [], []

        for func_name in self.REQUIRED_FUNCTIONS:
            # Pattern: @traceable followed by def func_name
            # Allow for @traceable(...) with arguments
            pattern = rf"@traceable[^@]*def\s+{func_name}\s*\("
            if re.search(pattern, content, re.DOTALL):
                traced.append(func_name)
            else:
                # Check if function exists but isn't traced
                if re.search(rf"def\s+{func_name}\s*\(", content):
                    untraced.append(func_name)

        return traced, untraced

    def _validate_typescript(self, path: Path) -> tuple[list[str], list[str]]:
        """Validate TypeScript tracing patterns."""
        passed, failed = [], []
        content = path.read_text()

        # Check imports
        if self.TS_IMPORT_TRACEABLE.search(content):
            passed.append("TypeScript: imports traceable")
        else:
            failed.append("TypeScript: missing 'import { traceable } from \"langsmith/traceable\"'")

        if self.TS_IMPORT_WRAP.search(content):
            passed.append("TypeScript: imports wrapOpenAI")
        else:
            failed.append("TypeScript: missing 'import { wrapOpenAI } from \"langsmith/wrappers\"'")

        # Check client wrapping
        if self.TS_WRAP_CLIENT.search(content):
            passed.append("TypeScript: wraps OpenAI client")
        else:
            failed.append("TypeScript: missing 'wrapOpenAI(new OpenAI())'")

        # Check each function is wrapped with traceable
        traced_funcs, untraced_funcs = self._check_typescript_functions(content)
        if traced_funcs:
            passed.append(
                f"TypeScript: traced {len(traced_funcs)} functions ({', '.join(traced_funcs)})"
            )
        if untraced_funcs:
            failed.append(f"TypeScript: missing traceable() on: {', '.join(untraced_funcs)}")

        # Note: runType: 'chain' is the default, so we don't require it explicitly

        return passed, failed

    def _check_typescript_functions(self, content: str) -> tuple[list[str], list[str]]:
        """Check which functions are wrapped with traceable()."""
        traced, untraced = [], []

        for func_name in self.REQUIRED_FUNCTIONS:
            # Convert snake_case to camelCase for TypeScript
            camel_name = self._to_camel_case(func_name)

            # Pattern 1: const funcName = traceable(async (...
            # Pattern 2: const funcName = traceable((...
            # Pattern 3: name in traceable options: { name: "func_name" }
            patterns = [
                rf"const\s+{camel_name}\s*=\s*traceable\s*\(",
                rf"const\s+{func_name}\s*=\s*traceable\s*\(",
                rf'name\s*:\s*["\']{func_name}["\']',
                rf'name\s*:\s*["\']{camel_name}["\']',
            ]

            found = any(re.search(p, content) for p in patterns)
            if found:
                traced.append(func_name)
            else:
                # Check if function exists but isn't traced
                func_patterns = [
                    rf"(const|let|function)\s+{camel_name}\s*[=\(]",
                    rf"(const|let|function)\s+{func_name}\s*[=\(]",
                    rf"async\s+function\s+{camel_name}\s*\(",
                    rf"async\s+function\s+{func_name}\s*\(",
                ]
                if any(re.search(p, content) for p in func_patterns):
                    untraced.append(func_name)

        return traced, untraced

    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])


class LanguageSyntaxValidator(Validator):
    """Validate that each file uses correct language syntax (no mixing)."""

    # Python-only patterns (shouldn't appear in TypeScript)
    PY_ONLY_PATTERNS = [
        re.compile(r"^def\s+\w+\s*\(", re.MULTILINE),  # def function(
        re.compile(r"^@\w+"),  # @decorator
    ]

    # TypeScript-only patterns (shouldn't appear in Python)
    TS_ONLY_PATTERNS = [
        re.compile(r":\s*(string|number|boolean|Promise<)"),  # Type annotations
        re.compile(r"^(const|let)\s+\w+\s*=", re.MULTILINE),  # const/let declarations
        re.compile(r"async\s+\([^)]*\)\s*=>"),  # async arrow function
    ]

    def __init__(
        self,
        python_file: str = "backend/support_bot.py",
        typescript_file: str = "frontend/support_bot.ts",
    ):
        self.python_file = python_file
        self.typescript_file = typescript_file

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Check Python file doesn't have TypeScript patterns
        py_path = test_dir / self.python_file
        if py_path.exists():
            content = py_path.read_text()
            ts_found = [p.pattern for p in self.TS_ONLY_PATTERNS if p.search(content)]
            if ts_found:
                failed.append(f"Python: contains TypeScript syntax ({len(ts_found)} patterns)")
            else:
                passed.append("Python: correct syntax")

        # Check TypeScript file doesn't have Python patterns
        ts_path = test_dir / self.typescript_file
        if ts_path.exists():
            content = ts_path.read_text()
            py_found = [p.pattern for p in self.PY_ONLY_PATTERNS if p.search(content)]
            if py_found:
                failed.append(f"TypeScript: contains Python syntax ({len(py_found)} patterns)")
            else:
                passed.append("TypeScript: correct syntax")

        return passed, failed


class CodeExecutionValidator(Validator):
    """Validate that traced code runs without errors."""

    def __init__(
        self,
        python_file: str = "backend/support_bot.py",
        typescript_file: str = "frontend/support_bot.ts",
    ):
        self.python_file = python_file
        self.typescript_file = typescript_file

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Python execution - run from test_dir (where Dockerfile is)
        py_path = test_dir / self.python_file
        if py_path.exists():
            success, output = run_python_in_docker(test_dir, self.python_file, timeout=120)
            if success:
                passed.append("Python: executes successfully")
            else:
                error = output[:100] if output else "unknown error"
                failed.append(f"Python: execution failed ({error})")
        else:
            failed.append(f"Python: {self.python_file} not found")

        # TypeScript execution - run from test_dir (where Dockerfile is)
        ts_path = test_dir / self.typescript_file
        if ts_path.exists():
            success, output = run_node_in_docker(test_dir, self.typescript_file, timeout=120)
            if success:
                passed.append("TypeScript: executes successfully")
            else:
                error = output[:100] if output else "unknown error"
                failed.append(f"TypeScript: execution failed ({error})")
        else:
            failed.append(f"TypeScript: {self.typescript_file} not found")

        return passed, failed


class SkillScriptUsageValidator(Validator):
    """Track which skill scripts Claude used (Python vs TypeScript).

    This validator doesn't fail - it just records usage patterns for analysis.
    Key insight: Did Claude use the correct language script for each task?
    - When working on Python agent: should use .py scripts
    - When working on TypeScript agent: should use .ts scripts
    """

    # Known skill scripts by language
    PY_SCRIPTS = [
        "query_traces.py",
        "generate_datasets.py",
        "query_datasets.py",
        "upload_evaluators.py",
    ]
    TS_SCRIPTS = [
        "query_traces.ts",
        "generate_datasets.ts",
        "query_datasets.ts",
        "upload_evaluators.ts",
    ]

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        commands = " ".join(events.get("commands_run", [])).lower()
        files_read = " ".join(events.get("files_read", [])).lower()
        all_activity = commands + " " + files_read

        # Count script usage
        py_used = [s for s in self.PY_SCRIPTS if s.lower() in all_activity]
        ts_used = [s for s in self.TS_SCRIPTS if s.lower() in all_activity]

        # Report findings
        if py_used:
            passed.append(f"Scripts: {len(py_used)} Python scripts used ({', '.join(py_used)})")
        if ts_used:
            passed.append(f"Scripts: {len(ts_used)} TypeScript scripts used ({', '.join(ts_used)})")

        if not py_used and not ts_used:
            passed.append("Scripts: no skill scripts used (Claude wrote from scratch)")

        # Check for language mixing - this is informational, not a failure
        if py_used and ts_used:
            passed.append("Scripts: mixed Python and TypeScript scripts")
        elif py_used and not ts_used:
            passed.append("Scripts: Python-only approach")
        elif ts_used and not py_used:
            passed.append("Scripts: TypeScript-only approach")

        # Store in outputs for later analysis
        if outputs is not None:
            outputs["py_scripts_used"] = py_used
            outputs["ts_scripts_used"] = ts_used

        return passed, failed


class LangSmithTraceValidator(Validator):
    """Validate that tracing worked by checking traces in LangSmith.

    This validator:
    1. Reads trace_id.txt and extracts all UUIDs via regex
    2. Queries LangSmith to verify each trace exists
    3. Checks that traces have proper structure (child runs for traced functions)
    """

    # Regex to match UUIDs (standard format)
    UUID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)

    def __init__(self, trace_id_file: str = "trace_id.txt"):
        self.trace_id_file = trace_id_file

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Read trace ID from file
        trace_file = test_dir / self.trace_id_file
        if not trace_file.exists():
            failed.append(f"LangSmith: {self.trace_id_file} not found")
            return passed, failed

        content = trace_file.read_text().strip()
        if not content:
            failed.append(f"LangSmith: {self.trace_id_file} is empty")
            return passed, failed

        # Extract all UUIDs from the content
        trace_ids = self.UUID_PATTERN.findall(content)
        if not trace_ids:
            failed.append(f"LangSmith: no valid trace IDs found in {self.trace_id_file}")
            return passed, failed

        passed.append(f"LangSmith: found {len(trace_ids)} trace ID(s)")

        # Get LangSmith client
        client, error = _get_langsmith_client()
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

        # Check for expected function names across all traces
        expected_funcs = {
            "classify_intent",
            "extract_entities",
            "lookup_order",
            "generate_response",
            "classifyIntent",
            "extractEntities",
            "lookupOrder",
            "generateResponse",
        }
        found_funcs = [n for n in all_child_names if n in expected_funcs]
        if found_funcs:
            passed.append(f"LangSmith: found traced functions: {', '.join(set(found_funcs))}")

        # Store trace info in outputs
        if outputs is not None:
            outputs["trace_ids"] = trace_ids
            outputs["child_run_names"] = all_child_names

        return passed, failed


# =============================================================================
# EVALUATOR VALIDATORS
# =============================================================================


class LanguageValidator(Validator):
    """Validate that evaluators are written in the correct language for each agent."""

    def __init__(
        self,
        python_evaluators: list[str] = None,  # Accept evaluator.py or evaluators.py
        javascript_evaluators: list[str] = None,  # Accept .js or .ts
    ):
        self.python_evaluators = python_evaluators or ["evaluator.py", "evaluators.py"]
        self.javascript_evaluators = javascript_evaluators or [
            "evaluator.js",
            "evaluator.ts",
            "evaluators.js",
            "evaluators.ts",
        ]

    def _find_py_evaluator(self, test_dir: Path) -> Path | None:
        """Find Python evaluator file."""
        for filename in self.python_evaluators:
            path = test_dir / "backend" / filename
            if path.exists():
                return path
        return None

    def _find_js_evaluator(self, test_dir: Path) -> Path | None:
        """Find JavaScript/TypeScript evaluator file."""
        for filename in self.javascript_evaluators:
            path = test_dir / "frontend" / filename
            if path.exists():
                return path
        return None

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Check Python evaluator exists and is Python
        py_path = self._find_py_evaluator(test_dir)
        if py_path:
            content = py_path.read_text()
            if self._is_python_syntax(content):
                passed.append(f"Python evaluator: correct language ({py_path.name})")
            else:
                failed.append("Python evaluator: contains non-Python syntax")
        else:
            failed.append(
                f"Python evaluator: not found (tried {', '.join(self.python_evaluators)})"
            )

        # Check JavaScript/TypeScript evaluator exists and is JavaScript
        js_path = self._find_js_evaluator(test_dir)
        if js_path:
            content = js_path.read_text()
            if self._is_javascript_syntax(content):
                passed.append(f"JavaScript evaluator: correct language ({js_path.name})")
            else:
                failed.append("JavaScript evaluator: contains non-JavaScript syntax")
        else:
            failed.append(
                f"JavaScript evaluator: not found (tried {', '.join(self.javascript_evaluators)})"
            )

        return passed, failed

    def _is_python_syntax(self, content: str) -> bool:
        """Check if content looks like Python."""
        python_indicators = [
            re.compile(r"^def\s+\w+\s*\(", re.MULTILINE),
            re.compile(r"^import\s+\w+", re.MULTILINE),
            re.compile(r"^from\s+\w+\s+import", re.MULTILINE),
        ]
        return any(p.search(content) for p in python_indicators)

    def _is_javascript_syntax(self, content: str) -> bool:
        """Check if content looks like JavaScript."""
        js_indicators = [
            re.compile(r"function\s+\w+\s*\("),
            re.compile(r"const\s+\w+\s*="),
            re.compile(r"=>\s*\{"),
            re.compile(r"module\.exports"),
            re.compile(r"export\s+(default\s+)?function"),
        ]
        return any(p.search(content) for p in js_indicators)


class PatternValidator(Validator):
    """Validate that evaluators follow the correct LangSmith patterns."""

    # Python evaluator patterns - allow optional type annotations
    # Matches: def func(run, example) OR def func(run: Run, example: Example)
    PY_FUNC_SIGNATURE = re.compile(
        r"def\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)"
    )
    PY_RETURN_SCORE = re.compile(r"return\s*\{[^}]*['\"]?\w+['\"]?\s*:")

    # JavaScript evaluator patterns - allow optional type annotations
    # Matches: function func(run, example) OR function func(run: Run, example: Example)
    JS_FUNC_SIGNATURE = re.compile(
        r"function\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)"
    )
    JS_ARROW_SIGNATURE = re.compile(
        r"=\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)\s*=>"
    )
    JS_RETURN_SCORE = re.compile(r"return\s*\{[^}]*\w+\s*:")

    def __init__(
        self,
        python_evaluators: list[str] = None,
        javascript_evaluators: list[str] = None,
    ):
        self.python_evaluators = python_evaluators or ["evaluator.py", "evaluators.py"]
        self.javascript_evaluators = javascript_evaluators or [
            "evaluator.js",
            "evaluator.ts",
            "evaluators.js",
            "evaluators.ts",
        ]

    def _find_py_evaluator(self, test_dir: Path) -> Path | None:
        """Find Python evaluator file."""
        for filename in self.python_evaluators:
            path = test_dir / "backend" / filename
            if path.exists():
                return path
        return None

    def _find_js_evaluator(self, test_dir: Path) -> Path | None:
        """Find JavaScript/TypeScript evaluator file."""
        for filename in self.javascript_evaluators:
            path = test_dir / "frontend" / filename
            if path.exists():
                return path
        return None

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Validate Python evaluator patterns
        py_path = self._find_py_evaluator(test_dir)
        if py_path:
            content = py_path.read_text()
            py_passed, py_failed = self._validate_python_patterns(content)
            passed.extend(py_passed)
            failed.extend(py_failed)

        # Validate JavaScript/TypeScript evaluator patterns
        js_path = self._find_js_evaluator(test_dir)
        if js_path:
            content = js_path.read_text()
            js_passed, js_failed = self._validate_javascript_patterns(content)
            passed.extend(js_passed)
            failed.extend(js_failed)

        return passed, failed

    def _validate_python_patterns(self, content: str) -> tuple[list[str], list[str]]:
        """Validate Python evaluator patterns."""
        passed, failed = [], []

        # Check function signature
        if self.PY_FUNC_SIGNATURE.search(content):
            passed.append("Python: has (run, example) signature")
        else:
            failed.append("Python: missing (run, example) function signature")

        # Check return format
        if self.PY_RETURN_SCORE.search(content):
            passed.append("Python: returns dict with score")
        else:
            failed.append("Python: missing return dict with score")

        # Check for run outputs access (dict or attribute)
        if 'run["outputs"]' in content or "run['outputs']" in content or "run.outputs" in content:
            passed.append("Python: accesses run outputs")
        else:
            failed.append("Python: missing run outputs access")

        # Check for example outputs access (dict or attribute)
        if (
            'example["outputs"]' in content
            or "example['outputs']" in content
            or "example.outputs" in content
        ):
            passed.append("Python: accesses example outputs")
        else:
            failed.append("Python: missing example outputs access")

        return passed, failed

    def _validate_javascript_patterns(self, content: str) -> tuple[list[str], list[str]]:
        """Validate JavaScript evaluator patterns."""
        passed, failed = [], []

        # Check function signature (regular or arrow)
        if self.JS_FUNC_SIGNATURE.search(content) or self.JS_ARROW_SIGNATURE.search(content):
            passed.append("JavaScript: has (run, example) signature")
        else:
            failed.append("JavaScript: missing (run, example) function signature")

        # Check return format
        if self.JS_RETURN_SCORE.search(content):
            passed.append("JavaScript: returns object with score")
        else:
            failed.append("JavaScript: missing return object with score")

        # Check for run.outputs access
        if "run.outputs" in content:
            passed.append("JavaScript: accesses run.outputs")
        else:
            failed.append("JavaScript: missing run.outputs access")

        # Check for example.outputs access
        if "example.outputs" in content:
            passed.append("JavaScript: accesses example.outputs")
        else:
            failed.append("JavaScript: missing example.outputs access")

        return passed, failed


class SyntaxValidator(Validator):
    """Validate that evaluator code has valid syntax."""

    def __init__(
        self,
        python_evaluators: list[str] = None,
        javascript_evaluators: list[str] = None,
    ):
        self.python_evaluators = python_evaluators or ["evaluator.py", "evaluators.py"]
        self.javascript_evaluators = javascript_evaluators or [
            "evaluator.js",
            "evaluator.ts",
            "evaluators.js",
            "evaluators.ts",
        ]

    def _find_py_evaluator(self, test_dir: Path) -> Path | None:
        """Find Python evaluator file."""
        for filename in self.python_evaluators:
            path = test_dir / "backend" / filename
            if path.exists():
                return path
        return None

    def _find_js_evaluator(self, test_dir: Path) -> Path | None:
        """Find JavaScript/TypeScript evaluator file."""
        for filename in self.javascript_evaluators:
            path = test_dir / "frontend" / filename
            if path.exists():
                return path
        return None

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Validate Python syntax
        py_path = self._find_py_evaluator(test_dir)
        if py_path:
            content = py_path.read_text()
            try:
                import ast

                ast.parse(content)
                passed.append("Python: valid syntax")
            except SyntaxError as e:
                failed.append(f"Python: syntax error at line {e.lineno}: {e.msg}")

        # Validate JavaScript/TypeScript syntax (basic check)
        js_path = self._find_js_evaluator(test_dir)
        if js_path:
            content = js_path.read_text()
            if self._basic_js_syntax_check(content):
                passed.append(f"JavaScript: valid syntax ({js_path.name})")
            else:
                failed.append("JavaScript: syntax appears invalid")

        return passed, failed

    def _basic_js_syntax_check(self, content: str) -> bool:
        """Basic JavaScript syntax validation."""
        # Check balanced braces
        if content.count("{") != content.count("}"):
            return False
        if content.count("(") != content.count(")"):
            return False
        if content.count("[") != content.count("]"):
            return False

        # Check for common syntax elements
        has_function = "function" in content or "=>" in content
        has_return = "return" in content

        return has_function and has_return


class DatasetValidator(Validator):
    """Validate evaluator logic using real datasets from traced agent runs.

    Uses the datasets generated from actual LangSmith traces:
    - SQL agent: sql_agent_trajectory_dataset.json (trajectory matching)
    - Support bot: support_bot_final_response_dataset.json (response matching)

    This validator tests that Claude's evaluators produce sensible scores when run
    against real data, not just synthetic test cases.
    """

    def __init__(
        self,
        python_evaluators: list[str] = None,
        javascript_evaluators: list[str] = None,
        py_dataset: str = "sql_agent_trajectory_dataset.json",
        ts_dataset: str = "support_bot_final_response_dataset.json",
    ):
        self.python_evaluators = python_evaluators or ["evaluator.py", "evaluators.py"]
        self.javascript_evaluators = javascript_evaluators or [
            "evaluator.js",
            "evaluator.ts",
            "evaluators.js",
            "evaluators.ts",
        ]
        self.py_dataset = py_dataset
        self.ts_dataset = ts_dataset

    def _find_py_evaluator(self, test_dir: Path) -> Path | None:
        for filename in self.python_evaluators:
            path = test_dir / "backend" / filename
            if path.exists():
                return path
        return None

    def _find_js_evaluator(self, test_dir: Path) -> Path | None:
        for filename in self.javascript_evaluators:
            path = test_dir / "frontend" / filename
            if path.exists():
                return path
        return None

    def _find_evaluator_function(self, content: str, language: str) -> tuple[str, str]:
        """Find evaluator function name via pattern matching."""
        if language == "python":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        args = [a.arg for a in node.args.args]
                        if "run" in args and "example" in args:
                            return node.name, None
                return None, "no (run, example) function found"
            except SyntaxError as e:
                return None, f"syntax error line {e.lineno}"
        else:
            # JavaScript - use regex
            func_match = re.search(r"function\s+(\w+)\s*\(\s*run", content)
            if func_match:
                return func_match.group(1), None
            func_match = re.search(r"const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*run", content)
            if func_match:
                return func_match.group(1), None
            return None, "no (run, example) function found"

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        # Test Python evaluator against real trajectory dataset
        py_path = self._find_py_evaluator(test_dir)
        if py_path:
            py_passed, py_failed = self._test_python_evaluator(py_path, test_dir)
            passed.extend(py_passed)
            failed.extend(py_failed)

        # Test JavaScript evaluator against real final_response dataset
        js_path = self._find_js_evaluator(test_dir)
        if js_path:
            js_passed, js_failed = self._test_js_evaluator(js_path, test_dir)
            passed.extend(js_passed)
            failed.extend(js_failed)

        return passed, failed

    def _test_python_evaluator(self, path: Path, test_dir: Path) -> tuple[list[str], list[str]]:
        """Test Python evaluator against real trajectory dataset."""
        content = path.read_text()
        func_name, error = self._find_evaluator_function(content, "python")
        if error:
            return [], [f"Python (trajectory): {error}"]

        # Load real dataset
        dataset_path = DATA_DIR / self.py_dataset
        if not dataset_path.exists():
            return ["Python (trajectory): dataset not found"], []

        dataset = json.loads(dataset_path.read_text())

        # Create test cases from real dataset
        # For trajectory: comparing run.outputs.expected_trajectory with example.outputs.expected_trajectory
        test_cases = []
        for i, example in enumerate(dataset):
            # Test 1: Exact match (run = example)
            test_cases.append(
                {
                    "name": f"exact_match_{i}",
                    "run": {"inputs": example["inputs"], "outputs": example["outputs"]},
                    "example": {"inputs": example["inputs"], "outputs": example["outputs"]},
                    "expected_result": {"should_pass": True, "min_score": 0.9},
                }
            )

            # Test 2: Empty trajectory (should be low score)
            test_cases.append(
                {
                    "name": f"empty_trajectory_{i}",
                    "run": {"inputs": example["inputs"], "outputs": {"expected_trajectory": []}},
                    "example": {"inputs": example["inputs"], "outputs": example["outputs"]},
                    "expected_result": {"should_pass": True, "max_score": 0.5},
                }
            )

        # Write test cases to root (test_dir)
        test_cases_path = test_dir / "_be_test_cases.json"
        test_cases_path.write_text(json.dumps(test_cases, indent=2))

        # Copy eval_runner.py to root
        runner_src = VALIDATION_DIR / "eval_runner.py"
        runner_dst = test_dir / "_eval_runner.py"
        runner_dst.write_text(runner_src.read_text())

        try:
            # Use backend.evaluator as module path
            module_name = f"backend.{path.name.replace('.py', '')}"
            args = [module_name, func_name, "_be_test_cases.json"]
            success, output = run_python_in_docker(
                test_dir, "_eval_runner.py", timeout=60, args=args
            )
            return self._parse_results(output, success, "Python (trajectory)")
        except Exception as e:
            return [], [f"Python (trajectory): {str(e)[:50]}"]
        finally:
            runner_dst.unlink(missing_ok=True)
            test_cases_path.unlink(missing_ok=True)

    def _test_js_evaluator(self, path: Path, test_dir: Path) -> tuple[list[str], list[str]]:
        """Test JavaScript/TypeScript evaluator against real final_response dataset."""
        content = path.read_text()
        func_name, error = self._find_evaluator_function(content, "javascript")
        if error:
            return [], [f"JavaScript (final_response): {error}"]

        # Load real dataset
        dataset_path = DATA_DIR / self.ts_dataset
        if not dataset_path.exists():
            return ["JavaScript (final_response): dataset not found"], []

        dataset = json.loads(dataset_path.read_text())

        # Create test cases from real dataset
        test_cases = []
        for i, example in enumerate(dataset):
            # Test 1: Exact match
            test_cases.append(
                {
                    "name": f"exact_match_{i}",
                    "run": {"inputs": example["inputs"], "outputs": example["outputs"]},
                    "example": {"inputs": example["inputs"], "outputs": example["outputs"]},
                    "expected_result": {"should_pass": True, "min_score": 0.9},
                }
            )

            # Test 2: Empty response (should be low score)
            test_cases.append(
                {
                    "name": f"empty_response_{i}",
                    "run": {"inputs": example["inputs"], "outputs": {"response": ""}},
                    "example": {"inputs": example["inputs"], "outputs": example["outputs"]},
                    "expected_result": {"should_pass": True, "max_score": 0.3},
                }
            )

        # Write test cases to root
        test_cases_path = test_dir / "_fe_test_cases.json"
        test_cases_path.write_text(json.dumps(test_cases, indent=2))

        # Copy eval_runner.ts to root
        runner_src = VALIDATION_DIR / "eval_runner.ts"
        runner_dst = test_dir / "_eval_runner.ts"
        runner_dst.write_text(runner_src.read_text())

        try:
            # Module path relative to workspace root
            module_path = f"./frontend/{path.name}"
            args = [module_path, func_name, "_fe_test_cases.json"]
            success, output = run_node_in_docker(test_dir, "_eval_runner.ts", timeout=60, args=args)
            return self._parse_results(output, success, "JavaScript (final_response)")
        except Exception as e:
            return [], [f"JavaScript (final_response): {str(e)[:50]}"]
        finally:
            runner_dst.unlink(missing_ok=True)
            test_cases_path.unlink(missing_ok=True)

    def _parse_results(self, output: str, success: bool, lang: str) -> tuple[list[str], list[str]]:
        """Parse EVALUATOR_RESULTS from output."""
        for line in output.split("\n"):
            if line.startswith("EVALUATOR_RESULTS:"):
                try:
                    results = json.loads(line.replace("EVALUATOR_RESULTS:", ""))
                    passed_count = sum(1 for r in results if r.get("passed"))
                    total = len(results)
                    msg = f"{lang}: {passed_count}/{total} tests"
                    if passed_count == total:
                        return [msg + " passed"], []
                    elif passed_count > total // 2:
                        return [msg + " (partial)"], []
                    else:
                        return [], [msg + " passed"]
                except json.JSONDecodeError:
                    pass

        if success:
            return [f"{lang}: executed"], []
        else:
            error_preview = output[:150].replace("\n", " ") if output else "no output"
            return [], [f"{lang}: execution failed - {error_preview}"]


class UploadValidator(Validator):
    """Validate evaluators were uploaded to LangSmith via /runs/rules API."""

    def __init__(self, upload_prefixes: list[str] = None):
        self.upload_prefixes = upload_prefixes or ["test-be-", "test-fe-"]

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        client, error = _get_langsmith_client()
        if not client:
            return [f"Upload: skipped ({error})"], []

        run_id = (outputs or {}).get("run_id")
        if not run_id:
            return ["Upload: skipped (no run_id)"], []

        try:
            response = client.session.get(
                f"{client.api_url}/runs/rules",
                headers={"x-api-key": client.api_key},
                params={"limit": 100},
            )
            if response.status_code != 200:
                return [f"Upload: skipped (API {response.status_code})"], []

            data = response.json()
            rules = data if isinstance(data, list) else data.get("rules", [])

            # Search for any evaluator containing the run_id
            matching = [r for r in rules if run_id in r.get("display_name", "")]

            if not matching:
                return [], [f"Upload: no evaluator with run_id '{run_id}' found"]

            names = ", ".join(r.get("display_name", "") for r in matching)[:80]
            return [f"Upload: found {len(matching)} evaluator(s): {names}"], []

        except Exception as e:
            return [], [f"Upload: API error: {str(e)[:100]}"]
