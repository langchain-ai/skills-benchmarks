"""scaffold.python.utils for Harbor verifier — real LangSmith client, stubbed Docker."""

import json
import os
from pathlib import Path


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """No-op stub: LLM eval is informational only and skipped in Harbor."""
    return {"pass": True, "reason": "LLM eval skipped in Harbor verifier"}


def run_python_in_docker(*args, **kwargs):
    """Stub: Docker-in-Docker not available in Harbor verifier."""
    return True, ""


def run_node_in_docker(*args, **kwargs):
    """Stub: Docker-in-Docker not available in Harbor verifier."""
    return True, ""


def check_docker_available() -> bool:
    return False


def get_langsmith_client():
    """Return (Client, None) or (None, error_str)."""
    try:
        from langsmith import Client
        api_key = os.environ.get("LANGSMITH_API_KEY")
        if not api_key:
            return None, "LANGSMITH_API_KEY not set"
        return Client(api_key=api_key), None
    except Exception as e:
        return None, str(e)


def safe_api_call(func, skip_msg: str = "skipped"):
    """Run API call, return (result, error_msg)."""
    try:
        return func(), None
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "rate limit" in msg:
            return None, f"{skip_msg} (rate limited)"
        return None, f"{skip_msg}: {str(e)[:80]}"


def read_json_file(path: Path):
    """Read JSON file. Returns (data, None) or (None, error)."""
    if not path.exists():
        return None, f"file not found: {path.name}"
    try:
        with open(path) as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"
    except Exception as e:
        return None, str(e)


def get_field(obj, *keys, default=None):
    """Get first matching field from dict."""
    if not isinstance(obj, dict):
        return default
    for key in keys:
        if key in obj:
            return obj[key]
    return default


def get_nested_field(obj: dict, outer_keys: list, inner_keys: list, default=None):
    """Get field from nested dict."""
    outer = get_field(obj, *outer_keys) or {}
    return get_field(outer, *inner_keys, default=default) if isinstance(outer, dict) else default


def normalize_score(score) -> float:
    if isinstance(score, bool):
        return 1.0 if score else 0.0
    if isinstance(score, (int, float)) and score > 1:
        return score / 100.0
    return float(score) if score is not None else 0.0
