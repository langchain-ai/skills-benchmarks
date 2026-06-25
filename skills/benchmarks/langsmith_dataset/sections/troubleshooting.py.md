**Dataset upload fails:**
- Verify LANGSMITH_API_KEY is set
- Check JSON file is valid: array of objects with `inputs` key
- Dataset name must be unique, or delete existing first

**Empty dataset after upload:**
- Verify JSON file contains an array of objects with `inputs` key
- Check file isn't empty: `langsmith example list --dataset "Name"`

**No trajectory data in traces:**
- Tools might be at different depth - check trace hierarchy
- Verify tool calls exist in your exported JSONL files
- Use `langsmith trace get <id>` to inspect trace structure

**Too many single_step examples:**
- Sample N occurrences per trace to limit dataset size
- Reduces dataset size while maintaining diversity

**No RAG data:**
- RAG only matches `run_type="retriever"`
- For custom retriever names, filter by `name` instead

**Export has no data:**
- Ensure traces were exported with `--full` flag to include inputs/outputs
- Verify traces have both `inputs` and `outputs` populated
