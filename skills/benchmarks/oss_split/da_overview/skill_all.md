---
name: Deep Agents Overview
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
| Use Deep Agents When | Use LangChain's create_agent/createAgent When |
|---------------------|-----------------------------------|
| Multi-step tasks requiring planning | Simple, single-purpose tasks |
| Large context requiring file management | Context fits in a single prompt |
| Need for specialized subagents | Single agent is sufficient |
| Persistent memory across sessions | Ephemeral, single-session work |
| CLI or coding assistant use cases | Simple API or chat applications |
</when-to-use>

<ex-basic-agent>
<python>
Create minimal agent with defaults:

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
</python>

<typescript>
Create minimal agent with defaults:

```typescript
import { createDeepAgent } from "deepagents";

// Minimal agent with default settings
const agent = await createDeepAgent({});

// Invoke the agent
const result = await agent.invoke({
  messages: [
    { role: "user", content: "What's the weather in Tokyo?" }
  ]
});
```
</typescript>
</ex-basic-agent>

<ex-custom-tools>
<python>
Add custom tools to agent:

```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It's always sunny in {city}!"

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
</python>

<typescript>
Add custom tools to agent:

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const getWeather = tool(
  ({ city }) => `It's always sunny in ${city}!`,
  {
    name: "get_weather",
    description: "Get the weather for a given city",
    schema: z.object({
      city: z.string(),
    }),
  }
);

const agent = await createDeepAgent({
  tools: [getWeather],
  systemPrompt: "You are a helpful weather assistant"
});

const result = await agent.invoke({
  messages: [
    { role: "user", content: "What's the weather in Tokyo?" }
  ]
});
```
</typescript>
</ex-custom-tools>

<ex-custom-model>
<python>
Specify model by string or instance:

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
</python>

<typescript>
Specify model by string or instance:

```typescript
import { createDeepAgent } from "deepagents";
import { ChatOpenAI } from "@langchain/openai";

// Use provider:model format
const agent = await createDeepAgent({
  model: "openai:gpt-4"
});

// Or pass a model instance
const model = new ChatOpenAI({ model: "gpt-4", temperature: 0 });
const agent2 = await createDeepAgent({
  model
});
```
</typescript>
</ex-custom-model>

<ex-harness-architecture>
<python>
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
</python>

<typescript>
Deep Agents automatically attach middleware when created.

Built-in middleware and tools included:

```typescript
import { createDeepAgent } from "deepagents";

// This agent automatically has:
// - TodoListMiddleware (task planning)
// - FilesystemMiddleware (file operations)
// - SubAgentMiddleware (task delegation)
// - SummarizationMiddleware (history management)
// - AnthropicPromptCachingMiddleware (caching)
// - PatchToolCallsMiddleware (tool call fixes)
const agent = await createDeepAgent({});
```

### Built-in Tools

Every deep agent has access to:

1. **Planning Tool**: `write_todos` - Track multi-step tasks
2. **Filesystem Tools**: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
3. **Subagent Tool**: `task` - Delegate work to specialized agents
</typescript>
</ex-harness-architecture>

<ex-config-options>
<python>
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
</python>

<typescript>
Full configuration with all options:

```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver, InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  name: "my-assistant",            // Optional: agent name
  model: "claude-sonnet-4-5-20250929",  // Model to use
  tools: [customTool1, customTool2],    // Additional tools
  systemPrompt: "Custom instructions",   // Custom system prompt
  middleware: [customMiddleware],        // Additional middleware
  subagents: [researchAgent, codeAgent], // Custom subagents
  backend: new FilesystemBackend({ rootDir: "." }),  // Storage backend
  interruptOn: { write_file: true },     // Human-in-the-loop config
  skills: ["/path/to/skills/"],     // Skill directories
  checkpointer: new MemorySaver(),  // Required for interrupts
  store: new InMemoryStore()        // For long-term memory
});
```
</typescript>
</ex-config-options>

<decision-table>
| If you need to... | Use this middleware | When to customize |
|------------------|-------------------|------------------|
| Track complex multi-step tasks | TodoListMiddleware / todoListMiddleware | Default works; customize prompt if needed |
| Manage file context | FilesystemMiddleware / createFilesystemMiddleware | Change backend or tool descriptions |
| Delegate specialized work | SubAgentMiddleware / createSubAgentMiddleware | Add custom subagents with specific tools |
| Prevent context overflow | SummarizationMiddleware / summarizationMiddleware | Default works; customize summarization strategy |
| Cache prompts (Anthropic) | AnthropicPromptCachingMiddleware / anthropicPromptCachingMiddleware | Default works automatically |
| Add human approval | HumanInTheLoopMiddleware / humanInTheLoopMiddleware | Configure which tools require approval |
| Load skills on-demand | SkillsMiddleware / skillsMiddleware | Provide skill directories |
| Access persistent memory | MemoryMiddleware / memoryMiddleware | Provide a Store instance |
</decision-table>

<boundaries>
**What Agents CAN Configure:**
- Model selection and parameters
- Additional custom tools
- System prompt customization
- Backend storage strategy
- Which tools require approval
- Custom subagents with specialized tools
- Skill directories and content
- Middleware order and configuration

**What Agents CANNOT Configure:**
- Core middleware removal (TodoList, Filesystem, SubAgent are always present)
- The write_todos, task, or filesystem tool names
- The fundamental tool-calling loop
- LangGraph's runtime execution model
- The Agent Skills protocol format
</boundaries>

<ex-gotcha-checkpointer>
<python>
Provide checkpointer when using HITL:

```python
# This will error if interrupt_on is set
agent = create_deep_agent(
    interrupt_on={"write_file": True}
)

# Checkpointer is required
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    interrupt_on={"write_file": True},
    checkpointer=MemorySaver()
)
```
</python>

<typescript>
Provide checkpointer when using HITL:

```typescript
// This will error if interruptOn is set
const agent = await createDeepAgent({
  interruptOn: { write_file: true }
});

// Checkpointer is required
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
</typescript>
</ex-gotcha-checkpointer>

<ex-gotcha-store>
<python>
Provide store when using StoreBackend:

```python
# StoreBackend needs a Store
from deepagents.backends import StoreBackend

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt)
)

# Pass a Store instance
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```
</python>

<typescript>
Provide store when using StoreBackend:

```typescript
// StoreBackend needs a Store
import { StoreBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// Pass a Store instance
import { InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```
</typescript>
</ex-gotcha-store>

<ex-gotcha-skills-backend>
<python>
Use FilesystemBackend for local skills:

```python
# Skills won't load without proper backend
agent = create_deep_agent(
    skills=["/path/to/skills/"]
)

# Use FilesystemBackend for local skills
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./skills/"]
)
```
</python>

<typescript>
Use FilesystemBackend for local skills:

```typescript
// Skills won't load without proper backend
const agent = await createDeepAgent({
  skills: ["/path/to/skills/"]
});

// Use FilesystemBackend for local skills
import { FilesystemBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```
</typescript>
</ex-gotcha-skills-backend>

<ex-gotcha-thread-id>
<python>
Use thread_id for conversation continuity:

```python
# Each invocation is isolated without thread_id
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]})
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]})

# Use consistent thread_id for conversation continuity
config = {"configurable": {"thread_id": "user-123"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi"}]}, config=config)
agent.invoke({"messages": [{"role": "user", "content": "What did I say?"}]}, config=config)
```
</python>

<typescript>
Use thread_id for conversation continuity:

```typescript
// Each invocation is isolated without thread_id
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] });
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] });

// Use consistent thread_id for conversation continuity
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] }, config);
```
</typescript>
</ex-gotcha-thread-id>

<ex-gotcha-default-model>
<python>
Set API key for default model:

```python
# Uses claude-sonnet-4-5-20250929 by default
agent = create_deep_agent()

# Requires ANTHROPIC_API_KEY environment variable
# Set OPENAI_API_KEY if using OpenAI models
import os
os.environ["ANTHROPIC_API_KEY"] = "your-key"
```
</python>

<typescript>
Set API key for default model:

```typescript
// Uses claude-sonnet-4-5-20250929 by default
const agent = await createDeepAgent({});

// Requires ANTHROPIC_API_KEY environment variable
// Set OPENAI_API_KEY if using OpenAI models
process.env.ANTHROPIC_API_KEY = "your-key";
```
</typescript>
</ex-gotcha-default-model>

<ex-gotcha-await>
<typescript>
Always await the async function:

```typescript
// Missing await
const agent = createDeepAgent({});

// createDeepAgent is async
const agent = await createDeepAgent({});
```
</typescript>
</ex-gotcha-await>

<links>
**Python:**
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Agent Harness Capabilities](https://docs.langchain.com/oss/python/deepagents/harness)
- [Customizing Deep Agents](https://docs.langchain.com/oss/python/deepagents/customization)
- [Deep Agents Quickstart](https://docs.langchain.com/oss/python/deepagents/quickstart)

**TypeScript:**
- [Deep Agents Overview](https://docs.langchain.com/oss/javascript/deepagents/overview)
- [Agent Harness Capabilities](https://docs.langchain.com/oss/javascript/deepagents/harness)
- [Customizing Deep Agents](https://docs.langchain.com/oss/javascript/deepagents/customization)
- [Deep Agents Quickstart](https://docs.langchain.com/oss/javascript/deepagents/quickstart)
</links>
