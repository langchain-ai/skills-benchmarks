# Fix: Data Processing Pipeline

We have a LangGraph pipeline in `broken_pipeline.py` that processes tasks in parallel using the Send API. Users are reporting multiple problems:

- "The pipeline crashes when I give it multiple tasks"
- "Even when it works, I only get one result back instead of all of them"
- "There's no way to review results before they're finalized"
- "When I try to resume after reviewing, it starts over from scratch"

## Current Behavior

```
run_pipeline(["task_a", "task_b", "task_c"])
# Results: ["processed:task_a"]   <-- Only one result! Should be three
# Summary: "Pipeline complete: 1 tasks processed"
```

## Expected Behavior

```
run_pipeline(["task_a", "task_b", "task_c"])
# Results: ["processed:task_a", "processed:task_b", "processed:task_c"]
# Summary: "Pipeline complete: 3 tasks processed"
# Also: pipeline should pause for review before finalizing
```

## Your Task

Review the pipeline code and fix all issues. The node logic (process_task, summarize) is correct — focus on how tasks are distributed, how results are collected, and how the review step works.

After your fixes:
1. All tasks should be processed, not just the first one
2. Results from parallel workers should accumulate correctly
3. The pipeline should pause for human review before finalizing
4. Resuming after review should continue where it left off, not restart
