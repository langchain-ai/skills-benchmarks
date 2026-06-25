| Need | Edge Type | When to Use |
|------|-----------|-------------|
| Always go to same node | `add_edge()` / `addEdge()` | Fixed, deterministic flow |
| Route based on state | `add_conditional_edges()` / `addConditionalEdges()` | Dynamic branching logic |
| Fan-out to multiple nodes | `Send` API | Map-reduce, parallel execution |
| Update state AND route | `Command` | Combine logic in single node |
