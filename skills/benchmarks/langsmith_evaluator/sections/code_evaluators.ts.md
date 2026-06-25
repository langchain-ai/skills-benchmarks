### Exact Match

```javascript
function exactMatchEvaluator(run, example) {
  const output = (run.outputs?.response ?? "").trim().toLowerCase();
  const expected = (example.outputs?.response ?? "").trim().toLowerCase();
  const match = output === expected;
  return { exact_match: match ? 1 : 0, comment: `Match: ${match}` };
}
```

### Trajectory Validation

```javascript
function trajectoryEvaluator(run, example) {
  const trajectory = run.outputs?.expected_trajectory ?? [];
  const expected = example.outputs?.expected_trajectory ?? [];
  const exact = JSON.stringify(trajectory) === JSON.stringify(expected);
  const allTools = expected.every(tool => trajectory.includes(tool));
  return {
    trajectory_match: exact ? 1 : 0,
    comment: `Exact: ${exact}, All tools: ${allTools}`
  };
}
```

### Contains Keywords

```javascript
function containsKeywords(run, example) {
  const output = (run.outputs?.response ?? "").toLowerCase();
  const keywords = example.outputs?.required_keywords ?? [];
  const found = keywords.filter(kw => output.includes(kw.toLowerCase()));
  const score = found.length / keywords.length;
  return {
    keyword_coverage: score,
    comment: `Found ${found.length}/${keywords.length} keywords`
  };
}
```
