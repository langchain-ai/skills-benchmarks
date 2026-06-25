Use the `langsmith` CLI to upload evaluators.

```bash
# List existing evaluators
langsmith evaluator list

# Upload JavaScript evaluator
langsmith evaluator upload my_evaluators.js \
  --name "Exact Match" \
  --function exactMatchEvaluator \
  --dataset "Skills: Final Response" \
  --replace

# Upload from TypeScript file
langsmith evaluator upload my_evaluators.ts \
  --name "Trajectory Match" \
  --function trajectoryEvaluator \
  --dataset "Skills: Trajectory" \
  --replace

# Delete evaluator
langsmith evaluator delete "Exact Match"
```

**IMPORTANT - Safety Prompts:**
- The CLI prompts for confirmation before destructive operations
- **NEVER use `--yes` flag unless the user explicitly requests it**
