Evaluators use `(run, example)` signature for LangSmith:

```python
def evaluator_name(run, example):
    """Evaluate using run/example dicts.

    Args:
        run: Dict with run["outputs"] containing agent outputs
        example: Dict with example["outputs"] containing expected outputs
    """
    # Field names (e.g. "response") must match your dataset schema
    agent_response = run["outputs"].get("response", "")
    expected = example["outputs"].get("response", "")

    return {
        "metric_name": 0.85,      # Metric name as key directly
        "comment": "Reason..."    # Optional explanation
    }
```
