# Tracing OpenAI Agents SDK applications

LangSmith ships `OpenAIAgentsTracingProcessor` for both Python and JS. Register it as a trace processor before running agents.

## Version requirements

- Python: `langsmith>=0.3.15` — `pip install "langsmith[openai-agents]"`
- JS/TS: `langsmith>=0.5.25` — `npm install langsmith @openai/agents zod`

## Env

```bash
LANGSMITH_API_KEY=<key>
OPENAI_API_KEY=<key>
LANGSMITH_PROJECT=<project>          # optional
LANGSMITH_WORKSPACE_ID=<workspace>   # only if API key spans multiple workspaces
```

Installing the processor is an **explicit opt-in** — it posts traces even when `LANGSMITH_TRACING` is not set.

## Python

```bash
pip install "langsmith[openai-agents]"
# or: uv add "langsmith[openai-agents]"
```

```python
import asyncio
from agents import Agent, Runner, set_trace_processors
from langsmith.integrations.openai_agents_sdk import OpenAIAgentsTracingProcessor

async def main():
    agent = Agent(
        name="Captain Obvious",
        instructions="You are Captain Obvious, the world's most literal technical support agent.",
    )
    result = await Runner.run(agent, "Why is my code failing when I try to divide by zero?")
    print(result.final_output)

if __name__ == "__main__":
    set_trace_processors([OpenAIAgentsTracingProcessor()])
    asyncio.run(main())
```

## JavaScript / TypeScript

```bash
npm install langsmith @openai/agents zod
# or: yarn add langsmith @openai/agents zod
# or: pnpm add langsmith @openai/agents zod
```

```typescript
import { Agent, run, setTraceProcessors, tool } from "@openai/agents";
import { z } from "zod";
import { OpenAIAgentsTracingProcessor } from "langsmith/wrappers/openai_agents";

setTraceProcessors([new OpenAIAgentsTracingProcessor()]);

const getWeather = tool({
  name: "get_weather",
  description: "Get the current weather for a city",
  parameters: z.object({ city: z.string() }),
  execute: async ({ city }) => `The weather in ${city} is sunny.`,
});

const agent = new Agent({
  name: "WeatherAgent",
  instructions: "Use get_weather when asked about weather.",
  model: "gpt-5-nano",
  tools: [getWeather],
});

const result = await run(agent, "What's the weather in San Francisco?");
console.log(result.finalOutput);
```

The trace contains the root agent run, response spans, handoffs, and nested tool call spans.

## Configure the processor

```typescript
import { Client } from "langsmith";
import { OpenAIAgentsTracingProcessor } from "langsmith/wrappers/openai_agents";

const client = new Client();
const processor = new OpenAIAgentsTracingProcessor({
  client,                          // optional langsmith Client
  projectName: "openai-agents-demo",
  name: "Support agent workflow",  // root trace name
  tags: ["openai-agents"],
  metadata: { environment: "development" },
});

setTraceProcessors([processor]);
```

## Nest `traceable` inside tools

`traceable` calls inside tool `execute` handlers nest under the active tool span automatically.

```typescript
import { traceable } from "langsmith/traceable";

const lookupOrder = traceable(
  async (orderId: string) => ({ orderId, status: "shipped" }),
  { name: "lookup_order" }
);

const orderStatus = tool({
  name: "order_status",
  description: "Look up the status of an order",
  parameters: z.object({ orderId: z.string() }),
  execute: async ({ orderId }) => JSON.stringify(await lookupOrder(orderId)),
});
```

## Serverless flush

Flush pending traces before the process exits:

```typescript
const processor = new OpenAIAgentsTracingProcessor({ client });
setTraceProcessors([processor]);

try {
  await run(agent, "Help me reset my password.");
} finally {
  await processor.forceFlush();
}
```

## Notes

- Installing the processor is an explicit opt-in — it posts traces even when `LANGSMITH_TRACING` is not set.
- Nested `traceable` calls inside agent tools inherit the active trace context.
- The processor logs the root agent run, response spans, handoffs, and nested tool spans.
