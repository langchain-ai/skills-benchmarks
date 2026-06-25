What Agents CAN Configure:
- **Model**: Any chat model (OpenAI, Anthropic, Google, etc.)
- **Tools**: Custom tools, built-in tools, dynamic tools
- **System Prompt**: Instructions for agent behavior
- **Middleware**: Human-in-the-loop, error handling, logging
- **Checkpointer**: Memory/persistence across conversations
- **Response Format**: Structured output schemas
- **Max Iterations**: Prevent infinite loops

What Agents CANNOT Configure:
- **Direct Graph Structure**: Use LangGraph directly for custom flows
- **Tool Execution Order**: Model decides which tools to call
- **Interrupt Model Decision**: Can only interrupt before tool execution
- **Multiple Models**: One agent = one model (use subagents for multiple)
