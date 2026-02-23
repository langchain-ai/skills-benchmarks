"""Dataset validation utilities.

Validates dataset structure, trajectory accuracy, and LangSmith uploads.
"""

import json
from pathlib import Path


def get_field(obj: dict, *fields) -> any:
    """Get first matching field from object."""
    if not isinstance(obj, dict):
        return None
    for field in fields:
        if field in obj:
            return obj[field]
    return None


def get_nested_field(obj: dict, paths: list[str], fields: list[str]) -> any:
    """Get field from nested locations."""
    if not isinstance(obj, dict):
        return None
    # Try each path
    for path in paths:
        current = obj.get(path)
        if isinstance(current, dict):
            result = get_field(current, *fields)
            if result is not None:
                return result
    return None


def extract_examples(data) -> list:
    """Extract examples list from various dataset formats."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("examples") or data.get("data") or [data]
    return []


def read_json_file(path: Path) -> tuple[dict | list | None, str | None]:
    """Read JSON file, return (data, error)."""
    if not path.exists():
        return None, f"file not found: {path.name}"
    try:
        with open(path) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"
    except Exception as e:
        return None, str(e)


def validate_dataset_structure(
    test_dir: Path,
    outputs: dict,
    filename: str = "trajectory_dataset.json",
    min_examples: int = 1,
    dataset_type: str = "trajectory",
    required_fields: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate dataset file structure.

    Checks:
    - File exists and is valid JSON
    - Contains expected number of examples
    - Examples have required fields (inputs, outputs)
    - For trajectory type: examples have trajectory data

    Args:
        test_dir: Test working directory
        outputs: Outputs dict
        filename: Dataset filename
        min_examples: Minimum number of examples required
        dataset_type: "trajectory" or "single_step"
        required_fields: Override default required fields

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []
    required_fields = required_fields or ["inputs", "outputs"]

    data, error = read_json_file(test_dir / filename)
    if error:
        return [], [f"Dataset: {error}"]

    examples = extract_examples(data)
    if len(examples) < min_examples:
        return [f"Dataset: {filename} created"], [
            f"Dataset: {len(examples)} examples (need {min_examples})"
        ]

    passed.append(f"Dataset: {len(examples)} examples")

    # Check structure
    sample = examples[:10]
    valid_io = sum(1 for ex in sample if _has_io(ex, required_fields))
    if valid_io:
        passed.append(f"Dataset: {valid_io}/{len(sample)} have input/output")
    else:
        failed.append("Dataset: no input/output structure")

    if dataset_type == "trajectory":
        has_traj = sum(1 for ex in sample if _get_trajectory(ex))
        if has_traj:
            passed.append(f"Dataset: {has_traj}/{len(sample)} have trajectory")
        else:
            failed.append("Dataset: no trajectory data")

    return passed, failed


def _has_io(ex: dict, required_fields: list[str]) -> bool:
    """Check if example has required fields."""
    if not isinstance(ex, dict):
        return False
    # Support both 'inputs'/'input' and 'outputs'/'output'
    has_input = any(f in ex or f.rstrip("s") in ex for f in required_fields if "input" in f.lower())
    has_output = any(
        f in ex or f.rstrip("s") in ex for f in required_fields if "output" in f.lower()
    )
    return has_input and has_output


def _get_trajectory(ex: dict) -> list:
    """Extract trajectory data, accepting various field names."""
    if not isinstance(ex, dict):
        return []

    # Known trajectory field names
    fields = ["expected_trajectory", "trajectory", "expected_tools", "tool_calls", "tools"]

    # Check top-level
    traj = get_field(ex, *fields)
    if isinstance(traj, list):
        return traj

    # Check nested in outputs
    traj = get_nested_field(ex, ["outputs", "output"], fields)
    if isinstance(traj, list):
        return traj

    # Fallback: any list of strings in outputs
    outputs_val = get_field(ex, "outputs", "output")
    if isinstance(outputs_val, dict):
        for val in outputs_val.values():
            if isinstance(val, list) and val and isinstance(val[0], str):
                return val

    return []


def validate_dataset_upload(
    test_dir: Path,
    outputs: dict,
    filename: str = "trajectory_dataset.json",
    upload_prefix: str = "test-",
) -> tuple[list[str], list[str]]:
    """Verify dataset was uploaded to LangSmith and matches local file.

    Args:
        test_dir: Test working directory
        outputs: Outputs dict containing run_id
        filename: Local dataset filename
        upload_prefix: Prefix for dataset names in LangSmith

    Returns:
        (passed, failed) lists
    """
    from scaffold.python.validation.langsmith import get_langsmith_client, safe_api_call

    passed, failed = [], []

    # Read local file to get example count
    local_data, error = read_json_file(test_dir / filename)
    if error:
        return [], [f"Upload: local file error - {error}"]
    local_examples = extract_examples(local_data)
    local_count = len(local_examples)

    client, error = get_langsmith_client()
    if error:
        return [f"Upload: skipped ({error})"], []

    datasets, error = safe_api_call(lambda: list(client.list_datasets()))
    if error:
        return [f"Upload: {error}"], []

    # Use run_id for precise matching if available
    run_id = outputs.get("run_id") if outputs else None
    if run_id:
        search_pattern = f"{upload_prefix}{run_id}"
    else:
        search_pattern = upload_prefix

    matching = [d for d in datasets if d.name.startswith(search_pattern)]
    if not matching:
        return [], [f"Upload: no dataset with prefix '{search_pattern}'"]

    recent = max(matching, key=lambda d: getattr(d, "created_at", d.name))
    remote_count = getattr(recent, "example_count", None)

    passed.append(f"Upload: '{recent.name}' ({remote_count} examples)")

    # Verify counts match
    if remote_count is not None and remote_count != local_count:
        failed.append(f"Upload: count mismatch (local={local_count}, remote={remote_count})")
        return passed, failed

    # Fetch remote examples and compare content
    remote_examples, error = safe_api_call(
        lambda: list(client.list_examples(dataset_name=recent.name))
    )
    if error:
        passed.append(f"Upload: count matches ({local_count}), content check skipped")
        return passed, failed

    # Compare trajectories
    matches = 0
    for local_ex in local_examples:
        local_traj = _get_trajectory(local_ex)
        if not local_traj:
            continue

        # Find matching remote example by comparing trajectories
        for remote_ex in remote_examples:
            remote_outputs = getattr(remote_ex, "outputs", {}) or {}
            remote_traj = _get_trajectory({"outputs": remote_outputs})
            if _to_tool_names(local_traj) == _to_tool_names(remote_traj):
                matches += 1
                break

    if matches == local_count:
        passed.append(f"Upload: content verified ({matches}/{local_count} match)")
    elif matches > 0:
        failed.append(f"Upload: partial match ({matches}/{local_count} examples)")
    else:
        failed.append(f"Upload: content mismatch (0/{local_count} trajectories match)")

    return passed, failed


def validate_trajectory_accuracy(
    test_dir: Path,
    outputs: dict,
    filename: str = "trajectory_dataset.json",
    expected_filename: str = "expected_dataset.json",
    data_dir: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Validate dataset content matches ground truth.

    Compares actual dataset against expected ground truth to ensure
    trajectories are accurate.

    Args:
        test_dir: Test working directory
        outputs: Outputs dict (may contain trace_id_map for remapped IDs)
        filename: Actual dataset filename
        expected_filename: Ground truth filename
        data_dir: Directory containing expected file

    Returns:
        (passed, failed) lists
    """
    passed, failed = [], []
    data_dir = data_dir or (test_dir.parent / "data")

    # Load actual dataset
    actual_data, error = read_json_file(test_dir / filename)
    if error:
        return [], [f"Accuracy: {error}"]
    actual_examples = extract_examples(actual_data)

    if not actual_examples:
        return [], ["Accuracy: no examples in dataset"]

    # Load ground truth
    expected_data, error = read_json_file(data_dir / expected_filename)
    if error:
        return ["Accuracy: skipped (no ground truth)"], []
    expected_examples = (
        expected_data.get("examples", []) if isinstance(expected_data, dict) else expected_data
    )

    if not expected_examples:
        return ["Accuracy: skipped (empty ground truth)"], []

    # Get trace_id_map if available (maps old expected IDs to new actual IDs)
    trace_id_map = outputs.get("trace_id_map", {}) if outputs else {}

    # Compare trajectories
    matches, mismatches, missing = _compare_datasets(
        actual_examples, expected_examples, trace_id_map
    )
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

    return passed, failed


def _compare_datasets(
    actual: list[dict], expected: list[dict], trace_id_map: dict[str, str] = None
) -> tuple[int, list[str], list[str]]:
    """Compare actual dataset against expected ground truth.

    Args:
        actual: Actual dataset examples from Claude
        expected: Expected ground truth examples
        trace_id_map: Optional mapping from expected trace_id -> actual trace_id
                      (used when traces are re-uploaded with new IDs)

    Returns: (match_count, mismatch_details, missing_ids)
    """
    trace_id_map = trace_id_map or {}

    # Index actual by trace_id if available, otherwise by input
    def get_key(ex):
        trace_id = ex.get("trace_id") or ex.get("id")
        if trace_id:
            return str(trace_id)
        inputs = ex.get("inputs") or ex.get("input") or {}
        if isinstance(inputs, dict):
            messages = inputs.get("messages", [])
            if messages and isinstance(messages[0], dict):
                return messages[0].get("content", "")
            return inputs.get("query") or inputs.get("input") or str(inputs)
        return str(inputs)

    actual_by_key = {get_key(ex): ex for ex in actual if get_key(ex)}

    matches, mismatches, missing = 0, [], []

    for exp in expected:
        exp_key = get_key(exp)
        exp_traj = _get_trajectory(exp)
        if not exp_traj:
            continue

        # Use remapped ID if available (traces re-uploaded with new IDs)
        actual_key = trace_id_map.get(exp_key, exp_key)
        actual_ex = actual_by_key.get(actual_key)

        if not actual_ex:
            missing.append(exp_key[:30] if exp_key else "unknown")
            continue

        actual_traj = _get_trajectory(actual_ex)
        if _to_tool_names(actual_traj) == _to_tool_names(exp_traj):
            matches += 1
        else:
            mismatches.append(f"'{exp_key[:20]}...' trajectory mismatch")

    return matches, mismatches, missing


def _to_tool_names(traj: list) -> list[str]:
    """Convert trajectory items to tool name strings."""
    if not traj:
        return []
    names = []
    for item in traj:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            name = item.get("name") or item.get("tool") or item.get("function")
            if name:
                names.append(name)
    return names
