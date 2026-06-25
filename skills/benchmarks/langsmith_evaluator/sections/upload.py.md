Use the `langsmith` CLI to upload evaluators.

```bash
# List existing evaluators
langsmith evaluator list

# Upload evaluator
langsmith evaluator upload my_evaluators.py \
  --name "Trajectory Match" \
  --function trajectory_match \
  --dataset "Skills: Trajectory" \
  --replace

# Delete evaluator
langsmith evaluator delete "Trajectory Match"
```

**IMPORTANT - Safety Prompts:**
- The CLI prompts for confirmation before destructive operations
- **NEVER use `--yes` flag unless the user explicitly requests it**
