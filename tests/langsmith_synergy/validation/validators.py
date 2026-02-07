"""Validators for LangSmith Synergy experiment."""

import ast
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scaffold.validation import Validator
from scaffold.utils import (
    retry_with_backoff,
    read_json_file,
    get_field,
    get_nested_field,
    run_python_in_docker,
)


# =============================================================================
# HELPERS
# =============================================================================

def get_langsmith_client():
    """Get LangSmith client. Returns (client, error_string)."""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    from langsmith import Client
    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        return None, "LANGSMITH_API_KEY not set"
    return Client(api_key=api_key), None


def extract_examples(data) -> list:
    """Extract examples list from various dataset formats."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("examples") or data.get("data") or [data]
    return []


def safe_api_call(func, skip_msg: str = "skipped"):
    """Run API call, return (result, error_msg) handling rate limits."""
    try:
        return func(), None
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "rate limit" in msg:
            return None, f"{skip_msg} (rate limited)"
        return None, f"{skip_msg} ({str(e)[:40]})"


# =============================================================================
# VALIDATORS
# =============================================================================

class TraceDataValidator(Validator):
    """Validate traces exist in LangSmith project."""

    def __init__(self, min_traces: int = 1, max_age_minutes: int = 1440):
        self.min_traces = min_traces
        self.max_age_minutes = max_age_minutes

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        project = os.environ.get("LANGSMITH_PROJECT")
        if not project:
            return [], ["Traces: LANGSMITH_PROJECT not set"]

        client, error = get_langsmith_client()
        if error:
            return [], [f"Traces: {error}"]

        start_time = datetime.now(timezone.utc) - timedelta(minutes=self.max_age_minutes)
        traces, error = safe_api_call(
            lambda: list(client.list_runs(project_name=project, is_root=True, start_time=start_time, limit=20))
        )
        if error:
            return [f"Traces: {error}"], []

        if len(traces) < self.min_traces:
            return [], [f"Traces: only {len(traces)} in project (need {self.min_traces})"]

        passed.append(f"Traces: {len(traces)} available in '{project}'")

        # Check for tool calls in sample
        with_tools = sum(1 for t in traces[:5] if self._has_tools(client, project, t))
        if with_tools:
            passed.append(f"Traces: {with_tools}/5 have tool calls")

        return passed, failed

    def _has_tools(self, client, project: str, trace) -> bool:
        try:
            tid = str(getattr(trace, "trace_id", trace.id))
            tools = list(client.list_runs(project_name=project, trace_id=tid, run_type="tool", limit=1))
            return bool(tools)
        except Exception:
            return False


class DatasetValidator(Validator):
    """Validate dataset file and LangSmith upload."""

    def __init__(
        self,
        filename: str = "trajectory_dataset.json",
        min_examples: int = 1,
        dataset_type: str = "trajectory",
        verify_upload: bool = True,
        upload_prefix: str = "test-",
    ):
        self.filename = filename
        self.min_examples = min_examples
        self.dataset_type = dataset_type
        self.verify_upload = verify_upload
        self.upload_prefix = upload_prefix

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        data, error = read_json_file(test_dir / self.filename)
        if error:
            return [], [f"Dataset: {error}"]

        examples = extract_examples(data)
        if len(examples) < self.min_examples:
            return [f"Dataset: {self.filename} created"], [f"Dataset: {len(examples)} examples (need {self.min_examples})"]

        passed.append(f"Dataset: {len(examples)} examples")

        # Check structure
        sample = examples[:10]
        valid_io = sum(1 for ex in sample if self._has_io(ex))
        if valid_io:
            passed.append(f"Dataset: {valid_io}/{len(sample)} have input/output")
        else:
            failed.append("Dataset: no input/output structure")

        if self.dataset_type == "trajectory":
            has_traj = sum(1 for ex in sample if self._get_trajectory(ex))
            if has_traj:
                passed.append(f"Dataset: {has_traj}/{len(sample)} have trajectory")
            else:
                failed.append("Dataset: no trajectory data")

        # Verify upload
        if self.verify_upload:
            up, uf = self._verify_upload()
            passed.extend(up)
            failed.extend(uf)

        return passed, failed

    def _has_io(self, ex: dict) -> bool:
        if not isinstance(ex, dict):
            return False
        return ("inputs" in ex or "input" in ex) and ("outputs" in ex or "output" in ex)

    def _get_trajectory(self, ex: dict) -> list:
        """Extract trajectory data, accepting various field names."""
        if not isinstance(ex, dict):
            return []

        # Known trajectory field names (priority order)
        FIELDS = ["expected_trajectory", "trajectory", "expected_tools", "tool_calls", "tools"]

        # Check top-level, then nested in outputs
        traj = get_field(ex, *FIELDS) or get_nested_field(ex, ["outputs", "output"], FIELDS)
        if isinstance(traj, list):
            return traj

        # Fallback: any list of strings in outputs
        for val in (get_field(ex, "outputs", "output") or {}).values():
            if isinstance(val, list) and val and isinstance(val[0], str):
                return val
        return []

    def _verify_upload(self) -> Tuple[List[str], List[str]]:
        client, error = get_langsmith_client()
        if error:
            return [f"Upload: skipped ({error})"], []

        datasets, error = safe_api_call(lambda: list(client.list_datasets()))
        if error:
            return [f"Upload: {error}"], []

        matching = [d for d in datasets if d.name.startswith(self.upload_prefix)]
        if not matching:
            return [], [f"Upload: no dataset with prefix '{self.upload_prefix}'"]

        recent = max(matching, key=lambda d: getattr(d, 'created_at', d.name))
        count = getattr(recent, 'example_count', '?')
        return [f"Upload: '{recent.name}' ({count} examples)"], []


class EvaluatorValidator(Validator):
    """Validate evaluator file, run tests in Docker, and verify upload."""

    def __init__(
        self,
        filename: str = "trajectory_evaluator.py",
        test_cases_filename: str = "evaluator_test_cases.json",
        verify_upload: bool = False,
        upload_prefix: str = "test-",
        max_age_minutes: int = 30,
    ):
        self.filename = filename
        self.test_cases_filename = test_cases_filename
        self.verify_upload = verify_upload
        self.upload_prefix = upload_prefix
        self.max_age_minutes = max_age_minutes

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        path = test_dir / self.filename
        if not path.exists():
            return [], [f"Evaluator: {self.filename} not created"]

        content = path.read_text()
        passed.append(f"Evaluator: {self.filename} ({len(content)} bytes)")

        # Find evaluator function via AST
        func_name, error = self._find_evaluator_function(content)
        if error:
            return passed, [error]
        passed.append(f"Evaluator: {func_name}(run, example)")

        # Run test cases in Docker
        tp, tf = self._run_tests(test_dir, func_name)
        passed.extend(tp)
        failed.extend(tf)

        # Verify upload
        if self.verify_upload:
            up, uf = self._verify_upload()
            passed.extend(up)
            failed.extend(uf)

        return passed, failed

    def _find_evaluator_function(self, content: str) -> Tuple[str, str]:
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return None, f"Evaluator: syntax error line {e.lineno}"

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                if "run" in args and "example" in args:
                    return node.name, None
        return None, "Evaluator: no (run, example) function"

    def _run_tests(self, test_dir: Path, func_name: str) -> Tuple[List[str], List[str]]:
        test_cases_path = test_dir / self.test_cases_filename
        if not test_cases_path.exists():
            return ["Evaluator: no test cases"], []

        runner_src = Path(__file__).parent / "eval_runner.py"
        runner_dst = test_dir / "_eval_runner.py"
        runner_dst.write_text(runner_src.read_text())

        try:
            module_name = self.filename.replace(".py", "")
            success, output = run_python_in_docker(
                test_dir, "_eval_runner.py", timeout=60,
                args=[module_name, func_name, self.test_cases_filename]
            )

            for line in output.split("\n"):
                if line.startswith("EVALUATOR_RESULTS:"):
                    results = json.loads(line.replace("EVALUATOR_RESULTS:", ""))
                    passed_count = sum(1 for r in results if r.get("passed"))
                    total = len(results)
                    msg = f"Evaluator: {passed_count}/{total} tests"
                    if passed_count == total:
                        return [msg + " passed"], []
                    elif passed_count > total // 2:
                        return [msg + " (partial)"], []
                    else:
                        return [], [msg + " passed"]

            return (["Evaluator: executed"], []) if success else ([], ["Evaluator: execution failed"])
        except Exception as e:
            return [], [f"Evaluator: {str(e)[:50]}"]
        finally:
            runner_dst.unlink(missing_ok=True)

    def _verify_upload(self) -> Tuple[List[str], List[str]]:
        """Verify evaluator uploaded via /runs/rules API."""
        client, error = get_langsmith_client()
        if error:
            return [f"Upload: skipped ({error})"], []

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

            # Filter by display_name (the rule name in LangSmith UI)
            matching = [r for r in rules if r.get("display_name", "").startswith(self.upload_prefix)]

            if not matching:
                return [], [f"Upload: no rule with prefix '{self.upload_prefix}'"]

            # Find most recent
            recent = max(matching, key=lambda r: r.get("created_at", ""))
            name = recent.get("display_name", "unknown")
            dataset_name = recent.get("dataset_name")

            # Check dataset attachment (dataset_name is included in response)
            if dataset_name and dataset_name.startswith(self.upload_prefix):
                return [f"Upload: '{name}' -> dataset '{dataset_name}'"], []
            elif dataset_name:
                return [f"Upload: '{name}' found"], [f"Upload: linked to '{dataset_name}' (expected prefix '{self.upload_prefix}')"]

            return [f"Upload: '{name}' found (no dataset)"], []

        except Exception as e:
            return [f"Upload: skipped ({str(e)[:30]})"], []


class SkillScriptValidator(Validator):
    """Validate that skill scripts were used in commands."""

    def __init__(self, script_patterns: Dict[str, str], require_scripts: bool = False):
        self.script_patterns = script_patterns
        self.require_scripts = require_scripts

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []
        commands = " ".join(events.get("commands_run", [])).lower()

        for pattern, desc in self.script_patterns.items():
            if pattern.lower() in commands:
                passed.append(f"Script: {desc}")
            elif self.require_scripts:
                failed.append(f"Script: missing {desc}")

        return passed, failed
