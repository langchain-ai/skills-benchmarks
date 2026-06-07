# Tracing Mistral applications

Mistral has no native instrumentation. Wrap calls with `@traceable` (Python) or `traceable` (TS) and tag with `ls_provider` / `ls_model_name` for cost tracking.

## Install

```bash
# Python
pip install mistralai langsmith
```

```bash
# JavaScript
npm install @mistralai/mistralai langsmith dotenv
```

## Env

```bash
MISTRAL_API_KEY=<key>
LANGSMITH_TRACING=true                  # required — without it nothing is recorded
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=<project>             # optional, defaults to "default"
```

## Python

```python
import os
from mistralai import Mistral
from langsmith import traceable

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

@traceable(
    run_type="llm",
    metadata={"ls_provider": "mistral", "ls_model_name": "mistral-medium-latest"},
)
def query_mistral(prompt: str):
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message

result = query_mistral("Hello, how are you?")
print(result.content)
```

Run: `python mistral_trace.py`.

## TypeScript

```typescript
import { Mistral } from "@mistralai/mistralai";
import { traceable } from "langsmith/traceable";
import "dotenv/config";

const mistral = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const tracedChat = traceable(
  async (params: { model: string; messages: { role: string; content: string }[] }) => {
    const response = await mistral.chat.complete(params);
    return response.choices[0].message.content;     // return content for LangSmith capture
  },
  {
    name: "Mistral Chat Completion",
    run_type: "llm",
    metadata: { ls_provider: "mistral", ls_model_name: "mistral-small-latest" },
  }
);

await tracedChat({
  model: "mistral-small-latest",
  messages: [{ role: "user", content: "Say hello in one short sentence." }],
});
```

Run: `node index.js`.

## Cost tracking

`ls_provider` + `ls_model_name` are what LangSmith uses to attach pricing to traced LLM calls — without them runs log but cost is `null`. Token counts come from the recorded prompt and response messages. Enable model pricing in your LangSmith workspace settings to see costs in the run UI. See "Automatically track costs based on token counts" in the LangSmith docs.

## Gotchas

- `LANGSMITH_TRACING=true` must be set; otherwise `@traceable` is a no-op and nothing reaches LangSmith.
- TS: return the message content from the traced function (not the full response object) for clean input/output rendering.
- Update `ls_model_name` whenever you switch models — it's used for cost lookup, not auto-detected.
