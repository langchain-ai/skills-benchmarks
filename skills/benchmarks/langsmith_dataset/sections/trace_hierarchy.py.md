Traces have depth levels based on parent-child relationships:

```
Depth 0: Root agent (e.g., "LangGraph")
  +-- Depth 1: Middleware/chains (model, tools, SummarizationMiddleware)
  |     +-- Depth 2: Tool calls (sql_db_query, retriever, etc.)
  |     +-- Depth 2: LLM calls (ChatOpenAI, ChatAnthropic)
  +-- Depth 3+: Nested subagent calls
```
