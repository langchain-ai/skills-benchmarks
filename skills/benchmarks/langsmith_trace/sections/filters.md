All commands support these filters (all AND together):

**Basic filters:**
- `--trace-ids abc,def` - Filter to specific traces
- `--limit N` - Max results
- `--project NAME` - Project name
- `--last-n-minutes N` - Time filter
- `--since TIMESTAMP` - Time filter (ISO format)
- `--error / --no-error` - Error status
- `--name PATTERN` - Name contains (case-insensitive)

**Performance filters:**
- `--min-latency SECONDS` - Minimum latency (e.g., `5` for >= 5s)
- `--max-latency SECONDS` - Maximum latency
- `--min-tokens N` - Minimum total tokens
- `--tags tag1,tag2` - Has any of these tags

**Advanced filter:**
- `--filter QUERY` - Raw LangSmith filter query for complex cases (feedback, metadata, etc.)

```bash
# Example: Filter by feedback score
langsmith trace list --filter 'and(eq(feedback_key, "correctness"), gte(feedback_score, 0.8))'
```
