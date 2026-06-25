Complete workflow to create and upload an evaluator:

```bash
# 1. Create evaluators file
cat > evaluators.py <<'EOF'
def exact_match(run, example):
    """Check if output exactly matches expected."""
    output = run["outputs"].get("response", "").strip().lower()
    expected = example["outputs"].get("response", "").strip().lower()
    match = output == expected
    return {"exact_match": 1 if match else 0, "comment": f"Match: {match}"}
EOF

# 2. Upload to LangSmith
langsmith evaluator upload evaluators.py \
  --name "Exact Match" \
  --function exact_match \
  --dataset "Skills: Final Response" \
  --replace

# 3. Evaluator runs automatically on new dataset runs
```
