What You CAN Configure:
- **Which tools are available**: bind_tools([tool1, tool2]) / bindTools([tool1, tool2])
- **Tool choice strategy**: auto, any, specific tool, none
- **Tool execution logic**: Custom error handling, retries
- **Tool parameters**: Via tool schema and type hints
- **Multiple tool calls**: Models can call multiple tools

What You CANNOT Configure:
- **Force model reasoning**: Can't control how model decides
- **Tool call order**: Model decides (can call in parallel)
- **Prevent all tool calls**: Use tool_choice or don't bind tools
- **Modify tool call after model generates**: Tool calls are immutable
