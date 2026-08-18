```bash
# List all datasets
langsmith dataset list

# View dataset details
langsmith dataset get "Skills: Trajectory"

# List examples in a dataset
langsmith example list --dataset "Skills: Trajectory" --limit 5

# Export to local file
langsmith dataset export "Skills: Final Response" /tmp/exported.json --limit 100

# Delete a dataset
langsmith dataset delete "Old Dataset"
```
