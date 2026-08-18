SubAgentMiddleware enables agents to delegate work to specialized subagents via the `task` tool. Subagents provide:
- **Context isolation**: Subagent work doesn't clutter main agent's context
- **Specialization**: Different tools/prompts for specific tasks
- **Token efficiency**: Large subtask context compressed into single result
- **Parallel execution**: Multiple subagents can run concurrently

**Default subagent**: "general-purpose" - automatically available with same tools/config as main agent.
