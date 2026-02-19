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


def run_tests(module_path: str) -> dict:
    """Run tests against the module.

    Returns dict with test results.
    """
    results = {"passed": [], "failed": [], "error": None}

    try:
        with open(module_path) as f:
            source = f.read()
    except Exception as e:
        results["error"] = f"Failed to read file: {e}"
        return results

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        results["error"] = f"Syntax error in file: {e}"
        return results

    # ========== lc_tools bugs (LangChain-specific) ==========

    # Test 1: Tools must have docstrings (LangChain uses docstring as tool description)
    try:
        tools_without_docstrings = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has @tool decorator
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
            results["passed"].append("tool_has_docstring")
        else:
            results["failed"].append(
                f"tool_has_docstring: tools {tools_without_docstrings} missing docstrings - "
                "LangChain uses docstring as tool description for the model"
            )
    except Exception as e:
        results["failed"].append(f"tool_has_docstring: {e}")

    # Test 2: Tool parameters must have type hints (LangChain generates schema from types)
    try:
        tools_without_types = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has @tool decorator
                for decorator in node.decorator_list:
                    decorator_name = None
                    if isinstance(decorator, ast.Name):
                        decorator_name = decorator.id
                    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                        decorator_name = decorator.func.id

                    if decorator_name == "tool":
                        # Check all non-self/cls arguments have type annotations
                        for arg in node.args.args:
                            if arg.arg not in ("self", "cls") and arg.annotation is None:
                                tools_without_types.append(f"{node.name}.{arg.arg}")

        if not tools_without_types:
            results["passed"].append("tool_has_types")
        else:
            results["failed"].append(
                f"tool_has_types: parameters {tools_without_types} missing type hints - "
                "LangChain generates tool schema from type annotations"
            )
    except Exception as e:
        results["failed"].append(f"tool_has_types: {e}")

    # ========== lc_streaming bugs (LangChain-specific) ==========

    # Test 3: Tuple unpacking in messages mode (LangChain streaming API)
    try:
        tuple_unpack_patterns = [
            r"token\s*,\s*_?metadata\s*=\s*chunk",  # token, metadata or token, _metadata
            r"msg\s*,\s*_?meta\s*=\s*chunk",
            r"message\s*,\s*_?metadata\s*=\s*chunk",
            r"content\s*,\s*_\s*=\s*chunk",
            r"token\s*,\s*_\s*=\s*chunk",
            r"chunk\s*\[\s*0\s*\]",
            r"\w+\s*,\s*_\w*\s*=\s*chunk",  # Generic: var, _ or var, _var = chunk
        ]

        has_tuple_unpack = any(re.search(pattern, source) for pattern in tuple_unpack_patterns)

        if has_tuple_unpack:
            results["passed"].append("tuple_unpacking")
        else:
            results["failed"].append(
                "tuple_unpacking: messages mode returns (token, metadata) tuple - "
                "unpack before accessing content"
            )
    except Exception as e:
        results["failed"].append(f"tuple_unpacking: {e}")

    # Test 4: Async stream in async context (LangChain astream API)
    try:
        async_func_source = extract_async_functions(source)

        if async_func_source:
            uses_astream = re.search(r"\.astream\(", async_func_source)
            uses_sync_stream = re.search(r"(?<!a)\.stream\(", async_func_source)

            if uses_astream and not uses_sync_stream:
                results["passed"].append("async_uses_astream")
            elif uses_astream:
                results["passed"].append("async_uses_astream")
            else:
                results["failed"].append(
                    "async_uses_astream: async functions should use astream() - "
                    "sync streams block the event loop"
                )
        else:
            results["passed"].append("async_uses_astream")
    except Exception as e:
        results["failed"].append(f"async_uses_astream: {e}")

    # Test 5: Mode checking in multi-mode streaming (LangChain multi-mode API)
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
                results["passed"].append("mode_checking")
            else:
                results["failed"].append(
                    "mode_checking: multi-mode streaming needs mode-specific handling"
                )
        else:
            results["passed"].append("mode_checking")
    except Exception as e:
        results["failed"].append(f"mode_checking: {e}")

    return results


def extract_async_functions(source: str) -> str:
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
