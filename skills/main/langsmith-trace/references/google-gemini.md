# Tracing Google Gemini applications

Wrap the `google-genai` (Python) or `@google/genai` (JS) client with LangSmith's `wrap_gemini` / `wrapGemini`. **Beta** — API may change.

## Python

```bash
pip install langsmith google-genai
```

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=<project>
GOOGLE_API_KEY=<key>
```

```python
from google import genai
from langsmith import wrappers

client = wrappers.wrap_gemini(
    genai.Client(),
    tracing_extra={
        "tags": ["gemini", "python"],
        "metadata": {"integration": "google-genai"},
    },
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain quantum computing in simple terms.",
)
```

## JavaScript / TypeScript

```bash
npm install langsmith @google/genai
```

```typescript
import { GoogleGenAI } from "@google/genai";
import { wrapGemini } from "langsmith/wrappers/gemini";

const client = wrapGemini(new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY }), {
  tags: ["gemini", "javascript"],
  metadata: { integration: "google-genai" },
});

const response = await client.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "Explain quantum computing in simple terms.",
});
```

## Config (applies to all calls on the wrapped client)

- `tags` — array of strings
- `metadata` — key-value object
- `client` — custom LangSmith `Client` instance (use to share auth/config)

For per-call control, nest with `@traceable` / `traceable` (see `traceable.md`).
