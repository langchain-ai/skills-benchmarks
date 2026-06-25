1. **Export successful traces first** - Use recent successful runs for baseline datasets
2. **Use time windows when exporting** - `--last-n-minutes 1440` for last 24 hours of data
3. **Verify exports have I/O** - Check that `inputs` and `outputs` are populated before processing
4. **Match depth to needs** - Depth 2 typically captures all main tool calls in LangGraph
5. **Iterative refinement** - Process small batches (5-20 traces) first, validate, then scale up
6. **Review before upload** - Inspect generated JSON before uploading to LangSmith
7. **Use the SDK for complex logic** - CLI is best for simple CRUD; SDK for programmatic dataset creation
