---
name: Deep Agents Overview (Python)
description: "[Deep Agents] Understanding Deep Agents framework - what they are, how to create them with create_deep_agent/createDeepAgent, and the agent harness architecture with built-in middleware for planning, filesystems, and subagents."
---

<overview>
Deep Agents are an opinionated agent framework built on top of LangChain and LangGraph, designed for complex, multi-step tasks. They come "batteries included" with built-in capabilities:

- **Task Planning**: TodoListMiddleware for breaking down complex tasks
- **Context Management**: Filesystem tools with pluggable backends
- **Task Delegation**: SubAgent middleware for spawning specialized agents
- **Long-term Memory**: Persistent storage across threads via Store
- **Human-in-the-loop**: Approval workflows for sensitive operations

Deep Agents use an "agent harness" architecture - the same core tool-calling loop as other frameworks, but with pre-configured middleware and tools.
</overview>

<when-to-use>

| Use Deep Agents When | Use LangChain's create_agent When |
|---------------------|-----------------------------------|
| Multi-step tasks requiring planning | Simple, single-purpose tasks |
| Large context requiring file management | Context fits in a single prompt |
| Need for specialized subagents | Single agent is sufficient |
| Persistent memory across sessions | Ephemeral, single-session work |
| CLI or coding assistant use cases | Simple API or chat applications |

</when-to-use>

<ex-basic-agent>
```python
from deepagents import create_deep_agent

# Minimal agent with default settings
agent = create_deep_agent()

# Invoke the agent
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What's the weather in Tokyo?"}
    ]
})
```
</ex-basic-agent>

<ex-custom-tools>
```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It is always sunny in {city}"

agent = create_deep_agent(
    tools=[get_weather],
    system_prompt="You are a helpful weather assistant"
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What's the weather in Tokyo?"}
    ]
})
```
</ex-custom-tools>

<ex-custom-model>
```python
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

# Use provider:model format
agent = create_deep_agent(
    model="openai:gpt-4"
)

# Or pass a model instance
model = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_deep_agent(
    model=model
)
```
</ex-custom-model>

<agent-harness-architecture>
Deep Agents automatically attach middleware when created:

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
</agent-harness-architecture>

<ex-configuration-options>
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
</ex-configuration-options>

<middleware-selection>

| If you need to... | Use this middleware | When to customize |
|------------------|-------------------|------------------|
| Track complex multi-step tasks | TodoListMiddleware | Default works; customize prompt if needed |
| Manage file context | FilesystemMiddleware | Change backend or tool descriptions |
| Delegate specialized work | SubAgentMiddleware | Add custom subagents with specific tools |
| Prevent context overflow | SummarizationMiddleware | Default works; customize summarization strategy |
| Cache prompts (Anthropic) | AnthropicPromptCachingMiddleware | Default works automatically |
| Add human approval | HumanInTheLoopMiddleware | Configure which tools require approval |
| Load skills on-demand | SkillsMiddleware | Provide skill directories |
| Access persistent memory | MemoryMiddleware | Provide a Store instance |

</middleware-selection>

<boundaries>
### What Agents CAN Configure

- Model selection and parameters
- Additional custom tools
- System prompt customization
- Backend storage strategy
- Which tools require approval
- Custom subagents with specialized tools
- Skill directories and content
- Middleware order and configuration

### What Agents CANNOT Configure

- Core middleware removal (TodoList, Filesystem, SubAgent are always present)
- The write_todos, task, or filesystem tool names
- The fundamental tool-calling loop
- LangGraph's runtime execution model
- The Agent Skills protocol format
</boundaries>

<fix-checkpointer-for-interrupts>
```python
# WRONG: This will error if interrupt_on is set
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# CORRECT: Checkpointer is required
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
</fix-checkpointer-for-interrupts>

<fix-store-for-memory>
```python
# WRONG: StoreBackend needs a Store
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# CORRECT: Pass a Store instance
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
</fix-store-for-memory>

<fix-backend-for-skills>
```python
# WRONG: Skills won't load without proper backend
agent = create_deep_agent(
    skills=["/path/to/skills/"]
)

# CORRECT: Use FilesystemBackend for local skills
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
</fix-backend-for-skills>

<fix-thread-id-for-conversations>
```python
# WRONG: Each invocation is isolated without thread_id
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]})
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]})

# CORRECT: Use consistent thread_id for conversation continuity
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]}, config=config)
```
</fix-thread-id-for-conversations>

<fix-default-model>
```python
# Uses claude-sonnet-4-5-20250929 by default
agent = create_deep_agent()

# Requires ANTHROPIC_API_KEY environment variable
# Set OPENAI_API_KEY if using OpenAI models
import os
os.environ["ANTHROPIC_API_KEY"] = "your-key"
```
</fix-default-model>

<links>
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Agent Harness Capabilities](https://docs.langchain.com/oss/python/deepagents/harness)
- [Customizing Deep Agents](https://docs.langchain.com/oss/python/deepagents/customization)
- [Deep Agents Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)
</links>
