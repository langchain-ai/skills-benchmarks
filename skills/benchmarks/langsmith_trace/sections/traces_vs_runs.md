Use the `langsmith` CLI to query trace data.

**Understanding the difference is critical:**

- **Trace** = A complete execution tree (root run + all child runs). A trace represents one full agent invocation with all its LLM calls, tool calls, and nested operations.
- **Run** = A single node in the tree (one LLM call, one tool call, etc.)

**Generally, query traces first** — they provide complete context and preserve hierarchy needed for trajectory analysis and dataset generation.
