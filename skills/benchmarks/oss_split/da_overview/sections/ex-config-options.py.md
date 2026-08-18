Full configuration with all options:

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    name="my-assistant",           # Optional: agent name
    model="claude-sonnet-4-5-20250929",  # Model to use
    tools=[custom_tool1, custom_tool2],  # Additional tools
    system_prompt="Custom instructions",  # Custom system prompt
    middleware=[custom_middleware],       # Additional middleware
    subagents=[research_agent, code_agent],  # Custom subagents
    backend=FilesystemBackend(root_dir="."),  # Storage backend
    interrupt_on={"write_file": True},  # Human-in-the-loop config
    skills=["/path/to/skills/"],   # Skill directories
    checkpointer=MemorySaver(),    # Required for interrupts
    store=InMemoryStore()          # For long-term memory
)
```
