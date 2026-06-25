JavaScript evaluators use `(run, example)` signature for offline (dataset) evaluations:

```javascript
function evaluatorName(run, example) {
  // Field names (e.g. "response") must match your dataset schema
  const agentResponse = run.outputs?.response ?? "";
  const expected = example.outputs?.response ?? "";

  const score = agentResponse === expected ? 1 : 0;
  return { metric_name: score, comment: "Reason..." };
}
```

For online evaluators (no dataset), only `run` is available:

```javascript
function onlineEvaluator(run) {
  const output = run.outputs?.response ?? "";
  const score = output.length > 0 ? 1 : 0;
  return { has_response: score };
}
```
