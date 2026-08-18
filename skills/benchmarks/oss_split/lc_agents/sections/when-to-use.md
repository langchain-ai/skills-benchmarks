| Scenario | Use Agent? | Why |
|----------|-----------|-----|
| Need to call external APIs/databases | Yes | Agents can dynamically choose which tools to call |
| Multi-step task with decision points | Yes | Agent loop handles iterative reasoning |
| Simple prompt-response | No | Use a chat model directly |
| Predetermined workflow | No | Use LangGraph workflow instead |
| Need tool calling without iteration | Maybe | Consider using model.bind_tools() directly |
