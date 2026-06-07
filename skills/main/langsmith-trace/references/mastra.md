# Tracing Mastra applications (TypeScript only)

Mastra ships a first-party `@mastra/langsmith` exporter. Configure it on the `Mastra` constructor.

## Install

```bash
npm install @mastra/core @mastra/langsmith @mastra/observability @mastra/libsql
```

## Env

```bash
LANGSMITH_API_KEY=<key>
LANGCHAIN_PROJECT=<project>   # optional
OPENAI_API_KEY=<key>          # if using OpenAI models
```

## Setup (`mastra.ts`)

```typescript
import { Mastra } from "@mastra/core";
import { LibSQLStore } from "@mastra/libsql";
import { LangSmithExporter } from "@mastra/langsmith";
import { echoAgent } from "./agent";

export const mastra = new Mastra({
  agents: { echoAgent },
  storage: new LibSQLStore({ url: "file:./mastra.db" }),  // required, even if exporting elsewhere
  observability: {
    configs: {
      langsmith: {
        serviceName: "mastra-langsmith-demo",
        exporters: [new LangSmithExporter({ apiKey: process.env.LANGSMITH_API_KEY })],
      },
    },
  },
  telemetry: { enabled: false },  // disable deprecated telemetry to avoid double-emitting
});
```

## Define and run an agent

```typescript
// agent.ts
import { Agent } from "@mastra/core/agent";

export const echoAgent = new Agent({
  name: "echoAgent",
  instructions: "You are a helpful assistant.",
  model: "openai/gpt-4o-mini",  // string-based ID, not provider object
});
```

```typescript
// index.ts
import { mastra } from "./mastra";
const result = await mastra.getAgent("echoAgent").generate("Say hello.");
```

## Notes

- Storage is required even when exporting traces externally
- Disable the deprecated `telemetry` block to avoid warnings + double traces
- Use string-based model IDs (`"openai/gpt-4o-mini"`) — provider object literals can break tracing
- No instrumentation file needed when running outside the Mastra server
