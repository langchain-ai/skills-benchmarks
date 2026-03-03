---
name: deep-agents-core-js
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---

<overview>
Deep Agents are an opinionated agent framework built on LangChain/LangGraph with built-in middleware:

- **Task Planning**: TodoListMiddleware for breaking down complex tasks
- **Context Management**: Filesystem tools with pluggable backends
- **Task Delegation**: SubAgent middleware for spawning specialized agents
- **Long-term Memory**: Persistent storage across threads via Store
- **Human-in-the-loop**: Approval workflows for sensitive operations
- **Skills**: On-demand loading of specialized capabilities

The agent harness provides these capabilities automatically - you configure, not implement.
</overview>

<when-to-use>

| Use Deep Agents When | Use LangChain's create_agent When |
|---------------------|-----------------------------------|
| Multi-step tasks requiring planning | Simple, single-purpose tasks |
| Large context requiring file management | Context fits in a single prompt |
| Need for specialized subagents | Single agent is sufficient |
| Persistent memory across sessions | Ephemeral, single-session work |

</when-to-use>

<middleware-selection>

| If you need to... | Middleware | Notes |
|------------------|------------|-------|
| Track complex tasks | TodoListMiddleware | Default enabled |
| Manage file context | FilesystemMiddleware | Configure backend |
| Delegate work | SubAgentMiddleware | Add custom subagents |
| Add human approval | HumanInTheLoopMiddleware | Requires checkpointer |
| Load skills | SkillsMiddleware | Provide skill directories |
| Access memory | MemoryMiddleware | Requires Store instance |

</middleware-selection>

<ex-basic-agent>
Create a basic deep agent with a custom tool and invoke it with a user message.
```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ city }) => `It is always sunny in ${city}`,
  { name: "get_weather", description: "Get weather for a city", schema: z.object({ city: z.string() }) }
);

const agent = await createDeepAgent({
  model: "claude-sonnet-4-5-20250929",
  tools: [getWeather],
  systemPrompt: "You are a helpful assistant"
});

const config = { configurable: { thread_id: "user-123" } };
const result = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in Tokyo?" }]
}, config);
```
</ex-basic-agent>

<ex-full-configuration>
Configure a deep agent with all available options including subagents, skills, and persistence.
```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver, InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  name: "my-assistant",
  model: "claude-sonnet-4-5-20250929",
  tools: [customTool1, customTool2],
  systemPrompt: "Custom instructions",
  subagents: [researchAgent, codeAgent],
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  interruptOn: { write_file: true },
  skills: ["./skills/"],
  checkpointer: new MemorySaver(),
  store: new InMemoryStore()
});
```
</ex-full-configuration>

<built-in-tools>
Every deep agent has access to:

1. **Planning**: `write_todos` - Track multi-step tasks
2. **Filesystem**: `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`
3. **Delegation**: `task` - Spawn specialized subagents
</built-in-tools>

---

## SKILL.md Format

<skill-md-format>
Skills use **progressive disclosure** - agents only load content when relevant.

### Directory Structure
```
skills/
└── my-skill/
    ├── SKILL.md        # Required: main skill file
    ├── examples.py     # Optional: supporting files
    └── templates/      # Optional: templates
```

### SKILL.md Format
```markdown
---
name: my-skill
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---

# Skill Name

## Overview
Brief explanation of the skill's purpose.

## When to Use
Conditions when this skill applies.

## Instructions
Step-by-step guidance for the agent.
```
</skill-md-format>

<skills-vs-memory>

| Skills | Memory (AGENTS.md) |
|--------|-------------------|
| On-demand loading | Always loaded at startup |
| Task-specific instructions | General preferences |
| Large documentation | Compact context |
| SKILL.md in directories | Single AGENTS.md file |

</skills-vs-memory>

<ex-skills-with-filesystem-backend>
Set up an agent with skills directory and filesystem backend for on-demand skill loading.
```typescript
import { createDeepAgent, FilesystemBackend } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"],
  checkpointer: new MemorySaver()
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Use the python-testing skill" }]
}, { configurable: { thread_id: "session-1" } });
```
</ex-skills-with-filesystem-backend>

<boundaries>
### What Agents CAN Configure

- Model selection and parameters
- Additional custom tools
- System prompt customization
- Backend storage strategy
- Which tools require approval
- Custom subagents with specialized tools

### What Agents CANNOT Configure

- Core middleware removal (TodoList, Filesystem, SubAgent always present)
- The write_todos, task, or filesystem tool names
- The SKILL.md frontmatter format
</boundaries>

<fix-checkpointer-for-interrupts>
Fix: Interrupts require a checkpointer to persist state during human-in-the-loop workflows.
```typescript
// WRONG: Will error
const agent = await createDeepAgent({ interruptOn: { write_file: true } });

// CORRECT: Checkpointer is required
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```
</fix-checkpointer-for-interrupts>

<fix-store-for-memory>
Fix: StoreBackend requires a Store instance for persistent memory across threads.
```typescript
// WRONG: Missing store
const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// CORRECT: Provide store
import { InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```
</fix-store-for-memory>

<fix-thread-id-for-conversations>
Fix: Use consistent thread_id to maintain conversation context across invocations.
```typescript
// WRONG: Each invocation is isolated
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] });
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] });

// CORRECT: Use consistent thread_id
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] }, config);
```
</fix-thread-id-for-conversations>

<fix-frontmatter-required>
```markdown
# WRONG: Missing frontmatter in SKILL.md
# My Skill
This is my skill...

# CORRECT: Include YAML frontmatter
---
name: my-skill
description: "INVOKE THIS SKILL when building ANY Deep Agents application. Covers create_deep_agent(), harness architecture, SKILL.md format, and configuration options. CRITICAL: Fixes for Store required for memory, backend configuration, and skill file structure."
---
# My Skill
This is my skill...
```
</fix-frontmatter-required>
