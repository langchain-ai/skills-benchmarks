Deep Agents automatically attach middleware when created.

Built-in middleware and tools included:

```python
from deepagents import create_deep_agent

# This agent automatically has:
# - TodoListMiddleware (task planning)
# - FilesystemMiddleware (file operations)
# - SubAgentMiddleware (task delegation)
# - SummarizationMiddleware (history management)
# - AnthropicPromptCachingMiddleware (caching)
# - PatchToolCallsMiddleware (tool call fixes)
agent = create_deep_agent()
```

### Built-in Tools

Every deep agent has access to:

1. **Planning Tool**: `write_todos` - Track multi-step tasks
2. **Filesystem Tools**: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
3. **Subagent Tool**: `task` - Delegate work to specialized agents
