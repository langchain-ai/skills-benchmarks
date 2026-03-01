"""Test script for ls-lang-evaluator validation.

Checks evaluator existence, syntax, patterns, and logic for both
Python and TypeScript evaluators. Runs inside Docker via make_execution_validator.

Usage: python test_evaluator.py <py_evaluator_dir> <js_evaluator_dir>
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path


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


def check_exists(py_dir, js_dir):
    """Check evaluator files exist."""
    passed, failed = [], []
    py = find_evaluator(py_dir, ["py"])
    js = find_evaluator(js_dir, ["ts", "js"])
    if py:
        passed.append(f"Python evaluator: {py.name} exists")
    else:
        failed.append(f"Python evaluator: not found in {py_dir}/")
    if js:
        passed.append(f"JavaScript evaluator: {js.name} exists")
    else:
        failed.append(f"JavaScript evaluator: not found in {js_dir}/")
    return passed, failed


def check_syntax(py_dir, js_dir):
    """Check evaluator syntax."""
    passed, failed = [], []
    py = find_evaluator(py_dir, ["py"])
    if py:
        try:
            ast.parse(py.read_text())
            passed.append(f"Python: {py.name} valid syntax")
        except SyntaxError as e:
            failed.append(f"Python: syntax error at line {e.lineno}: {e.msg}")

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
            passed.append(f"JavaScript: {js.name} valid syntax")
        else:
            failed.append(f"JavaScript: {js.name} syntax appears invalid")
    return passed, failed


def check_patterns(py_dir, js_dir):
    """Check evaluator follows LangSmith patterns."""
    passed, failed = [], []

    py = find_evaluator(py_dir, ["py"])
    if py:
        content = py.read_text()
        if re.search(r"def\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example", content):
            passed.append("Python: has (run, example) signature")
        else:
            failed.append("Python: missing (run, example) function signature")
        if re.search(r"return\s*\{[^}]*['\"]?\w+['\"]?\s*:", content):
            passed.append("Python: returns dict with score")
        else:
            failed.append("Python: missing return dict with score")
        if re.search(r"run\[.outputs.\]|run\.outputs|run\.get\(.outputs", content):
            passed.append("Python: accesses run outputs")
        else:
            failed.append("Python: missing run outputs access")
        if re.search(r"example\[.outputs.\]|example\.outputs|example\.get\(.outputs", content):
            passed.append("Python: accesses example outputs")
        else:
            failed.append("Python: missing example outputs access")

    js = find_evaluator(js_dir, ["ts", "js"])
    if js:
        content = js.read_text()
        has_sig = re.search(
            r"function\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example", content
        ) or re.search(r"=\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)\s*=>", content)
        if has_sig:
            passed.append("JavaScript: has (run, example) signature")
        else:
            failed.append("JavaScript: missing (run, example) function signature")
        if re.search(r"return\s*\{[^}]*(?:\w+\s*:|score)", content):
            passed.append("JavaScript: returns object with score")
        else:
            failed.append("JavaScript: missing return object with score")
        if re.search(r'run[.?]+outputs|run\[["\']outputs', content):
            passed.append("JavaScript: accesses run.outputs")
        else:
            failed.append("JavaScript: missing run.outputs access")
        if re.search(r'example[.?]+outputs|example\[["\']outputs', content):
            passed.append("JavaScript: accesses example.outputs")
        else:
            failed.append("JavaScript: missing example.outputs access")

    return passed, failed


def check_python_logic(py_dir, test_cases_file):
    """Run Python evaluator against test cases."""
    py = find_evaluator(py_dir, ["py"])
    if not py:
        return [], []

    content = py.read_text()
    func_name, error = find_eval_function(content, "python")
    if error:
        return [], [f"Python logic: {error}"]

    test_cases = Path(test_cases_file).resolve()
    if not test_cases.exists():
        return ["Python logic: no test cases"], []

    runner = Path("eval_runner.py").resolve()
    if not runner.exists():
        return ["Python logic: no eval_runner.py"], []

    module_name = py.name.replace(".py", "")
    try:
        r = subprocess.run(
            [sys.executable, str(runner), module_name, func_name, str(test_cases)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(py.parent),
        )
        return _parse_eval_results(r.stdout + r.stderr, r.returncode == 0, "Python")
    except Exception as e:
        return [], [f"Python logic: {str(e)[:50]}"]


def check_js_logic(js_dir, test_cases_file):
    """Run JavaScript evaluator against test cases."""
    js = find_evaluator(js_dir, ["ts", "js"])
    if not js:
        return [], []

    content = js.read_text()
    func_name, error = find_eval_function(content, "javascript")
    if error:
        return [], [f"JavaScript logic: {error}"]

    test_cases = Path(test_cases_file).resolve()
    if not test_cases.exists():
        return ["JavaScript logic: no test cases"], []

    runner = Path("eval_runner.ts").resolve()
    if not runner.exists():
        return ["JavaScript logic: no eval_runner.ts"], []

    try:
        r = subprocess.run(
            ["npx", "tsx", str(runner), js.name, func_name, str(test_cases)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(js.parent),
        )
        return _parse_eval_results(r.stdout + r.stderr, r.returncode == 0, "JavaScript")
    except Exception as e:
        return [], [f"JavaScript logic: {str(e)[:50]}"]


def _parse_eval_results(output, success, lang):
    """Parse EVALUATOR_RESULTS from output."""
    for line in output.split("\n"):
        if line.startswith("EVALUATOR_RESULTS:"):
            try:
                results = json.loads(line.replace("EVALUATOR_RESULTS:", ""))
                passed_count = sum(1 for r in results if r.get("passed"))
                total = len(results)
                msg = f"{lang} logic: {passed_count}/{total} tests"
                if passed_count == total:
                    return [msg + " passed"], []
                elif passed_count > total // 2:
                    return [msg + " (partial)"], []
                else:
                    return [], [msg + " passed"]
            except json.JSONDecodeError:
                pass
    if success:
        return [f"{lang} logic: executed"], []
    return [], [f"{lang} logic: execution failed - {output[:150]}"]


def run_tests(py_dir, js_dir):
    passed, failed = [], []
    for p, f in [
        check_exists(py_dir, js_dir),
        check_syntax(py_dir, js_dir),
        check_patterns(py_dir, js_dir),
        check_python_logic(py_dir, "trajectory_test_cases.json"),
        check_js_logic(js_dir, "single_step_test_cases.json"),
    ]:
        passed.extend(p)
        failed.extend(f)
    return {"passed": passed, "failed": failed, "error": None}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_evaluator.py <python_dir> <typescript_dir>")
        sys.exit(1)
    results = run_tests(sys.argv[1], sys.argv[2])
    print(json.dumps(results, indent=2))
    with open("_test_results.json", "w") as f:
        json.dump(results, f)
    sys.exit(1 if results["failed"] else 0)
