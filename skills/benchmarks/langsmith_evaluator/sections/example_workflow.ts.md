Complete workflow to create and upload a JavaScript evaluator:

```bash
# 1. Create evaluators file
cat > evaluators.js <<'EOF'
function exactMatch(run, example) {
  // Check if output exactly matches expected
  const output = (run.outputs?.response ?? "").trim().toLowerCase();
  const expected = (example.outputs?.response ?? "").trim().toLowerCase();
  const match = output === expected;
  return { exact_match: match ? 1 : 0, comment: `Match: ${match}` };
}
EOF

# 2. Upload to LangSmith
langsmith evaluator upload evaluators.js \
  --name "Exact Match" \
  --function exactMatch \
  --dataset "Skills: Final Response" \
  --replace

# 3. Evaluator runs automatically on new dataset runs
```
