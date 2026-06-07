# Tracing with @traceable / wrap_openai

The default path for any non-LangChain app **without** native OTel support. Wrap your LLM client and/or decorate functions you want as spans. LangSmith handles context propagation across nested calls automatically.

For OTel-instrumented apps see `otel.md`. For raw REST (no SDK), see `api.md`.

## Install

```bash
pip install langsmith                # Python
npm install langsmith                 # TypeScript / JavaScript
```

## Environment variables

| Var | Notes |
|---|---|
| `LANGSMITH_TRACING` | `true` to enable. Required even when only using `wrap_*`. |
| `LANGSMITH_API_KEY` | Required. |
| `LANGSMITH_PROJECT` | Optional; defaults to `default`. |
| `LANGSMITH_WORKSPACE_ID` | Set if your API key is linked to multiple workspaces. |
| `LANGSMITH_ENDPOINT` | Override the base URL (EU, AWS SaaS, self-hosted). |
| `LANGSMITH_HIDE_INPUTS` / `LANGSMITH_HIDE_OUTPUTS` | `true` to strip inputs/outputs before send. |
| `LANGSMITH_HIDE_METADATA` | `true` to strip run metadata (Python). |
| `LANGCHAIN_CALLBACKS_BACKGROUND` | `false` for serverless (Python) so spans flush before the process exits. |

## `@traceable` / `traceable`

Apply to any function to make it a traced run. Nested traceable calls auto-nest as child runs.

### Python

```python
from langsmith import traceable
from openai import Client

openai = Client()

@traceable
def format_prompt(subject):
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Name a store that sells {subject}?"},
    ]

@traceable(run_type="llm")
def invoke_llm(messages):
    return openai.chat.completions.create(
        model="gpt-4o-mini", messages=messages, temperature=0
    )

@traceable
def parse_output(response):
    return response.choices[0].message.content

@traceable
def run_pipeline():
    return parse_output(invoke_llm(format_prompt("colorful socks")))

run_pipeline()
```

### TypeScript

```typescript
import { traceable } from "langsmith/traceable";
import OpenAI from "openai";

const openai = new OpenAI();

const formatPrompt = traceable((subject: string) => [
  { role: "system" as const, content: "You are a helpful assistant." },
  { role: "user" as const, content: `Name a store that sells ${subject}?` },
], { name: "formatPrompt" });

const invokeLLM = traceable(
  async ({ messages }: { messages: { role: string; content: string }[] }) =>
    openai.chat.completions.create({ model: "gpt-4o-mini", messages, temperature: 0 }),
  { run_type: "llm", name: "invokeLLM" }
);

const runPipeline = traceable(async () => {
  const messages = await formatPrompt("colorful socks");
  const response = await invokeLLM({ messages });
  return response.choices[0].message.content;
}, { name: "runPipeline" });

await runPipeline();
```

When you wrap a sync function with `traceable` in JS, `await` it on call so the span flushes before the parent ends.

### Decorator / config options

| Option | Notes |
|---|---|
| `name` | Display name in the UI. Defaults to the function name. |
| `run_type` | `chain` (default), `llm`, `tool`, `retriever`, `embedding`, `prompt`, `parser`. Drives UI rendering. |
| `tags` | List of strings for filtering. |
| `metadata` | Dict merged into `extra.metadata`. Use `ls_provider` / `ls_model_name` to enable cost tracking on non-OpenAI LLMs. |
| `project_name` | Route this run (and its children) to a named project. |
| `client` | Pass a pre-configured `Client` (e.g. for `flush()` control). |
| `process_inputs` | Function `(inputs: dict) -> dict` to transform inputs before logging. |
| `process_outputs` | Function `(output) -> dict` to transform outputs before logging (Python `langsmith>=0.1.98`). |
| `reduce_fn` (Python) / `aggregator` (JS) | Aggregate streamed chunks into a single output value. |

## Wrap an LLM client

`wrap_*` auto-traces every call on a client — no decorator needed. Renders messages, tool calls, and multimodal content blocks correctly. Composable with `@traceable`.

### OpenAI (and OpenAI-compatible: Azure OpenAI, Together, Groq, ...)

```python
from openai import OpenAI
from langsmith.wrappers import wrap_openai

client = wrap_openai(OpenAI())
client.chat.completions.create(model="gpt-4o-mini", messages=[...])
```

```typescript
import OpenAI from "openai";
import { wrapOpenAI } from "langsmith/wrappers";

const client = wrapOpenAI(new OpenAI());
```

### Anthropic

```python
import anthropic
from langsmith.wrappers import wrap_anthropic

client = wrap_anthropic(anthropic.Anthropic())
```

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { wrapAnthropic } from "langsmith/wrappers/anthropic";

const client = wrapAnthropic(new Anthropic());
```

### Google Gemini

See `google-gemini.md`. Python: `wrap_gemini` from `langsmith.wrappers`.

### Other providers

If LangSmith doesn't ship a dedicated wrapper, wrap your own call with `@traceable(run_type="llm", metadata={"ls_provider": "...", "ls_model_name": "..."})` to enable cost tracking and the LLM span renderer.

## `trace` context manager (Python only)

Useful when you can't decorate (e.g. dynamic project name, partial blocks). Composes with `@traceable` and `wrap_openai`.

```python
import langsmith as ls
from langsmith.wrappers import wrap_openai
from openai import Client

client = wrap_openai(Client())

with ls.trace("Chat Pipeline", "chain", project_name="my_test", inputs={"q": q}) as rt:
    output = client.chat.completions.create(...).choices[0].message.content
    rt.end(outputs={"output": output})
```

## RunTree API (low-level)

Manually post and patch runs — equivalent to the SDK's internal model. Not recommended unless you need precise control over `dotted_order` / parent-child links. `LANGSMITH_API_KEY` is required; `LANGSMITH_TRACING` is not (RunTree always sends).

```python
from langsmith.run_trees import RunTree

pipeline = RunTree(name="Chat Pipeline", run_type="chain", inputs={"q": q})
pipeline.post()
child = pipeline.create_child(name="OpenAI Call", run_type="llm", inputs={"messages": ...})
child.post()
# ...
child.end(outputs=...); child.patch()
pipeline.end(outputs=...); pipeline.patch()
```

```typescript
import { RunTree } from "langsmith";

const pipeline = new RunTree({ name: "Chat Pipeline", run_type: "chain", inputs: { q } });
await pipeline.postRun();
const child = await pipeline.createChild({ name: "OpenAI Call", run_type: "llm", inputs: { messages } });
await child.postRun();
child.end(result); await child.patchRun();
pipeline.end({ outputs: { answer } }); await pipeline.patchRun();
```

## Streaming / generator functions

`@traceable` natively traces generators. Outputs are aggregated into a list by default; pass `reduce_fn` (Python) / `aggregator` (JS) to fold them.

```python
from langsmith import traceable

@traceable(reduce_fn=lambda chunks: "".join(chunks))
def my_generator():
    for chunk in ["Hello", " ", "World"]:
        yield chunk
```

```typescript
const myGenerator = traceable(function* () {
  for (const chunk of ["Hello", " ", "World"]) yield chunk;
}, { aggregator: (chunks: string[]) => chunks.join("") });
```

Aggregation only changes how the trace stores the output — your function still yields chunks.

## Custom run IDs (UUIDv7)

Override the run ID when you need to attach feedback immediately or correlate with an external system. Use UUIDv7 so timestamp ordering is preserved.

```python
from langsmith import traceable, uuid7

run_id = uuid7()
my_pipeline("…", langsmith_extra={"run_id": run_id})
```

```typescript
import { traceable, uuid7 } from "langsmith";

const myPipeline = traceable(async (q: string) => "…", { name: "my-pipeline", id: uuid7() });
```

`uuid7` requires `langsmith>=0.4.43` (Python) or `>=0.3.80` (JS).

## Access the current run

```python
from langsmith import traceable, get_current_run_tree

@traceable
def step():
    rt = get_current_run_tree()
    print(rt.trace_id)
```

```typescript
import { traceable, getCurrentRunTree } from "langsmith/traceable";

const step = traceable(() => {
  const rt = getCurrentRunTree();
  console.log(rt.trace_id);
});
```

## Flush before exit (serverless / short-lived processes)

Tracing runs in a background thread. AWS Lambda / Vercel Functions / scripts can exit before runs flush.

```python
from langsmith import Client

client = Client()

@traceable(client=client)
async def handler(): ...

try:
    await handler()
finally:
    await client.flush()
```

```typescript
import { Client } from "langsmith";

const client = new Client();
const handler = traceable(async () => { /* … */ }, { client });

try { await handler(); } finally { await client.flush(); }
```

Python alternative: `LANGCHAIN_CALLBACKS_BACKGROUND=false` makes calls block until flushed.

## Tips

- Apply `@traceable` to every nested function you want as its own span — without it, nested calls collapse into one.
- Set `run_type="llm"` + `metadata={"ls_provider": "...", "ls_model_name": "..."}` on raw LLM calls to enable cost tracking.
- For nested instrumentation (e.g. `instructor` patching a wrapped OpenAI client) the wrapped client should be patched **last** — see `instructor.md`.
- `wrap_*` and `@traceable` compose — use both in the same app.
