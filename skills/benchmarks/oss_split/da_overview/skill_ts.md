---
name: Deep Agents Overview (TypeScript)
description: [Deep Agents] Understanding Deep Agents framework - what they are, how to create them with create_deep_agent/createDeepAgent, and the agent harness architecture with built-in middleware for planning, filesystems, and subagents.
---

# deepagents-overview (JavaScript/TypeScript)

## What are Deep Agents?

Deep Agents are an opinionated agent framework built on top of LangChain and LangGraph, designed for complex, multi-step tasks. They come "batteries included" with built-in capabilities:

- **Task Planning**: TodoListMiddleware for breaking down complex tasks
- **Context Management**: Filesystem tools with pluggable backends
- **Task Delegation**: SubAgent middleware for spawning specialized agents
- **Long-term Memory**: Persistent storage across threads via Store
- **Human-in-the-loop**: Approval workflows for sensitive operations

Deep Agents use an "agent harness" architecture - the same core tool-calling loop as other frameworks, but with pre-configured middleware and tools.

## When to Use Deep Agents

| Use Deep Agents When | Use LangChain's createAgent When |
|---------------------|-----------------------------------|
| Multi-step tasks requiring planning | Simple, single-purpose tasks |
| Large context requiring file management | Context fits in a single prompt |
| Need for specialized subagents | Single agent is sufficient |
| Persistent memory across sessions | Ephemeral, single-session work |
| CLI or coding assistant use cases | Simple API or chat applications |

## Creating a Deep Agent

### Basic Agent Creation

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

### Agent with Custom Tools

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

### Agent with Custom Model

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

## The Agent Harness Architecture

Deep Agents automatically attach middleware when created:

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

## Configuration Options

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

## Decision Table: Which Middleware to Customize

| If you need to... | Use this middleware | When to customize |
|------------------|-------------------|------------------|
| Track complex multi-step tasks | todoListMiddleware | Default works; customize prompt if needed |
| Manage file context | createFilesystemMiddleware | Change backend or tool descriptions |
| Delegate specialized work | createSubAgentMiddleware | Add custom subagents with specific tools |
| Prevent context overflow | summarizationMiddleware | Default works; customize summarization strategy |
| Cache prompts (Anthropic) | anthropicPromptCachingMiddleware | Default works automatically |
| Add human approval | humanInTheLoopMiddleware | Configure which tools require approval |
| Load skills on-demand | skillsMiddleware | Provide skill directories |
| Access persistent memory | memoryMiddleware | Provide a Store instance |

## Boundaries

### What Agents CAN Configure

✅ Model selection and parameters
✅ Additional custom tools
✅ System prompt customization
✅ Backend storage strategy
✅ Which tools require approval
✅ Custom subagents with specialized tools
✅ Skill directories and content
✅ Middleware order and configuration

### What Agents CANNOT Configure

❌ Core middleware removal (TodoList, Filesystem, SubAgent are always present)
❌ The write_todos, task, or filesystem tool names
❌ The fundamental tool-calling loop
❌ LangGraph's runtime execution model
❌ The Agent Skills protocol format

## Gotchas

### 1. Checkpointer Required for Interrupts

```typescript
// ❌ This will error if interruptOn is set
const agent = await createDeepAgent({
  interruptOn: { write_file: true }
});

// ✅ Checkpointer is required
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  interruptOn: { write_file: true },
  checkpointer: new MemorySaver()
});
```

### 2. Store Required for Persistent Memory

```typescript
// ❌ StoreBackend needs a Store
import { StoreBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config)
});

// ✅ Pass a Store instance
import { InMemoryStore } from "@langchain/langgraph";

const agent = await createDeepAgent({
  backend: (config) => new StoreBackend(config),
  store: new InMemoryStore()
});
```

### 3. Skills Require Backend Setup

```typescript
// ❌ Skills won't load without proper backend
const agent = await createDeepAgent({
  skills: ["/path/to/skills/"]
});

// ✅ Use FilesystemBackend for local skills
import { FilesystemBackend } from "deepagents";

const agent = await createDeepAgent({
  backend: new FilesystemBackend({ rootDir: ".", virtualMode: true }),
  skills: ["./skills/"]
});
```

### 4. Thread ID Required for Stateful Conversations

```typescript
// ❌ Each invocation is isolated without thread_id
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] });
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] });

// ✅ Use consistent thread_id for conversation continuity
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "Hi" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What did I say?" }] }, config);
```

### 5. Default Model is Anthropic Claude

```typescript
// Uses claude-sonnet-4-5-20250929 by default
const agent = await createDeepAgent({});

// Requires ANTHROPIC_API_KEY environment variable
// Set OPENAI_API_KEY if using OpenAI models
process.env.ANTHROPIC_API_KEY = "your-key";
```

### 6. Await createDeepAgent

```typescript
// ❌ Missing await
const agent = createDeepAgent({});

// ✅ createDeepAgent is async
const agent = await createDeepAgent({});
```

## Full Documentation

- [Deep Agents Overview](https://docs.langchain.com/oss/javascript/deepagents/overview)
- [Agent Harness Capabilities](https://docs.langchain.com/oss/javascript/deepagents/harness)
- [Customizing Deep Agents](https://docs.langchain.com/oss/javascript/deepagents/customization)
- [Deep Agents Quickstart](https://docs.langchain.com/oss/javascript/deepagents/quickstart)
