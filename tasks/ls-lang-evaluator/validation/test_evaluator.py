"""Test script for ls-lang-evaluator validation.

Checks evaluator existence, syntax, patterns, and logic for both
Python and TypeScript evaluators. Also validates LangSmith upload
and skill script usage.
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

from scaffold.python.validation.evaluator import check_evaluator_upload
from scaffold.python.validation.runner import TestRunner
from scaffold.python.validation.scripts import check_skill_scripts


def find_evaluator(directory, extensions):
    """Find evaluator file in directory."""
    d = Path(directory)
    if not d.exists():
        return None
    for ext in extensions:
        for name in ["evaluator", "evaluators"]:
            p = d / f"{name}.{ext}"
            if p.exists():
                return p
    return None


def find_eval_function(content, language):
    """Find evaluator function with (run, example) signature."""
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
        m = re.search(r"function\s+(\w+)\s*\(\s*run", content)
        if m:
            return m.group(1), None
        m = re.search(r"const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*run", content)
        if m:
            return m.group(1), None
        return None, "no (run, example) function found"


def check_exists(runner: TestRunner):
    """Check evaluator files exist."""
    py_dir = runner.artifacts[0]
    js_dir = runner.artifacts[1]
    py = find_evaluator(py_dir, ["py"])
    js = find_evaluator(js_dir, ["ts", "js"])
    if py:
        runner.passed(f"Python evaluator: {py.name} exists")
    else:
        runner.failed(f"Python evaluator: not found in {py_dir}/")
    if js:
        runner.passed(f"JavaScript evaluator: {js.name} exists")
    else:
        runner.failed(f"JavaScript evaluator: not found in {js_dir}/")


def check_syntax(runner: TestRunner):
    """Check evaluator syntax."""
    py_dir = runner.artifacts[0]
    js_dir = runner.artifacts[1]
    py = find_evaluator(py_dir, ["py"])
    if py:
        try:
            ast.parse(py.read_text())
            runner.passed(f"Python: {py.name} valid syntax")
        except SyntaxError as e:
            runner.failed(f"Python: syntax error at line {e.lineno}: {e.msg}")
    else:
        runner.failed(f"Python syntax: skipped (no evaluator in {py_dir}/)")

    js = find_evaluator(js_dir, ["ts", "js"])
    if js:
        content = js.read_text()
        balanced = (
            content.count("{") == content.count("}")
            and content.count("(") == content.count(")")
            and content.count("[") == content.count("]")
        )
        has_func = "function" in content or "=>" in content
        if balanced and has_func and "return" in content:
            runner.passed(f"JavaScript: {js.name} valid syntax")
        else:
            runner.failed(f"JavaScript: {js.name} syntax appears invalid")
    else:
        runner.failed(f"JavaScript syntax: skipped (no evaluator in {js_dir}/)")


def check_patterns(runner: TestRunner):
    """Check evaluator follows LangSmith patterns."""
    py_dir = runner.artifacts[0]
    js_dir = runner.artifacts[1]

    py = find_evaluator(py_dir, ["py"])
    if py:
        content = py.read_text()
        if re.search(r"def\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example", content):
            runner.passed("Python: has (run, example) signature")
        else:
            runner.failed("Python: missing (run, example) function signature")
        if re.search(r"return\s*\{[^}]*['\"]?\w+['\"]?\s*:", content):
            runner.passed("Python: returns dict with score")
        else:
            runner.failed("Python: missing return dict with score")
        if re.search(r"run\[.outputs.\]|run\.outputs|run\.get\(.outputs", content):
            runner.passed("Python: accesses run outputs")
        else:
            runner.failed("Python: missing run outputs access")
        if re.search(r"example\[.outputs.\]|example\.outputs|example\.get\(.outputs", content):
            runner.passed("Python: accesses example outputs")
        else:
            runner.failed("Python: missing example outputs access")
    else:
        runner.failed("Python patterns: skipped (no evaluator)")

    js = find_evaluator(js_dir, ["ts", "js"])
    if js:
        content = js.read_text()
        has_sig = re.search(
            r"function\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example", content
        ) or re.search(r"=\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)\s*=>", content)
        if has_sig:
            runner.passed("JavaScript: has (run, example) signature")
        else:
            runner.failed("JavaScript: missing (run, example) function signature")
        if re.search(r"return\s*\{[^}]*(?:\w+\s*:|score)", content):
            runner.passed("JavaScript: returns object with score")
        else:
            runner.failed("JavaScript: missing return object with score")
        if re.search(r'run[.?]+outputs|run\[["\']outputs', content):
            runner.passed("JavaScript: accesses run.outputs")
        else:
            runner.failed("JavaScript: missing run.outputs access")
        if re.search(r'example[.?]+outputs|example\[["\']outputs', content):
            runner.passed("JavaScript: accesses example.outputs")
        else:
            runner.failed("JavaScript: missing example.outputs access")
    else:
        runner.failed("JavaScript patterns: skipped (no evaluator)")


def _parse_eval_results(output, success, lang, runner: TestRunner):
    """Parse EVALUATOR_RESULTS from output."""
    for line in output.split("\n"):
        if line.startswith("EVALUATOR_RESULTS:"):
            try:
                results = json.loads(line.replace("EVALUATOR_RESULTS:", ""))
                passed_count = sum(1 for r in results if r.get("passed"))
                total = len(results)
                msg = f"{lang} logic: {passed_count}/{total} tests"
                if passed_count == total:
                    runner.passed(msg + " passed")
                elif passed_count > total // 2:
                    runner.passed(msg + " (partial)")
                else:
                    runner.failed(msg + " passed")
                return
            except json.JSONDecodeError:
                pass
    if success:
        runner.passed(f"{lang} logic: executed")
    else:
        runner.failed(f"{lang} logic: execution failed - {output[:150]}")


def check_python_logic(runner: TestRunner):
    """Run Python evaluator against test cases."""
    py_dir = runner.artifacts[0]
    py = find_evaluator(py_dir, ["py"])
    if not py:
        runner.failed("Python logic: skipped (no evaluator)")
        return

    content = py.read_text()
    func_name, error = find_eval_function(content, "python")
    if error:
        runner.failed(f"Python logic: {error}")
        return

    test_cases = Path("data/trajectory_test_cases.json").resolve()
    if not test_cases.exists():
        runner.failed("Python logic: no test cases")
        return

    eval_runner = Path("validation/eval_runner.py").resolve()
    if not eval_runner.exists():
        runner.failed("Python logic: no eval_runner.py")
        return

    module_name = py.name.replace(".py", "")
    try:
        r = subprocess.run(
            [sys.executable, str(eval_runner), module_name, func_name, str(test_cases)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(py.parent),
        )
        _parse_eval_results(r.stdout + r.stderr, r.returncode == 0, "Python", runner)
    except Exception as e:
        runner.failed(f"Python logic: {str(e)[:50]}")


def check_js_logic(runner: TestRunner):
    """Run JavaScript evaluator against test cases."""
    js_dir = runner.artifacts[1]
    js = find_evaluator(js_dir, ["ts", "js"])
    if not js:
        runner.failed("JavaScript logic: skipped (no evaluator)")
        return

    content = js.read_text()
    func_name, error = find_eval_function(content, "javascript")
    if error:
        runner.failed(f"JavaScript logic: {error}")
        return

    test_cases = Path("data/single_step_test_cases.json").resolve()
    if not test_cases.exists():
        runner.failed("JavaScript logic: no test cases")
        return

    eval_runner = Path("validation/eval_runner.ts").resolve()
    if not eval_runner.exists():
        runner.failed("JavaScript logic: no eval_runner.ts")
        return

    try:
        r = subprocess.run(
            ["npx", "tsx", str(eval_runner), js.name, func_name, str(test_cases)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(js.parent),
        )
        _parse_eval_results(r.stdout + r.stderr, r.returncode == 0, "JavaScript", runner)
    except Exception as e:
        runner.failed(f"JavaScript logic: {str(e)[:50]}")


def check_upload(runner: TestRunner):
    """Validate that evaluators were uploaded to LangSmith."""
    p, f = check_evaluator_upload(Path("."), runner.context)
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
            check_exists,
            check_syntax,
            check_patterns,
            check_python_logic,
            check_js_logic,
            check_upload,
            check_scripts,
        ]
    )
