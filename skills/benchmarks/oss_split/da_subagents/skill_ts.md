---
name: Deep Agents Subagents (TypeScript)
description: [Deep Agents] Using SubAgentMiddleware to spawn subagents for task delegation, context isolation, and specialized work in Deep Agents.
---

# deepagents-subagents (JavaScript/TypeScript)

## Overview

SubAgentMiddleware enables task delegation via the `task` tool. Benefits: context isolation, specialization, token efficiency, parallel execution.

**Default subagent**: "general-purpose" - automatically available with same tools/config as main agent.

## Defining Subagents

### Dictionary-based Subagent

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const searchPapers = tool(
  async ({ query }) => `Found 10 papers about ${query}`,
  {
    name: "search_papers",
    description: "Search academic papers",
    schema: z.object({ query: z.string() }),
  }
);

const agent = await createDeepAgent({
  subagents: [
    {
      name: "research",
      description: "Research academic papers and provide summaries",
      systemPrompt: "You are a research assistant. Provide concise summaries.",
      tools: [searchPapers],
      model: "claude-sonnet-4-5-20250929",  // Optional
    }
  ]
});

const result = await agent.invoke({
  messages: [{ role: "user", content: "Research recent papers on transformers" }]
});
```

### CompiledSubAgent (Custom Graph)

```typescript
import { createDeepAgent, CompiledSubAgent } from "deepagents";

const weatherGraph = createWeatherGraph();  // Your custom LangGraph

const weatherSubagent = new CompiledSubAgent({
  name: "weather",
  description: "Get weather forecasts",
  runnable: weatherGraph
});

const agent = await createDeepAgent({
  subagents: [weatherSubagent]
});
```

## Code Examples

### Example 1: Research Subagent

```typescript
import { createDeepAgent } from "deepagents";
import { tool } from "langchain";
import { z } from "zod";

const webSearch = tool(
  async ({ query }) => `Search results for: ${query}`,
  {
    name: "web_search",
    description: "Search the web",
    schema: z.object({ query: z.string() }),
  }
);

const agent = await createDeepAgent({
  subagents: [
    {
      name: "researcher",
      description: "Conduct web research and compile findings",
      systemPrompt: "Search thoroughly, save to /research/, return summary",
      tools: [webSearch],
    }
  ]
});

const result = await agent.invoke({
  messages: [{
    role: "user",
    content: "Research market trends for EVs"
  }]
});
```

### Example 2: Subagent with HITL

```typescript
import { createDeepAgent } from "deepagents";
import { MemorySaver } from "@langchain/langgraph";

const agent = await createDeepAgent({
  subagents: [
    {
      name: "code-deployer",
      description: "Deploy code to production",
      systemPrompt: "Deploy code safely with all checks",
      tools: [runTests, deployToProd],
      interruptOn: { deploy_to_prod: true },  // Require approval
    }
  ],
  checkpointer: new MemorySaver()  // Required
});
```

### Example 3: Subagent with Custom Skills

```typescript
const agent = await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [
    {
      name: "python-expert",
      description: "Python code review and refactoring",
      systemPrompt: "Review Python code for best practices",
      tools: [readCode, suggestImprovements],
      skills: ["/python-skills/"],  // Subagent-specific
    }
  ]
});
// Custom subagents DON'T inherit main skills by default
// General-purpose subagent DOES inherit main skills
```

## Boundaries

### What Agents CAN Configure
✅ Subagent name, description, tools  
✅ Different models per subagent  
✅ Subagent-specific prompts, middleware, skills  
✅ HITL for subagent tools

### What Agents CANNOT Configure
❌ Change `task` tool name  
❌ Make subagents stateful  
❌ Share state between subagents  
❌ Remove default general-purpose subagent

## Gotchas

### 1. Subagents Are Stateless
```typescript
// ❌ Subagents don't remember previous calls
await agent.invoke({messages: [{role: "user", content: "Research X"}]});
await agent.invoke({messages: [{role: "user", content: "What did you find?"}]});
// Fresh subagent each time

// ✅ Main agent maintains conversation memory
```

### 2. Custom Subagents Don't Inherit Skills
```typescript
// ❌ Subagent won't have main skills
await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [{ name: "helper", ... }]
});

// ✅ Provide skills explicitly
await createDeepAgent({
  skills: ["/main-skills/"],
  subagents: [{
    name: "helper",
    skills: ["/helper-skills/"],
    ...
  }]
});
```

### 3. Subagent Interrupts Need Main Checkpointer
```typescript
// ❌ Missing checkpointer
await createDeepAgent({
  subagents: [{
    name: "deployer",
    interruptOn: { deploy: true }
  }]
});

// ✅ Checkpointer on main agent
await createDeepAgent({
  subagents: [{
    name: "deployer",
    interruptOn: { deploy: true }
  }],
  checkpointer: new MemorySaver()
});
```

## Full Documentation
- [Subagents Guide](https://docs.langchain.com/oss/javascript/deepagents/subagents)
- [SubAgent Middleware](https://docs.langchain.com/oss/javascript/langchain/middleware/built-in#subagent)
- [Task Delegation](https://docs.langchain.com/oss/javascript/deepagents/harness#task-delegation-subagents)
