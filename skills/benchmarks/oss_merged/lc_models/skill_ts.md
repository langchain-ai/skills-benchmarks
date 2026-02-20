---
name: LangChain Models & Streaming (TypeScript)
description: "INVOKE THIS SKILL when configuring chat models OR implementing streaming. Covers ChatOpenAI/ChatAnthropic, streaming tokens, and multimodal inputs. CRITICAL: Fixes for messages mode tuple unpacking [token, metadata], and multi-mode stream handling."
---

<overview>
Chat models are the core of LangChain applications. They take messages as input and return AI-generated messages as output with a unified interface across providers.

**Key Concepts:**
- **init_chat_model()**: Universal initialization for any provider
- **Provider classes**: Direct initialization (ChatOpenAI, ChatAnthropic, etc.)
- **Streaming**: Real-time token-by-token responses
- **Multimodal**: Images, PDFs, and other non-text data
</overview>

<provider-selection>

| Provider | Best For | Package |
|----------|----------|---------|
| **OpenAI** | General purpose, reasoning | `langchain-openai` |
| **Anthropic** | Safety, analysis, long context | `langchain-anthropic` |
| **Google** | Multimodal, speed | `langchain-google-genai` |

</provider-selection>

<stream-mode-selection>

| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state dict |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | (token, metadata) tuples |

</stream-mode-selection>

---

## Model Initialization

<ex-basic-model-initialization>
Initialize chat models directly using provider-specific classes from LangChain packages.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";

// OpenAI
const model = new ChatOpenAI({ model: "gpt-4" });

// Anthropic
const anthropic = new ChatAnthropic({ model: "claude-sonnet-4-5-20250929" });
```
</ex-basic-model-initialization>

<ex-provider-specific>
Configure provider-specific chat models with custom parameters like temperature and max tokens.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";

const openai = new ChatOpenAI({
  model: "gpt-4",
  temperature: 0.7,
  maxTokens: 1000,
});

const anthropic = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
  maxTokens: 2000,
});
```
</ex-provider-specific>

---

## Invocation

<ex-simple-invocation>
Invoke a chat model with either a simple string or an array of message objects.
```typescript
const model = new ChatOpenAI({ model: "gpt-4" });

// String input
const response = await model.invoke("What is LangChain?");
console.log(response.content);

// Message array
const response2 = await model.invoke([{ role: "user", content: "Hello!" }]);
```
</ex-simple-invocation>

---

## Streaming

<ex-basic-token-streaming>
Stream tokens in real-time using for await with the async stream() method.
```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4" });

for await (const chunk of await model.stream("Explain quantum computing")) {
  process.stdout.write(chunk.content);
}
```
</ex-basic-token-streaming>

<ex-async-streaming>
Stream responses asynchronously using for await with the stream() method.
```typescript
const model = new ChatOpenAI({ model: "gpt-4" });

for await (const chunk of await model.stream("Explain AI")) {
  process.stdout.write(chunk.content);
}
```
</ex-async-streaming>

---

## Multimodal

<ex-image-input>
Send images to multimodal models using URL or base64-encoded data URL format.
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";
import * as fs from "fs";

const model = new ChatOpenAI({ model: "gpt-4o" });

// From URL
const message = new HumanMessage({
  content: [
    { type: "text", text: "What's in this image?" },
    { type: "image_url", image_url: { url: "https://example.com/photo.jpg" } },
  ],
});

// From base64
const imageData = fs.readFileSync("./photo.jpg").toString("base64");
const message2 = new HumanMessage({
  content: [
    { type: "text", text: "Describe this image" },
    { type: "image_url", image_url: { url: `data:image/jpeg;base64,${imageData}` } },
  ],
});

const response = await model.invoke([message]);
```
</ex-image-input>

<boundaries>
### What You CAN Configure

- Model Selection: Any supported model
- Temperature: Control randomness (0-1)
- Max Tokens: Limit response length
- Stream modes

### What You CANNOT Configure

- Model Training Data
- Token Costs: Set by provider
- Rate Limits: Set by provider
</boundaries>

<fix-response-content-access>
Access the .content property on AIMessage to get the actual response text.
```typescript
// WRONG: Wrong property access
const response = await model.invoke("Hello");
console.log(response);  // AIMessage object

// CORRECT: Access .content property
console.log(response.content);
```
</fix-response-content-access>

<fix-streaming-requires-iteration>
Iterate over the async stream with for await to receive chunks.
```typescript
// WRONG: Not iterating stream
const stream = model.stream("Hello");
console.log(stream);  // AsyncGenerator

// CORRECT: Use for await
for await (const chunk of await model.stream("Hello")) {
  process.stdout.write(chunk.content);
}
```
</fix-streaming-requires-iteration>

<fix-sync-vs-async>
TypeScript methods are async by default; always use await with invoke() and stream().
```typescript
// TypeScript is always async - use await
const response = await model.invoke("Hello");

for await (const chunk of await model.stream("Hello")) {
  process.stdout.write(chunk.content);
}
```
</fix-sync-vs-async>
