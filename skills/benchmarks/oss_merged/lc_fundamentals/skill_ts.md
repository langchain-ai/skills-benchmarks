---
name: langchain-fundamentals
description: Create LangChain agents with createAgent, define tools, and use middleware for human-in-the-loop and error handling
---

<oneliner>
Build production agents using `create_agent()`, middleware patterns, and the `@tool` decorator / `tool()` function. When creating LangChain agents, you MUST use create_agent(), with middleware for custom flows. All other alternatives are outdated.
</oneliner>

<quick_start>
**Modern LangChain Agent Pattern:**

```typescript
import { createAgent } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const search = tool(
  async ({ query }) => {
    return `Results for: ${query}`;
  },
  {
    name: "search",
    description: "Search for information on the web.",
    schema: z.object({
      query: z.string().describe("The search query"),
    }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  systemPrompt: "You are a helpful assistant.",
});

const result = await agent.invoke({ messages: [["user", "Search for LangChain docs"]] });
```

**Key Imports:**
- `import { createAgent } from "langchain"` - Agent factory
- `import { tool } from "@langchain/core/tools"` - Tool function
- `import { humanInTheLoopMiddleware } from "langchain"` - Human approval
</quick_start>

<create_agent>
## Creating Agents with createAgent

`createAgent()` is the recommended way to build agents. It handles the agent loop, tool execution, and state management.

### Basic Agent

```typescript
import { createAgent } from "langchain";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  async ({ location }) => {
    return `Weather in ${location}: Sunny, 72F`;
  },
  {
    name: "get_weather",
    description: "Get current weather for a location.",
    schema: z.object({
      location: z.string().describe("City name"),
    }),
  }
);

const search = tool(
  async ({ query }) => {
    return `Search results for: ${query}`;
  },
  {
    name: "search",
    description: "Search for information on the web.",
    schema: z.object({
      query: z.string().describe("The search query"),
    }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [getWeather, search],
  systemPrompt: "You are a helpful assistant that can search and check weather.",
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "What's the weather in Paris?" }],
});
console.log(result.messages[result.messages.length - 1].content);
```

### Agent with Persistence

```typescript
import { createAgent } from "langchain";
import { MemorySaver } from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  checkpointer,
});

// Conversation maintains state across invocations
const config = { configurable: { thread_id: "user-123" } };
await agent.invoke({ messages: [{ role: "user", content: "My name is Alice" }] }, config);
const result = await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Alice"
```

### Agent Configuration Options

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `model` | LLM to use | `"anthropic:claude-sonnet-4-5"` or model instance |
| `tools` | List of tools | `[search, calculator]` |
| `systemPrompt` | Agent instructions | `"You are a helpful assistant"` |
| `checkpointer` | State persistence | `new MemorySaver()` |
| `middleware` | Processing hooks | `[humanInTheLoopMiddleware]` |
| `maxIterations` | Loop limit | `10` |
| `responseFormat` | Structured output | Zod schema |
</create_agent>

<tools>
## Defining Tools with tool()

Tools are functions that agents can call. Use the `tool()` function with a Zod schema.

### Basic Tool

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const calculate = tool(
  async ({ expression }) => {
    const allowed = new Set("0123456789+-*/(). ".split(""));
    if (![...expression].every((c) => allowed.has(c))) {
      return "Error: Invalid characters in expression";
    }
    try {
      return String(eval(expression));
    } catch (e) {
      return `Error: ${e}`;
    }
  },
  {
    name: "calculate",
    description: "Evaluate a mathematical expression safely.",
    schema: z.object({
      expression: z.string().describe("Math expression like '2 + 2' or '10 * 5'"),
    }),
  }
);
```

### Tool with Complex Parameters

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const advancedSearch = tool(
  async ({ query, limit, category }) => {
    return `Found ${limit} results for '${query}' in ${category || "all"}`;
  },
  {
    name: "advanced_search",
    description: "Search with filters.",
    schema: z.object({
      query: z.string().describe("Search query"),
      limit: z.number().default(10).describe("Max results"),
      category: z.enum(["news", "docs", "code"]).optional().describe("Filter by category"),
    }),
  }
);
```

### Async Tool with External API

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const fetchUrl = tool(
  async ({ url }) => {
    const response = await fetch(url);
    return await response.text();
  },
  {
    name: "fetch_url",
    description: "Fetch content from a URL.",
    schema: z.object({
      url: z.string().url().describe("URL to fetch"),
    }),
  }
);
```

### Tool Best Practices

**Good tool definition:**
```typescript
const searchCustomers = tool(
  async ({ query }) => {
    return searchDatabase(query);
  },
  {
    name: "search_customers",
    description: "Search customer database by name, email, or ID. Returns customer records with contact information. Use this when user asks about customer data.",
    schema: z.object({
      query: z.string().describe("Customer name, email, or ID to search for"),
    }),
  }
);
```

**Bad tool definition:**
```typescript
const badTool = tool(
  async ({ data }) => "result",
  {
    name: "bad_tool",
    description: "Does something.", // Too vague!
    schema: z.object({ data: z.string() }),
  }
);
```
</tools>

<middleware>
## Middleware for Agent Control

Middleware intercepts the agent loop to add human approval, error handling, logging, etc.

### Human-in-the-Loop Middleware

Require human approval before executing sensitive tools:

```typescript
import { createAgent, humanInTheLoopMiddleware } from "langchain";

const deleteRecord = tool(
  async ({ recordId }) => {
    await db.delete(recordId);
    return `Deleted record ${recordId}`;
  },
  {
    name: "delete_record",
    description: "Delete a database record permanently.",
    schema: z.object({
      recordId: z.string().describe("ID of record to delete"),
    }),
  }
);

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [deleteRecord, search],
  middleware: [
    humanInTheLoopMiddleware({
      toolsRequiringApproval: ["delete_record"],
    }),
  ],
});

// Agent will pause and ask for approval before calling delete_record
```

### Error Handling Middleware

Catch and handle tool errors gracefully:

```typescript
import { createAgent, createMiddleware } from "langchain";

const errorHandler = createMiddleware({
  name: "ErrorHandler",
  wrapToolCall: async (request, handler) => {
    try {
      return await handler(request);
    } catch (error) {
      return {
        ...request.toolCall,
        content: `Tool error: ${error}. Please try a different approach.`,
      };
    }
  },
});

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [riskyTool],
  middleware: [errorHandler],
});
```

### Logging Middleware

Log all tool calls for debugging:

```typescript
import { createMiddleware } from "langchain";

const loggingMiddleware = createMiddleware({
  name: "LoggingMiddleware",
  wrapToolCall: async (request, handler) => {
    console.log(`Calling tool: ${request.toolCall.name} with args:`, request.toolCall.args);
    const result = await handler(request);
    console.log(`Tool result: ${result.content?.slice(0, 100)}...`);
    return result;
  },
});
```
</middleware>

<model_config>
## Model Configuration

### Model String Format

`createAgent` accepts model strings in `provider:model` format:

```typescript
// Anthropic
const agent = createAgent({ model: "anthropic:claude-sonnet-4-5", tools: [...] });

// OpenAI
const agent = createAgent({ model: "openai:gpt-4.1", tools: [...] });

// AWS Bedrock
const agent = createAgent({ model: "bedrock:anthropic.claude-3-5-sonnet-20241022-v2:0", tools: [...] });
```

### Using Model Instances

For more control, pass a model instance:

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { ChatOpenAI } from "@langchain/openai";

// Anthropic with custom settings
const model = new ChatAnthropic({
  model: "claude-sonnet-4-5",
  temperature: 0,
  maxTokens: 4096,
});

// OpenAI with custom settings
const model = new ChatOpenAI({
  model: "gpt-4.1",
  temperature: 0.7,
});

const agent = createAgent({ model, tools: [...] });
```

### Using initChatModel

For dynamic provider selection:

```typescript
import { initChatModel } from "langchain/chat_models/universal";

const model = await initChatModel("claude-sonnet-4-5", {
  modelProvider: "anthropic",
  temperature: 0,
});

const agent = createAgent({ model, tools: [...] });
```
</model_config>

<streaming>
## Streaming Agent Output

### Stream Modes

```typescript
// Stream full state after each step
for await (const [mode, chunk] of agent.stream(input, { streamMode: ["values"] })) {
  console.log(chunk.messages[chunk.messages.length - 1]);
}

// Stream only changes
for await (const [mode, chunk] of agent.stream(input, { streamMode: ["updates"] })) {
  console.log(chunk);
}

// Stream LLM tokens
for await (const [mode, chunk] of agent.stream(input, { streamMode: ["messages"] })) {
  const [token, metadata] = chunk;
  if (token.content) {
    process.stdout.write(token.content);
  }
}
```
</streaming>

<fix-missing-tool-description>
```typescript
// WRONG: Vague description
const badTool = tool(async ({ input }) => "result", {
  name: "bad_tool",
  description: "Does stuff.", // Too vague!
  schema: z.object({ input: z.string() }),
});

// CORRECT: Clear, specific description
const search = tool(async ({ query }) => webSearch(query), {
  name: "search",
  description: "Search the web for current information about a topic. Use this when you need recent data or facts.",
  schema: z.object({
    query: z.string().describe("The search query (2-10 words recommended)"),
  }),
});
```
</fix-missing-tool-description>

<fix-no-checkpointer>
```typescript
// WRONG: No persistence - agent forgets between calls
const agent = createAgent({ model: "anthropic:claude-sonnet-4-5", tools: [search] });
await agent.invoke({ messages: [{ role: "user", content: "I'm Bob" }] });
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] });
// Agent doesn't remember!

// CORRECT: Add checkpointer and thread_id
import { MemorySaver } from "@langchain/langgraph";

const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  checkpointer: new MemorySaver(),
});

const config = { configurable: { thread_id: "session-1" } };
await agent.invoke({ messages: [{ role: "user", content: "I'm Bob" }] }, config);
await agent.invoke({ messages: [{ role: "user", content: "What's my name?" }] }, config);
// Agent remembers: "Your name is Bob"
```
</fix-no-checkpointer>

<fix-infinite-loop>
```typescript
// WRONG: No iteration limit - could loop forever
const agent = createAgent({ model: "anthropic:claude-sonnet-4-5", tools: [search] });
const result = await agent.invoke({
  messages: [{ role: "user", content: "Keep searching until you find everything" }],
});

// CORRECT: Set maxIterations
const agent = createAgent({
  model: "anthropic:claude-sonnet-4-5",
  tools: [search],
  maxIterations: 10, // Stop after 10 tool calls
});
```
</fix-infinite-loop>

<fix-accessing-result-wrong>
```typescript
// WRONG: Trying to access result.content directly
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.content); // undefined!

// CORRECT: Access messages from result object
const result = await agent.invoke({ messages: [{ role: "user", content: "Hello" }] });
console.log(result.messages[result.messages.length - 1].content); // Last message content
```
</fix-accessing-result-wrong>

<related_skills>
- **langgraph-fundamentals**: For custom graph-based agents with StateGraph
- **langgraph-persistence**: For advanced persistence patterns with checkpointers
- **langchain-output**: For structured output with Zod models
- **langchain-rag**: For RAG pipelines with vector stores
</related_skills>
