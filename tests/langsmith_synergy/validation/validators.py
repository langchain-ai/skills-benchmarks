"""Validators for LangSmith Synergy experiment."""

import ast
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scaffold import (
    Validator,
    get_field,
    get_nested_field,
    read_json_file,
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

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
        passed, failed = [], []

        data, error = read_json_file(test_dir / self.filename)
        if error:
            return [], [f"Dataset: {error}"]

        examples = extract_examples(data)
        if len(examples) < self.min_examples:
            return [f"Dataset: {self.filename} created"], [
                f"Dataset: {len(examples)} examples (need {self.min_examples})"
            ]

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
            run_id = outputs.get("run_id") if outputs else None
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

    def _verify_upload(self, run_id: str = None) -> tuple[list[str], list[str]]:
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

        recent = max(matching, key=lambda d: getattr(d, "created_at", d.name))
        count = getattr(recent, "example_count", "?")
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

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
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
            run_id = outputs.get("run_id") if outputs else None
            up, uf = self._verify_upload(run_id)
            passed.extend(up)
            failed.extend(uf)

        return passed, failed

    def _find_evaluator_function(self, content: str) -> tuple[str, str]:
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

    def _run_tests(self, test_dir: Path, func_name: str) -> tuple[list[str], list[str]]:
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
                test_dir, "_eval_runner.py", timeout=60, args=args
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

            return (
                (["Evaluator: executed"], []) if success else ([], ["Evaluator: execution failed"])
            )
        except Exception as e:
            return [], [f"Evaluator: {str(e)[:50]}"]
        finally:
            runner_dst.unlink(missing_ok=True)

    def _verify_upload(self, run_id: str = None) -> tuple[list[str], list[str]]:
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
                return [f"Upload: '{name}' found"], [
                    f"Upload: linked to '{dataset_name}' (expected prefix '{search_pattern}')"
                ]

            return [f"Upload: '{name}' found (no dataset)"], []

        except Exception as e:
            return [f"Upload: skipped ({str(e)[:30]})"], []


class SkillScriptValidator(Validator):
    """Validate that skill scripts were used in commands."""

    def __init__(self, script_patterns: dict[str, str], require_scripts: bool = False):
        self.script_patterns = script_patterns
        self.require_scripts = require_scripts

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
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

    def validate(
        self, events: dict, test_dir: Path, outputs: dict = None
    ) -> tuple[list[str], list[str]]:
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
            return ["Accuracy: skipped (no ground truth)"], []
        expected_examples = expected_data.get("examples", [])

        if not expected_examples:
            return ["Accuracy: skipped (empty ground truth)"], []

        # Match actual examples against expected - each expected must appear exactly once
        # Use trace_id_map to remap expected IDs to actual IDs (since IDs are regenerated on upload)
        trace_id_map = outputs.get("trace_id_map", {}) if outputs else {}
        matches, mismatches, missing = self._compare_datasets(
            actual_examples, expected_examples, trace_id_map
        )

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
            run_id = outputs.get("run_id") if outputs else None
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
            # Check for messages array (LangSmith trace format)
            messages = inputs.get("messages", [])
            if messages and isinstance(messages, list) and isinstance(messages[0], dict):
                return messages[0].get("content", "")
            return inputs.get("query") or inputs.get("input") or inputs.get("question") or ""
        return ""

    def _get_trajectory(self, ex: dict) -> list[str]:
        """Extract tool name list from example. Returns None if not found or invalid."""
        if not isinstance(ex, dict):
            return None

        # Look in outputs.expected_trajectory, outputs.trajectory, etc.
        outputs = ex.get("outputs") or ex.get("output") or {}
        if isinstance(outputs, dict):
            for field in ["expected_trajectory", "trajectory", "tools", "tool_calls"]:
                traj = outputs.get(field)
                if isinstance(traj, list):
                    return self._to_tool_names(traj)
        return None

    def _to_tool_names(self, traj: list) -> list[str]:
        """Convert trajectory items to tool name strings."""
        names = []
        for item in traj:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict) and "inputs" not in item:  # Simple dict, not run object
                name = item.get("name") or item.get("tool") or item.get("function")
                if name:
                    names.append(name)
                else:
                    return None
            else:
                return None
        return names

    def _get_trace_id(self, ex: dict) -> str:
        """Extract trace_id from example."""
        return str(ex.get("trace_id") or ex.get("id") or "")

    def _compare_datasets(
        self, actual: list[dict], expected: list[dict], trace_id_map: dict[str, str] = None
    ) -> tuple[int, list[str], list[str]]:
        """Compare actual dataset against expected ground truth by trace_id.

        Args:
            trace_id_map: Mapping of original -> new trace_id (for re-uploaded traces)

        Returns: (match_count, mismatch_details, missing_trace_ids)
        """
        trace_id_map = trace_id_map or {}

        # Index actual examples by trace_id
        actual_by_id = {self._get_trace_id(ex): ex for ex in actual if self._get_trace_id(ex)}

        matches, mismatches, missing = 0, [], []

        for exp in expected:
            exp_id = self._get_trace_id(exp)
            exp_traj = self._get_trajectory(exp)
            if not exp_traj:
                continue

            # Look up using remapped ID
            actual_id = trace_id_map.get(exp_id, exp_id)
            actual_ex = actual_by_id.get(actual_id)

            if not actual_ex:
                missing.append(exp_id or "unknown")
                continue

            actual_traj = self._get_trajectory(actual_ex)
            if actual_traj == exp_traj:
                matches += 1
            else:
                query = self._get_input_query(exp)
                mismatches.append(self._trajectory_diff(exp_traj, actual_traj, query))

        return matches, mismatches, missing

    def _verify_upload_matches(
        self, local_examples: list[dict], run_id: str = None
    ) -> tuple[list[str], list[str]]:
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

        recent = max(matching, key=lambda d: getattr(d, "created_at", d.name))

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

    def _get_trajectory_from_langsmith_example(self, ex) -> list[str]:
        """Extract trajectory from a LangSmith example object."""
        outputs = getattr(ex, "outputs", None) or {}
        if not isinstance(outputs, dict):
            return []

        for field in ["expected_trajectory", "trajectory", "tools"]:
            traj = outputs.get(field)
            if isinstance(traj, list):
                return self._to_tool_names(traj) or []
        return []

    def _trajectory_diff(self, expected: list[str], actual: list[str], query: str) -> str:
        """Generate human-readable diff between trajectories."""
        q = (query[:20] + "...") if query and len(query) > 20 else (query or "?")

        if not actual:
            return f"'{q}': empty vs {len(expected)} tools"

        # Find first difference
        for i, (a, e) in enumerate(zip(actual, expected, strict=False)):
            if a != e:
                return f"'{q}': tool[{i}] '{a}' vs expected '{e}'"

        if len(actual) != len(expected):
            return f"'{q}': {len(actual)} tools vs expected {len(expected)}"

        return f"'{q}': order mismatch"
