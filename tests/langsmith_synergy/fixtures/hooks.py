"""LangSmith Synergy test hooks.

Pre/post run hooks for generating traces and cleaning up datasets.
The actual run_experiment() lives in scaffold.
"""

import os
import time
from pathlib import Path
from typing import List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scaffold import build_docker_image, run_in_docker
from tests.langsmith_synergy.fixtures.ground_truth import generate_all_ground_truth

ENVIRONMENT_DIR = Path(__file__).parent / "environment"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def generate_traces(verbose: bool = True) -> bool:
    """Run sql_agent.py to generate traces in LangSmith."""
    if verbose:
        print("\n" + "=" * 60)
        print("PRE-GENERATING TRACES")
        print("=" * 60)

    image_name = build_docker_image(ENVIRONMENT_DIR, verbose=verbose)
    if not image_name:
        print("ERROR: Failed to build Docker image")
        return False

    try:
        result = run_in_docker(
            FIXTURES_DIR,
            ["python", "sql_agent.py"],
            timeout=300,
            image_name=image_name,
        )
        success = result.returncode == 0
        if verbose:
            if success:
                print("SUCCESS: Traces generated")
            else:
                print("WARNING: sql_agent.py returned errors")
            print("=" * 60 + "\n")
        time.sleep(2)
        return success
    except Exception as e:
        if verbose:
            print(f"ERROR: Failed to run sql_agent.py: {e}")
        return False


def generate_ground_truth(base_dir: Path, verbose: bool = True) -> None:
    """Generate ground truth ONCE for all treatments."""
    if verbose:
        print("\n" + "=" * 60)
        print("GENERATING GROUND TRUTH")
        print("=" * 60)

    gt_dir = base_dir / "ground_truth"
    gt_dir.mkdir(parents=True, exist_ok=True)
    gt_data = generate_all_ground_truth(gt_dir)

    if verbose:
        trace_count = gt_data.get("trace_count", 0)
        example_count = gt_data.get("dataset_example_count", 0)
        print(f"Generated: {trace_count} traces, {example_count} examples")
        print("=" * 60 + "\n")


def cleanup_langsmith_datasets(run_ids: List[str] = None, verbose: bool = True) -> int:
    """Delete LangSmith datasets created during the experiment."""
    if not run_ids:
        return 0

    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass

    api_key = os.environ.get("LANGSMITH_API_KEY")
    if not api_key:
        return 0

    try:
        from langsmith import Client
        client = Client(api_key=api_key)
        datasets = list(client.list_datasets())
        prefixes = [f"test-{rid}" for rid in run_ids]
        test_datasets = [d for d in datasets if any(d.name.startswith(p) for p in prefixes)]

        deleted = 0
        for dataset in test_datasets:
            try:
                client.delete_dataset(dataset_id=dataset.id)
                deleted += 1
            except Exception:
                pass
        return deleted
    except Exception:
        return 0
