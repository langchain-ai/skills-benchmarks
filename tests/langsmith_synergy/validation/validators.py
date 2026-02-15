"""Validators for LangSmith Synergy experiment."""

import ast
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scaffold import (
    Validator,
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

class DatasetStructureValidator(Validator):
    """Validate dataset file structure (not content accuracy - see TrajectoryAccuracyValidator)."""

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
            run_id = outputs.get("_run_id") if outputs else None
            up, uf = self._verify_upload(run_id)
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

    def _verify_upload(self, run_id: str = None) -> Tuple[List[str], List[str]]:
        client, error = get_langsmith_client()
        if error:
            return [f"Upload: skipped ({error})"], []

        datasets, error = safe_api_call(lambda: list(client.list_datasets()))
        if error:
            return [f"Upload: {error}"], []

        # Use run_id for precise matching if available
        if run_id:
            search_pattern = f"{self.upload_prefix}{run_id}"
        else:
            search_pattern = self.upload_prefix
        matching = [d for d in datasets if d.name.startswith(search_pattern)]
        if not matching:
            return [], [f"Upload: no dataset with prefix '{search_pattern}'"]

        recent = max(matching, key=lambda d: getattr(d, 'created_at', d.name))
        count = getattr(recent, 'example_count', '?')
        return [f"Upload: '{recent.name}' ({count} examples)"], []


class EvaluatorValidator(Validator):
    """Validate evaluator file, run tests in Docker, and verify upload."""

    def __init__(
        self,
        filename: str = "trajectory_evaluator.py",
        test_cases_filename: str = "evaluator_test_cases.json",
        dataset_filename: str = "trajectory_dataset.json",
        verify_upload: bool = False,
        upload_prefix: str = "test-",
    ):
        self.filename = filename
        self.test_cases_filename = test_cases_filename
        self.dataset_filename = dataset_filename
        self.verify_upload = verify_upload
        self.upload_prefix = upload_prefix

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

        # Run test cases in Docker (eval_runner handles dynamic test case generation)
        tp, tf = self._run_tests(test_dir, func_name)
        passed.extend(tp)
        failed.extend(tf)

        # Verify upload
        if self.verify_upload:
            run_id = outputs.get("_run_id") if outputs else None
            up, uf = self._verify_upload(run_id)
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
        # Copy test cases from data if not in test_dir
        test_cases_path = test_dir / self.test_cases_filename
        if not test_cases_path.exists():
            data_path = Path(__file__).parent.parent / "data" / self.test_cases_filename
            if data_path.exists():
                test_cases_path.write_text(data_path.read_text())
            else:
                return ["Evaluator: no test cases"], []

        runner_src = Path(__file__).parent / "eval_runner.py"
        runner_dst = test_dir / "_eval_runner.py"
        runner_dst.write_text(runner_src.read_text())

        try:
            module_name = self.filename.replace(".py", "")
            # Pass dataset filename so eval_runner can generate test cases dynamically
            args = [module_name, func_name, self.test_cases_filename, self.dataset_filename]
            success, output = run_python_in_docker(
                test_dir, "_eval_runner.py", timeout=60,
                args=args
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

    def _verify_upload(self, run_id: str = None) -> Tuple[List[str], List[str]]:
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

            # Use run_id for precise matching if available
            if run_id:
                search_pattern = f"{self.upload_prefix}{run_id}"
            else:
                search_pattern = self.upload_prefix

            # Filter by display_name (the rule name in LangSmith UI)
            matching = [r for r in rules if r.get("display_name", "").startswith(search_pattern)]

            if not matching:
                return [], [f"Upload: no rule with prefix '{search_pattern}'"]

            # Find most recent
            recent = max(matching, key=lambda r: r.get("created_at", ""))
            name = recent.get("display_name", "unknown")
            dataset_name = recent.get("dataset_name")

            # Check dataset attachment (dataset_name is included in response)
            if dataset_name and dataset_name.startswith(search_pattern):
                return [f"Upload: '{name}' -> dataset '{dataset_name}'"], []
            elif dataset_name:
                return [f"Upload: '{name}' found"], [f"Upload: linked to '{dataset_name}' (expected prefix '{search_pattern}')"]

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


class TrajectoryAccuracyValidator(Validator):
    """Validate dataset content matches actual LangSmith trace data.

    CRITICAL: This validator ensures Claude's dataset contains REAL trace data,
    not fabricated content. It checks:
    1. Every expected trace appears exactly once in actual output
    2. Tool sequences match expected (ORDER MATTERS)
    3. Uploaded dataset matches local file

    Example ordering and extra fields are allowed.
    Duplicates naturally fail because each expected can only match once.
    """

    # Path to pre-generated expected dataset
    DATA_DIR = Path(__file__).parent.parent / "data"

    def __init__(
        self,
        filename: str = "trajectory_dataset.json",
        expected_filename: str = "expected_dataset.json",
        verify_upload: bool = True,
        upload_prefix: str = "test-",
    ):
        self.filename = filename
        self.expected_filename = expected_filename
        self.verify_upload = verify_upload
        self.upload_prefix = upload_prefix

    def validate(self, events: dict, test_dir: Path, outputs: Dict = None) -> Tuple[List[str], List[str]]:
        passed, failed = [], []

        # Load Claude's dataset
        actual_data, error = read_json_file(test_dir / self.filename)
        if error:
            return [], [f"Accuracy: {error}"]
        actual_examples = extract_examples(actual_data)

        if not actual_examples:
            return [], ["Accuracy: no examples in dataset"]

        # Load ground truth from data directory
        expected_data, error = read_json_file(self.DATA_DIR / self.expected_filename)
        if error:
            return [f"Accuracy: skipped (no ground truth)"], []
        expected_examples = expected_data.get("examples", [])

        if not expected_examples:
            return [f"Accuracy: skipped (empty ground truth)"], []

        # Match actual examples against expected - each expected must appear exactly once
        matches, mismatches, missing = self._compare_datasets(actual_examples, expected_examples)

        # Report results
        total_expected = len(expected_examples)

        if matches == total_expected:
            passed.append(f"Accuracy: {matches}/{total_expected} trajectories match")
        elif matches > 0:
            failed.append(f"Accuracy: only {matches}/{total_expected} trajectories match")
        else:
            failed.append(f"Accuracy: 0/{total_expected} trajectories match")

        if mismatches:
            first_mm = mismatches[0]
            failed.append(f"Accuracy: {len(mismatches)} wrong trajectories (e.g., {first_mm})")

        if missing:
            failed.append(f"Accuracy: {len(missing)} expected traces missing")

        # Verify uploaded dataset matches local file
        if self.verify_upload:
            run_id = outputs.get("_run_id") if outputs else None
            up, uf = self._verify_upload_matches(actual_examples, run_id)
            passed.extend(up)
            failed.extend(uf)

        return passed, failed

    def _get_input_query(self, ex: dict) -> str:
        """Extract input query from example."""
        if not isinstance(ex, dict):
            return ""

        # Check various input locations
        inputs = ex.get("inputs") or ex.get("input") or {}
        if isinstance(inputs, str):
            return inputs
        if isinstance(inputs, dict):
            return inputs.get("query") or inputs.get("input") or inputs.get("question") or ""
        return ""

    def _extract_tool_names(self, traj: list) -> List[str]:
        """Extract tool names from trajectory list.

        Each item must be a string or simple dict with "name"/"tool" key.
        Returns None if format is invalid (e.g., complex nested objects).
        """
        result = []
        for item in traj:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                if "inputs" in item or "outputs" in item:  # Complex run object
                    return None
                name = item.get("name") or item.get("tool") or item.get("function")
                if isinstance(name, str):
                    result.append(name)
                else:
                    return None
            else:
                return None
        return result

    def _get_trajectory(self, ex: dict) -> List[str]:
        """Extract trajectory from example dict. Returns None if invalid format."""
        if not isinstance(ex, dict):
            return None

        outputs = ex.get("outputs") or ex.get("output") or {}
        for field in ["expected_trajectory", "trajectory", "tools", "tool_calls"]:
            traj = outputs.get(field) if isinstance(outputs, dict) else ex.get(field)
            if isinstance(traj, list):
                return self._extract_tool_names(traj)
        return None

    def _get_trace_id(self, ex: dict) -> str:
        """Extract trace_id from example."""
        return str(ex.get("trace_id") or ex.get("id") or "")

    def _compare_datasets(
        self, actual: List[dict], expected: List[dict]
    ) -> Tuple[int, List[str], List[str]]:
        """Compare actual dataset against expected ground truth.

        Each expected entry must appear exactly once in actual.
        Once an actual entry is matched, it cannot match another expected.

        Returns: (match_count, mismatch_details, missing_trace_ids)
        """
        matches = 0
        mismatches = []
        missing = []

        # Build lookup for actual examples by trace_id
        # Use list to handle potential duplicates (same trace_id appearing multiple times)
        actual_by_trace = {}
        for i, ex in enumerate(actual):
            trace_id = self._get_trace_id(ex)
            if trace_id:
                if trace_id not in actual_by_trace:
                    actual_by_trace[trace_id] = []
                actual_by_trace[trace_id].append((i, ex))

        # Track which actual entries have been used
        used_indices = set()

        # Check each expected example
        for exp_ex in expected:
            exp_trace_id = self._get_trace_id(exp_ex)
            exp_trajectory = self._get_trajectory(exp_ex)

            if not exp_trajectory:
                continue  # Skip expected examples without trajectory

            # Find matching actual example by trace_id
            actual_ex = None
            matched_idx = None

            if exp_trace_id and exp_trace_id in actual_by_trace:
                # Find first unused match with this trace_id
                for idx, ex in actual_by_trace[exp_trace_id]:
                    if idx not in used_indices:
                        actual_ex = ex
                        matched_idx = idx
                        break

            if actual_ex is None:
                missing.append(exp_trace_id or "unknown")
                continue

            # Mark as used
            used_indices.add(matched_idx)

            # Compare trajectories (ORDER MATTERS!)
            actual_trajectory = self._get_trajectory(actual_ex)

            # None means invalid format (e.g., complex nested objects instead of tool names)
            if actual_trajectory is None:
                exp_query = self._get_input_query(exp_ex)
                query_short = (exp_query[:20] + "...") if exp_query and len(exp_query) > 20 else (exp_query or "?")
                mismatches.append(f"'{query_short}': invalid trajectory format (expected list of tool names)")
                continue

            if actual_trajectory == exp_trajectory:
                matches += 1
            else:
                # Generate mismatch detail
                exp_query = self._get_input_query(exp_ex)
                detail = self._trajectory_diff(exp_trajectory, actual_trajectory, exp_query)
                mismatches.append(detail)

        return matches, mismatches, missing

    def _verify_upload_matches(self, local_examples: List[dict], run_id: str = None) -> Tuple[List[str], List[str]]:
        """Verify the uploaded LangSmith dataset matches the local file."""
        client, error = get_langsmith_client()
        if error:
            return [f"Upload check: skipped ({error})"], []

        # Find the uploaded dataset
        datasets, error = safe_api_call(lambda: list(client.list_datasets()))
        if error:
            return [f"Upload check: {error}"], []

        # Use run_id for precise matching if available, otherwise fall back to upload_prefix
        if run_id:
            search_pattern = f"{self.upload_prefix}{run_id}"
        else:
            search_pattern = self.upload_prefix
        matching = [d for d in datasets if d.name.startswith(search_pattern)]
        if not matching:
            return [], [f"Upload check: no dataset with prefix '{search_pattern}'"]

        recent = max(matching, key=lambda d: getattr(d, 'created_at', d.name))

        # Fetch examples from uploaded dataset
        try:
            uploaded_examples = list(client.list_examples(dataset_name=recent.name))
        except Exception as e:
            return [f"Upload check: couldn't fetch examples ({str(e)[:30]})"], []

        # Compare counts
        local_count = len(local_examples)
        uploaded_count = len(uploaded_examples)

        if uploaded_count != local_count:
            return [], [f"Upload check: {uploaded_count} uploaded vs {local_count} local"]

        # Compare trajectories
        # Build lookup of uploaded by trace_id or inputs
        uploaded_trajectories = set()
        for ex in uploaded_examples:
            traj = self._get_trajectory_from_langsmith_example(ex)
            if traj:
                uploaded_trajectories.add(tuple(traj))

        local_trajectories = set()
        for ex in local_examples:
            traj = self._get_trajectory(ex)
            if traj:
                local_trajectories.add(tuple(traj))

        if uploaded_trajectories == local_trajectories:
            return [f"Upload check: '{recent.name}' matches local ({uploaded_count} examples)"], []
        else:
            diff = len(local_trajectories - uploaded_trajectories)
            return [], [f"Upload check: {diff} trajectories differ from uploaded"]

    def _get_trajectory_from_langsmith_example(self, ex) -> List[str]:
        """Extract trajectory from a LangSmith example object."""
        outputs = getattr(ex, 'outputs', None) or {}
        if not isinstance(outputs, dict):
            return []

        for field in ["expected_trajectory", "trajectory", "tools"]:
            traj = outputs.get(field)
            if isinstance(traj, list):
                result = self._extract_tool_names(traj)
                return result if result else []
        return []

    def _trajectory_diff(self, expected: List[str], actual: List[str], query: str) -> str:
        """Generate a human-readable diff between trajectories."""
        query_short = (query[:20] + "...") if query and len(query) > 20 else (query or "?")

        if not actual:
            return f"'{query_short}': empty vs {len(expected)} tools"

        if len(actual) != len(expected):
            return f"'{query_short}': {len(actual)} tools vs expected {len(expected)}"

        # Find first difference
        for i, (a, e) in enumerate(zip(actual, expected)):
            if a != e:
                return f"'{query_short}': tool[{i}] '{a}' vs expected '{e}'"

        # Actual is longer
        if len(actual) > len(expected):
            return f"'{query_short}': extra tool '{actual[len(expected)]}'"

        return f"'{query_short}': order mismatch"
