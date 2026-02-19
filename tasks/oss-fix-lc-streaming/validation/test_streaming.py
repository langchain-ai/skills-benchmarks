"""Pattern-based tests for chat application fixes.

The broken code has bugs from multiple skill areas:

From lc_tools/lc_agents:
1. Vague tool descriptions - agent doesn't know when to use tools
2. Non-serializable returns - datetime objects cause serialization errors

From lc_streaming:
3. Tuple unpacking - messages mode returns (token, metadata) tuple
4. Generator exhaustion - caching/reusing exhausted stream
5. Missing flush - tokens buffered instead of real-time display
6. Sync in async - using sync stream in async context

Tests verify correct patterns are present after fixing.
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
        ast.parse(source)
    except SyntaxError as e:
        results["error"] = f"Syntax error in file: {e}"
        return results

    # ========== lc_tools / lc_agents bugs ==========

    # Test 1: Tool descriptions should be specific (not vague)
    # Looking for descriptive docstrings in tool functions
    try:
        tool_pattern = r'@tool\s*\ndef\s+(\w+)[^"\']*?["\'\'\']([^"\']*)["\'\'\']'
        tool_matches = re.findall(tool_pattern, source, re.DOTALL)

        specific_keywords = [
            "search the web",
            "find information",
            "perform mathematical",
            "calculate",
            "compute",
            "current time",
            "retrieve",
            "query",
        ]

        has_good_descriptions = False
        for _name, docstring in tool_matches:
            docstring_lower = docstring.lower()
            # Check if docstring is specific (contains action words)
            if any(keyword in docstring_lower for keyword in specific_keywords):
                has_good_descriptions = True
                break

        if has_good_descriptions:
            results["passed"].append("specific_tool_descriptions")
        else:
            results["failed"].append(
                "specific_tool_descriptions: tool descriptions are too vague - "
                "agent won't know when to use them"
            )
    except Exception as e:
        results["failed"].append(f"specific_tool_descriptions: {e}")

    # Test 2: Tools should return serializable types (not datetime objects)
    try:
        # Check for datetime return type annotations or raw datetime returns
        datetime_return_pattern = r"def\s+\w+\([^)]*\)\s*->\s*datetime"
        returns_datetime_raw = r"return\s+datetime\.now\(\)"

        has_datetime_return = re.search(datetime_return_pattern, source)
        has_raw_datetime = re.search(returns_datetime_raw, source)

        # Check for fixed version: converting datetime to string
        fixed_patterns = [
            r"\.isoformat\(\)",
            r"\.strftime\(",
            r"str\(datetime",
            r"datetime\.now\(\)\.isoformat",
        ]
        has_serializable_fix = any(re.search(pattern, source) for pattern in fixed_patterns)

        if not has_datetime_return and not has_raw_datetime:
            results["passed"].append("serializable_tool_returns")
        elif has_serializable_fix:
            results["passed"].append("serializable_tool_returns")
        else:
            results["failed"].append(
                "serializable_tool_returns: tools returning datetime objects cause "
                "serialization errors - return strings instead (use .isoformat())"
            )
    except Exception as e:
        results["failed"].append(f"serializable_tool_returns: {e}")

    # ========== lc_streaming bugs ==========

    # Test 3: Tuple unpacking in messages mode
    try:
        tuple_unpack_patterns = [
            r"token\s*,\s*metadata\s*=\s*chunk",
            r"msg\s*,\s*meta\s*=\s*chunk",
            r"message\s*,\s*metadata\s*=\s*chunk",
            r"content\s*,\s*_\s*=\s*chunk",
            r"token\s*,\s*_\s*=\s*chunk",
            r"chunk\s*\[\s*0\s*\]",
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

    # Test 4: No generator caching/reuse
    try:
        cached_stream_pattern = r"_stream\s*=|cached.*stream|self\.stream\s*="
        reuses_stream = re.search(cached_stream_pattern, source)

        if not reuses_stream:
            results["passed"].append("no_generator_reuse")
        else:
            results["failed"].append(
                "no_generator_reuse: generators exhausted after iteration - "
                "create new stream for each request"
            )
    except Exception as e:
        results["failed"].append(f"no_generator_reuse: {e}")

    # Test 5: Real-time display with flush
    try:
        flush_pattern = r"print\([^)]*flush\s*=\s*True"
        stdout_flush = r"sys\.stdout\.(write|flush)"

        has_flush = re.search(flush_pattern, source) or re.search(stdout_flush, source)

        if has_flush:
            results["passed"].append("realtime_flush")
        else:
            results["failed"].append(
                "realtime_flush: tokens buffered instead of real-time - use print(..., flush=True)"
            )
    except Exception as e:
        results["failed"].append(f"realtime_flush: {e}")

    # Test 6: Async stream in async context
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

    # Test 7: Mode checking in multi-mode streaming
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
