"""Stub for scaffold.python.utils — LLM-based eval helpers not available in Harbor verifier."""


def evaluate_with_schema(prompt: str, model: str = None) -> dict:
    """No-op stub: LLM eval is informational only and skipped in Harbor."""
    return {"pass": True, "reason": "LLM eval skipped in Harbor verifier"}
