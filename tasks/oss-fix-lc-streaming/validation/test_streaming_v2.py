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
import re

from scaffold.python.validation.runner import TestRunner


def _require_source_and_tree(runner):
    """Load source and parse AST. Returns (source, tree) or (None, None)."""
    source = runner.read(runner.artifacts[0])
    if not source:
        runner.failed(f"Failed to read file: {runner.artifacts[0]}")
        return None, None

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        runner.failed(f"Syntax error in file: {e}")
        return None, None

    return source, tree


# =============================================================================
# Check 1: Tool Docstrings (lc_tools)
# =============================================================================


def check_tool_has_docstring(runner):
    """Check that @tool decorated functions have docstrings.

    LangChain uses the docstring as the tool description for the model.
    Without a docstring, the model has no idea what the tool does.
    """
    source, tree = _require_source_and_tree(runner)
    if source is None:
        return

    try:
        tools_without_docstrings = []
        for node in ast.walk(tree):
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
            runner.passed("tool_has_docstring")
        else:
            runner.failed(
                f"tool_has_docstring: "
                f"tools {tools_without_docstrings} missing docstrings - "
                "LangChain uses docstring as tool description for the model"
            )
    except Exception as e:
        runner.failed(f"tool_has_docstring: {e}")


# =============================================================================
# Check 2: Tool Type Hints (lc_tools)
# =============================================================================


def check_tool_has_types(runner):
    """Check that @tool decorated functions have type hints on parameters.

    LangChain generates the tool schema from type annotations.
    Without types, the schema is incomplete and the model may misuse the tool.
    """
    source, tree = _require_source_and_tree(runner)
    if source is None:
        return

    try:
        tools_without_types = []
        for node in ast.walk(tree):
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
            runner.passed("tool_has_types")
        else:
            runner.failed(
                f"tool_has_types: "
                f"parameters {tools_without_types} missing type hints - "
                "LangChain generates tool schema from type annotations"
            )
    except Exception as e:
        runner.failed(f"tool_has_types: {e}")


# =============================================================================
# Check 3: Tuple Unpacking (lc_streaming)
# =============================================================================


def check_tuple_unpacking(runner):
    """Check that messages mode streaming unpacks the (token, metadata) tuple.

    In messages mode, LangChain returns a tuple, not just the token.
    Code must unpack: `token, metadata = chunk` or use `chunk[0]`.
    """
    source, tree = _require_source_and_tree(runner)
    if source is None:
        return

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

        has_tuple_unpack = any(re.search(pattern, source) for pattern in tuple_unpack_patterns)

        if has_tuple_unpack:
            runner.passed("tuple_unpacking")
        else:
            runner.failed(
                "tuple_unpacking: "
                "messages mode returns (token, metadata) tuple - unpack before accessing content"
            )
    except Exception as e:
        runner.failed(f"tuple_unpacking: {e}")


# =============================================================================
# Check 4: Async Uses astream (lc_streaming)
# =============================================================================


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


def check_async_uses_astream(runner):
    """Check that async functions use .astream() not .stream().

    Using sync .stream() in an async function blocks the event loop.
    Always use .astream() in async contexts.
    """
    source, tree = _require_source_and_tree(runner)
    if source is None:
        return

    try:
        async_func_source = _extract_async_functions(source)

        if async_func_source:
            uses_astream = re.search(r"\.astream\(", async_func_source)
            uses_sync_stream = re.search(r"(?<!a)\.stream\(", async_func_source)

            if uses_astream and not uses_sync_stream:
                runner.passed("async_uses_astream")
            elif uses_astream:
                runner.passed("async_uses_astream")
            else:
                runner.failed(
                    "async_uses_astream: "
                    "async functions should use astream() - sync streams block the event loop"
                )
        else:
            runner.passed("async_uses_astream")
    except Exception as e:
        runner.failed(f"async_uses_astream: {e}")


# =============================================================================
# Check 5: Mode Checking (lc_streaming)
# =============================================================================


def check_mode_checking(runner):
    """Check that multi-mode streaming has mode-specific handling.

    When using stream_mode=[...] with multiple modes, each chunk includes
    a mode indicator. Code must check the mode before processing.
    """
    source, tree = _require_source_and_tree(runner)
    if source is None:
        return

    try:
        multimode_pattern = r"stream_mode\s*=\s*\[.*,.*\]"
        has_multimode = re.search(multimode_pattern, source)

        if has_multimode:
            mode_check_patterns = [
                r'if\s+mode\s*==\s*["\']messages["\']',
                r'if\s+mode\s*==\s*["\']updates["\']',
                r'elif\s+mode\s*==\s*["\']',
                r"match\s+mode",
            ]
            has_mode_check = any(re.search(pattern, source) for pattern in mode_check_patterns)

            if has_mode_check:
                runner.passed("mode_checking")
            else:
                runner.failed("mode_checking: multi-mode streaming needs mode-specific handling")
        else:
            runner.passed("mode_checking")
    except Exception as e:
        runner.failed(f"mode_checking: {e}")


if __name__ == "__main__":
    TestRunner.run(
        [
            check_tool_has_docstring,
            check_tool_has_types,
            check_tuple_unpacking,
            check_async_uses_astream,
            check_mode_checking,
        ]
    )
