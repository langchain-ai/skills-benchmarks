### Exact Match

```python
def exact_match_evaluator(run, example):
    output = run["outputs"].get("response", "").strip().lower()
    expected = example["outputs"].get("response", "").strip().lower()
    match = output == expected
    return {"exact_match": 1 if match else 0, "comment": f"Match: {match}"}
```

### Trajectory Validation

```python
def trajectory_evaluator(run, example):
    trajectory = run["outputs"].get("expected_trajectory", [])
    expected = example["outputs"].get("expected_trajectory", [])
    exact = trajectory == expected
    all_tools = set(expected).issubset(set(trajectory))
    return {
        "trajectory_match": 1 if exact else 0,
        "comment": f"Exact: {exact}, All tools: {all_tools}"
    }
```
