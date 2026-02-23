"""Pattern-based tests for chat application fixes.

Tests LangChain-specific bugs from multiple skills:

From lc_streaming:
1. Tuple unpacking - messages mode returns (token, metadata) tuple
2. Mode checking - multi-mode streaming needs mode-specific handling
3. Async uses astream - async functions should use .astream() not .stream()

From lc_tools:
4. Missing docstrings - tools without docstrings have no description for model
5. Missing type hints - tool parameters without types have poor schema

These are NOT basic Python bugs - they require understanding LangChain APIs.
"""

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestContext:
    """Shared context for test execution."""

    module_path: str
    source: str = ""
    tree: Any | None = None
    results: dict = field(default_factory=lambda: {"passed": [], "failed": [], "error": None})

    def load(self) -> bool:
        """Load source and parse AST. Returns True if successful."""
        try:
            with open(self.module_path) as f:
                self.source = f.read()
        except Exception as e:
            self.results["error"] = f"Failed to read file: {e}"
            return False

        try:
            self.tree = ast.parse(self.source)
        except SyntaxError as e:
            self.results["error"] = f"Syntax error in file: {e}"
            return False

        return True

    def pass_test(self, name: str):
        """Mark a test as passed."""
        self.results["passed"].append(name)

    def fail_test(self, name: str, reason: str):
        """Mark a test as failed with reason."""
        self.results["failed"].append(f"{name}: {reason}")


# =============================================================================
# Test 1: Tool Docstrings (lc_tools)
# =============================================================================


def test_tool_docstrings(ctx: TestContext):
    """Check that @tool decorated functions have docstrings.

    LangChain uses the docstring as the tool description for the model.
    Without a docstring, the model has no idea what the tool does.
    """
    TEST_NAME = "tool_has_docstring"

    try:
        tools_without_docstrings = []
        for node in ast.walk(ctx.tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    decorator_name = None
                    if isinstance(decorator, ast.Name):
                        decorator_name = decorator.id
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorator_name = decorator.func.id

                    if decorator_name == "tool":
                        docstring = ast.get_docstring(node)
                        if not docstring or len(docstring.strip()) < 10:
                            tools_without_docstrings.append(node.name)

        if not tools_without_docstrings:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"tools {tools_without_docstrings} missing docstrings - "
                "LangChain uses docstring as tool description for the model",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 2: Tool Type Hints (lc_tools)
# =============================================================================


def test_tool_type_hints(ctx: TestContext):
    """Check that @tool decorated functions have type hints on parameters.

    LangChain generates the tool schema from type annotations.
    Without types, the schema is incomplete and the model may misuse the tool.
    """
    TEST_NAME = "tool_has_types"

    try:
        tools_without_types = []
        for node in ast.walk(ctx.tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    decorator_name = None
                    if isinstance(decorator, ast.Name):
                        decorator_name = decorator.id
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorator_name = decorator.func.id

                    if decorator_name == "tool":
                        for arg in node.args.args:
                            if arg.arg not in ("self", "cls") and arg.annotation is None:
                                tools_without_types.append(f"{node.name}.{arg.arg}")

        if not tools_without_types:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                f"parameters {tools_without_types} missing type hints - "
                "LangChain generates tool schema from type annotations",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 3: Tuple Unpacking (lc_streaming)
# =============================================================================


def test_tuple_unpacking(ctx: TestContext):
    """Check that messages mode streaming unpacks the (token, metadata) tuple.

    In messages mode, LangChain returns a tuple, not just the token.
    Code must unpack: `token, metadata = chunk` or use `chunk[0]`.
    """
    TEST_NAME = "tuple_unpacking"

    try:
        tuple_unpack_patterns = [
            r"token\s*,\s*_?metadata\s*=\s*chunk",
            r"msg\s*,\s*_?meta\s*=\s*chunk",
            r"message\s*,\s*_?metadata\s*=\s*chunk",
            r"content\s*,\s*_\s*=\s*chunk",
            r"token\s*,\s*_\s*=\s*chunk",
            r"chunk\s*\[\s*0\s*\]",
            r"\w+\s*,\s*_\w*\s*=\s*chunk",
        ]

        has_tuple_unpack = any(re.search(pattern, ctx.source) for pattern in tuple_unpack_patterns)

        if has_tuple_unpack:
            ctx.pass_test(TEST_NAME)
        else:
            ctx.fail_test(
                TEST_NAME,
                "messages mode returns (token, metadata) tuple - unpack before accessing content",
            )
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Test 4: Async Uses astream (lc_streaming)
# =============================================================================


def test_async_uses_astream(ctx: TestContext):
    """Check that async functions use .astream() not .stream().

    Using sync .stream() in an async function blocks the event loop.
    Always use .astream() in async contexts.
    """
    TEST_NAME = "async_uses_astream"

    try:
        async_func_source = _extract_async_functions(ctx.source)

        if async_func_source:
            uses_astream = re.search(r"\.astream\(", async_func_source)
            uses_sync_stream = re.search(r"(?<!a)\.stream\(", async_func_source)

            if uses_astream and not uses_sync_stream:
                ctx.pass_test(TEST_NAME)
            elif uses_astream:
                ctx.pass_test(TEST_NAME)
            else:
                ctx.fail_test(
                    TEST_NAME,
                    "async functions should use astream() - sync streams block the event loop",
                )
        else:
            ctx.pass_test(TEST_NAME)
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


def _extract_async_functions(source: str) -> str:
    """Extract source code of all async functions."""
    tree = ast.parse(source)
    async_sources = []

    lines = source.split("\n")
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            start_line = node.lineno - 1
            end_line = node.end_lineno
            async_sources.append("\n".join(lines[start_line:end_line]))

    return "\n\n".join(async_sources)


# =============================================================================
# Test 5: Mode Checking (lc_streaming)
# =============================================================================


def test_mode_checking(ctx: TestContext):
    """Check that multi-mode streaming has mode-specific handling.

    When using stream_mode=[...] with multiple modes, each chunk includes
    a mode indicator. Code must check the mode before processing.
    """
    TEST_NAME = "mode_checking"

    try:
        multimode_pattern = r"stream_mode\s*=\s*\[.*,.*\]"
        has_multimode = re.search(multimode_pattern, ctx.source)

        if has_multimode:
            mode_check_patterns = [
                r'if\s+mode\s*==\s*["\']messages["\']',
                r'if\s+mode\s*==\s*["\']updates["\']',
                r'elif\s+mode\s*==\s*["\']',
                r"match\s+mode",
            ]
            has_mode_check = any(re.search(pattern, ctx.source) for pattern in mode_check_patterns)

            if has_mode_check:
                ctx.pass_test(TEST_NAME)
            else:
                ctx.fail_test(TEST_NAME, "multi-mode streaming needs mode-specific handling")
        else:
            ctx.pass_test(TEST_NAME)
    except Exception as e:
        ctx.fail_test(TEST_NAME, str(e))


# =============================================================================
# Main Test Runner
# =============================================================================


def run_tests(module_path: str) -> dict:
    """Run all tests against the module.

    Returns dict with test results: {passed: [], failed: [], error: str|None}
    """
    ctx = TestContext(module_path=module_path)

    if not ctx.load():
        return ctx.results

    # Run each test
    tests = [
        test_tool_docstrings,
        test_tool_type_hints,
        test_tuple_unpacking,
        test_async_uses_astream,
        test_mode_checking,
    ]

    for test_fn in tests:
        try:
            test_fn(ctx)
        except Exception as e:
            test_name = test_fn.__name__.replace("test_", "")
            ctx.fail_test(test_name, str(e))

    return ctx.results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_streaming.py <path_to_chat_app.py>")
        sys.exit(1)

    module_path = sys.argv[1]
    results = run_tests(module_path)

    print(json.dumps(results, indent=2))

    if results["error"] or results["failed"]:
        sys.exit(1)
    sys.exit(0)
