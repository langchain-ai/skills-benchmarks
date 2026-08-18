```bash
# List all datasets
langsmith dataset list

# View dataset details
langsmith dataset get "Skills: Trajectory"

# List examples
langsmith example list --dataset "Skills: Trajectory" --limit 5

# Export from LangSmith to local
langsmith dataset export "Skills: Final Response" /tmp/exported.json --limit 100

# View experiments
langsmith experiment list --dataset "Skills: Trajectory"
```
