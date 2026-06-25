Human-in-the-Loop (HITL) middleware adds human oversight to tool calls. When the agent proposes a sensitive action, execution pauses for human decision:
- **approve**: Execute as-is
- **edit**: Modify before executing
- **reject**: Cancel with feedback

Requires LangGraph's persistence (checkpointer) to save state during interrupts.
