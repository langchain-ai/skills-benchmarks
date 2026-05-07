# Tracing Vercel AI SDK applications (TS/JS only)

Wrap the AI SDK's exported methods with `wrapAISDK`. Requires AI SDK v5 and `langsmith>=0.3.63`. (For older AI SDK versions, fall back to OTel — see `otel.md`.)

## Install

```bash
npm install ai @ai-sdk/openai zod
```

## Env

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<key>
LANGSMITH_WORKSPACE_ID=<workspace-id>   # only if API key spans multiple workspaces
OPENAI_API_KEY=<key>
```

## Basic setup

```typescript
import { openai } from "@ai-sdk/openai";
import * as ai from "ai";
import { wrapAISDK } from "langsmith/experimental/vercel";

const { generateText, streamText, generateObject, streamObject } = wrapAISDK(ai);

await generateText({
  model: openai("gpt-5-nano"),
  prompt: "Write a vegetarian lasagna recipe.",
});
```

Tool calls and multi-step runs (`stopWhen: stepCountIs(N)`) are traced as nested spans automatically.

## Group runs with `traceable`

```typescript
import { traceable } from "langsmith/traceable";

const wrapper = traceable(async (input: string) => {
  const { text } = await generateText({ model: openai("gpt-5-nano"), prompt: input, tools: {...} });
  return text;
}, { name: "wrapper" });
```

## Per-call config

```typescript
import { createLangSmithProviderOptions } from "langsmith/experimental/vercel";

const lsConfig = createLangSmithProviderOptions({
  metadata: { individual_key: "value" },
  name: "my_individual_run",
});

await generateText({
  model: openai("gpt-5-nano"),
  prompt: "...",
  providerOptions: { langsmith: lsConfig },
});
```

Pass options to `wrapAISDK(ai, { ... })` for config that applies to **all** calls.

## Serverless flush

```typescript
import { Client } from "langsmith";
const client = new Client();
const { generateText } = wrapAISDK(ai, { client });

try {
  await generateText({ ... });
} finally {
  await client.awaitPendingTraceBatches();
}
```

Next.js: use the `after()` hook from `next/server` to call `awaitPendingTraceBatches()` after the response is sent.

## Pre-specified run IDs

```typescript
import { uuid7 } from "langsmith";

const runId = uuid7();
const lsConfig = createLangSmithProviderOptions({ id: runId });
await generateText({ model: openai("gpt-5.4-mini"), prompt: "...", providerOptions: { langsmith: lsConfig } });
// Later: attach feedback / look up run by runId
```

## Redacting inputs/outputs

`createLangSmithProviderOptions` accepts `processInputs`, `processOutputs`, `processChildLLMRunInputs`, `processChildLLMRunOutputs`. The actual return value is unaffected — only what's sent to LangSmith gets redacted. For tool input/output redaction, wrap the tool's `execute` in `traceable({ processInputs, processOutputs, run_type: "tool" })`.
