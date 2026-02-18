"""Evaluator validation utilities.

Validates evaluator files for:
- Existence and language correctness
- Syntax validity
- LangSmith evaluator patterns (run, example signature)
- Logic execution via Docker
- LangSmith upload verification
"""

import ast
import json
import re
from pathlib import Path

from scaffold.python.validation.langsmith import get_langsmith_client


def find_evaluator_file(
    test_dir: Path,
    directory: str,
    extensions: list[str],
) -> Path | None:
    """Find evaluator file in a directory.

    Args:
        test_dir: Test working directory
        directory: Subdirectory (e.g., "backend", "frontend")
        extensions: List of file extensions to try

    Returns:
        Path to evaluator file or None
    """
    dir_path = test_dir / directory
    if not dir_path.exists():
        return None

    for ext in extensions:
        for name in ["evaluator", "evaluators"]:
            path = dir_path / f"{name}.{ext}"
            if path.exists():
                return path
    return None


def find_evaluator_function(content: str, language: str) -> tuple[str | None, str | None]:
    """Find evaluator function name via AST (Python) or regex (TypeScript).

    Args:
        content: File content
        language: "python" or "typescript"/"javascript"

    Returns:
        (function_name, error_message) - one will be None
    """
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
        # JavaScript/TypeScript - use regex
        func_match = re.search(r"function\s+(\w+)\s*\(\s*run", content)
        if func_match:
            return func_match.group(1), None
        # Try arrow function
        func_match = re.search(r"const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*run", content)
        if func_match:
            return func_match.group(1), None
        return None, "no (run, example) function found"


def validate_evaluator_exists(
    test_dir: Path,
    outputs: dict,
    python_dir: str = "backend",
    javascript_dir: str = "frontend",
) -> tuple[list[str], list[str]]:
    """Validate that evaluator files exist for both languages.

    Args:
        test_dir: Test working directory
        outputs: Outputs dict
        python_dir: Directory for Python evaluator
        javascript_dir: Directory for JavaScript/TypeScript evaluator

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []

    # Check Python evaluator
    py_path = find_evaluator_file(test_dir, python_dir, ["py"])
    if py_path:
        passed.append(f"Python evaluator: {py_path.name} exists")
    else:
        failed.append(f"Python evaluator: not found in {python_dir}/")

    # Check JavaScript/TypeScript evaluator
    js_path = find_evaluator_file(test_dir, javascript_dir, ["ts", "js"])
    if js_path:
        passed.append(f"JavaScript evaluator: {js_path.name} exists")
    else:
        failed.append(f"JavaScript evaluator: not found in {javascript_dir}/")

    return passed, failed


def validate_evaluator_syntax(
    test_dir: Path,
    outputs: dict,
    python_dir: str = "backend",
    javascript_dir: str = "frontend",
) -> tuple[list[str], list[str]]:
    """Validate evaluator code has valid syntax.

    Args:
        test_dir: Test working directory
        outputs: Outputs dict
        python_dir: Directory for Python evaluator
        javascript_dir: Directory for JavaScript/TypeScript evaluator

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []

    # Check Python syntax
    py_path = find_evaluator_file(test_dir, python_dir, ["py"])
    if py_path:
        content = py_path.read_text()
        try:
            ast.parse(content)
            passed.append(f"Python: {py_path.name} valid syntax")
        except SyntaxError as e:
            failed.append(f"Python: syntax error at line {e.lineno}: {e.msg}")

    # Check JavaScript/TypeScript syntax (basic check)
    js_path = find_evaluator_file(test_dir, javascript_dir, ["ts", "js"])
    if js_path:
        content = js_path.read_text()
        if _basic_js_syntax_check(content):
            passed.append(f"JavaScript: {js_path.name} valid syntax")
        else:
            failed.append(f"JavaScript: {js_path.name} syntax appears invalid")

    return passed, failed


def _basic_js_syntax_check(content: str) -> bool:
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


def validate_evaluator_patterns(
    test_dir: Path,
    outputs: dict,
    python_dir: str = "backend",
    javascript_dir: str = "frontend",
) -> tuple[list[str], list[str]]:
    """Validate that evaluators follow LangSmith patterns.

    Checks for:
    - (run, example) function signature
    - Access to run.outputs and example.outputs
    - Return dict with score

    Args:
        test_dir: Test working directory
        outputs: Outputs dict
        python_dir: Directory for Python evaluator
        javascript_dir: Directory for JavaScript/TypeScript evaluator

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []

    # Python patterns
    PY_FUNC_SIGNATURE = re.compile(r"def\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)")
    PY_RETURN_SCORE = re.compile(r"return\s*\{[^}]*['\"]?\w+['\"]?\s*:")

    py_path = find_evaluator_file(test_dir, python_dir, ["py"])
    if py_path:
        content = py_path.read_text()

        # Check function signature
        if PY_FUNC_SIGNATURE.search(content):
            passed.append("Python: has (run, example) signature")
        else:
            failed.append("Python: missing (run, example) function signature")

        # Check return format
        if PY_RETURN_SCORE.search(content):
            passed.append("Python: returns dict with score")
        else:
            failed.append("Python: missing return dict with score")

        # Check for run outputs access
        if 'run["outputs"]' in content or "run['outputs']" in content or "run.outputs" in content:
            passed.append("Python: accesses run outputs")
        else:
            failed.append("Python: missing run outputs access")

        # Check for example outputs access
        if 'example["outputs"]' in content or "example['outputs']" in content or "example.outputs" in content:
            passed.append("Python: accesses example outputs")
        else:
            failed.append("Python: missing example outputs access")

    # JavaScript patterns
    JS_FUNC_SIGNATURE = re.compile(r"function\s+\w+\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)")
    JS_ARROW_SIGNATURE = re.compile(r"=\s*\(\s*run\s*(:\s*\w+)?\s*,\s*example\s*(:\s*\w+)?\s*\)\s*=>")
    JS_RETURN_SCORE = re.compile(r"return\s*\{[^}]*\w+\s*:")

    js_path = find_evaluator_file(test_dir, javascript_dir, ["ts", "js"])
    if js_path:
        content = js_path.read_text()

        # Check function signature
        if JS_FUNC_SIGNATURE.search(content) or JS_ARROW_SIGNATURE.search(content):
            passed.append("JavaScript: has (run, example) signature")
        else:
            failed.append("JavaScript: missing (run, example) function signature")

        # Check return format
        if JS_RETURN_SCORE.search(content):
            passed.append("JavaScript: returns object with score")
        else:
            failed.append("JavaScript: missing return object with score")

        # Check for outputs access
        if "run.outputs" in content:
            passed.append("JavaScript: accesses run.outputs")
        else:
            failed.append("JavaScript: missing run.outputs access")

        if "example.outputs" in content:
            passed.append("JavaScript: accesses example.outputs")
        else:
            failed.append("JavaScript: missing example.outputs access")

    return passed, failed


def validate_evaluator_logic(
    test_dir: Path,
    outputs: dict,
    python_dir: str = "backend",
    javascript_dir: str = "frontend",
    py_test_cases: str = "trajectory_test_cases.json",
    ts_test_cases: str = "single_step_test_cases.json",
    data_dir: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Validate evaluator logic by running test cases in Docker.

    Args:
        test_dir: Test working directory
        outputs: Outputs dict
        python_dir: Directory for Python evaluator
        javascript_dir: Directory for JavaScript/TypeScript evaluator
        py_test_cases: Python test cases filename
        ts_test_cases: TypeScript test cases filename
        data_dir: Directory containing test cases

    Returns:
        (passed, failed) lists
    """
    from scaffold.python.utils import run_node_in_docker, run_python_in_docker

    passed, failed = [], []
    data_dir = data_dir or (test_dir.parent / "data")
    validation_dir = test_dir.parent / "validation"

    # Test Python evaluator
    py_path = find_evaluator_file(test_dir, python_dir, ["py"])
    if py_path:
        py_passed, py_failed = _test_python_evaluator(
            py_path, test_dir, py_test_cases, data_dir, validation_dir, run_python_in_docker
        )
        passed.extend(py_passed)
        failed.extend(py_failed)

    # Test JavaScript evaluator
    js_path = find_evaluator_file(test_dir, javascript_dir, ["ts", "js"])
    if js_path:
        js_passed, js_failed = _test_js_evaluator(
            js_path, test_dir, ts_test_cases, data_dir, run_node_in_docker
        )
        passed.extend(js_passed)
        failed.extend(js_failed)

    return passed, failed


def _test_python_evaluator(
    path: Path,
    test_dir: Path,
    test_cases_filename: str,
    data_dir: Path,
    validation_dir: Path,
    run_python_fn,
) -> tuple[list[str], list[str]]:
    """Test Python evaluator using eval_runner.py in Docker."""
    content = path.read_text()
    func_name, error = find_evaluator_function(content, "python")
    if error:
        return [], [f"Python logic: {error}"]

    # Copy test cases if not present
    test_cases_path = path.parent / test_cases_filename
    if not test_cases_path.exists():
        source_path = data_dir / test_cases_filename
        if source_path.exists():
            test_cases_path.write_text(source_path.read_text())
        else:
            return ["Python logic: no test cases"], []

    # Copy eval_runner.py
    runner_src = validation_dir / "eval_runner.py"
    runner_dst = path.parent / "_eval_runner.py"
    if runner_src.exists():
        runner_dst.write_text(runner_src.read_text())
    else:
        return ["Python logic: no eval_runner.py"], []

    try:
        module_name = path.name.replace(".py", "")
        args = [module_name, func_name, test_cases_filename]
        success, output = run_python_fn(test_dir, f"{path.parent.name}/_eval_runner.py", timeout=60, args=args)
        return _parse_evaluator_results(output, success, "Python")
    except Exception as e:
        return [], [f"Python logic: {str(e)[:50]}"]
    finally:
        runner_dst.unlink(missing_ok=True)


def _test_js_evaluator(
    path: Path,
    test_dir: Path,
    test_cases_filename: str,
    data_dir: Path,
    run_node_fn,
) -> tuple[list[str], list[str]]:
    """Test JavaScript evaluator using inline test harness in Docker."""
    content = path.read_text()
    func_name, error = find_evaluator_function(content, "javascript")
    if error:
        return [], [f"JavaScript logic: {error}"]

    # Load test cases
    test_cases_path = data_dir / test_cases_filename
    if not test_cases_path.exists():
        return ["JavaScript logic: no test cases"], []

    test_cases = json.loads(test_cases_path.read_text())

    # Create test harness script
    test_script = f'''
const fs = require('fs');
const evaluatorCode = fs.readFileSync('{path.name}', 'utf8');
eval(evaluatorCode);

const testCases = {json.dumps(test_cases)};

function normalizeScore(score) {{
    if (typeof score === 'boolean') return score ? 1.0 : 0.0;
    if (typeof score === 'number') return score >= 0 && score <= 1 ? score : (score > 1 ? score / 100 : 0);
    return 0.0;
}}

function extractScore(result) {{
    if (typeof result === 'number' || typeof result === 'boolean') return result;
    if (result && typeof result === 'object') {{
        for (const key of ['score', 'value', 'result', 'pass', 'passed']) {{
            if (key in result) return result[key];
        }}
    }}
    return null;
}}

const results = testCases.map(tc => {{
    const name = tc.name || 'unknown';
    const expected = tc.expected_result || {{}};
    const run = tc.run || {{}};
    const example = tc.example || {{}};

    try {{
        const result = {func_name}(run, example);
        if (expected.should_not_crash) {{
            return {{ name, passed: true }};
        }}
        let score = extractScore(result);
        if (score === null) {{
            return {{ name, passed: false, error: 'no score' }};
        }}
        score = normalizeScore(score);
        const minS = expected.min_score || 0;
        const maxS = expected.max_score || 1;
        return {{ name, passed: score >= minS && score <= maxS, score }};
    }} catch (e) {{
        if (expected.should_not_crash) {{
            return {{ name, passed: false, error: e.message.slice(0, 50) }};
        }}
        return {{ name, passed: false, error: e.message.slice(0, 50) }};
    }}
}});

console.log("EVALUATOR_RESULTS:" + JSON.stringify(results));
'''

    test_file = path.parent / "_test_evaluator.js"
    try:
        test_file.write_text(test_script)
        success, output = run_node_fn(test_dir, f"{path.parent.name}/_test_evaluator.js", timeout=60)
        return _parse_evaluator_results(output, success, "JavaScript")
    except Exception as e:
        return [], [f"JavaScript logic: {str(e)[:50]}"]
    finally:
        test_file.unlink(missing_ok=True)


def _parse_evaluator_results(output: str, success: bool, lang: str) -> tuple[list[str], list[str]]:
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

    return (
        ([f"{lang} logic: executed"], []) if success else ([], [f"{lang} logic: execution failed"])
    )


def validate_evaluator_upload(
    test_dir: Path,
    outputs: dict,
    upload_prefix: str = "test-",
) -> tuple[list[str], list[str]]:
    """Validate evaluators were uploaded to LangSmith via /runs/rules API.

    Args:
        test_dir: Test working directory (unused but matches signature)
        outputs: Outputs dict containing run_id
        upload_prefix: Prefix for evaluator names

    Returns:
        (passed, failed) lists
    """
    client, error = get_langsmith_client()
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
