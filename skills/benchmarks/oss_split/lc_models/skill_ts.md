---
name: langchain-models-js
description: "[LangChain] Initialize and use LangChain chat models - includes provider selection (OpenAI, Anthropic, Google), model configuration, and invocation patterns"
---

<overview>
Chat models are the core of LangChain applications. They take messages as input and return AI-generated messages as output. LangChain provides a unified interface across multiple providers (OpenAI, Anthropic, Google, etc.).

**Key Concepts:**
- **initChatModel()**: Universal initialization for any provider
- **Provider-specific classes**: Direct initialization (ChatOpenAI, ChatAnthropic, etc.)
- **Messages**: Structured input/output format (HumanMessage, AIMessage, etc.)
- **Invocation patterns**: invoke(), stream(), batch()
</overview>

<provider-selection-table>

| Provider | Best For | Models | Strengths |
|----------|----------|--------|-----------|
| OpenAI | General purpose, reasoning | GPT-4.1, GPT-5 | Strong reasoning, large context |
| Anthropic | Safety, analysis | Claude Sonnet/Opus | Safety, long context, vision |
| Google | Multimodal, speed | Gemini 2.5 | Fast, multimodal, cost-effective |
| AWS Bedrock | Enterprise, compliance | Multiple providers | Security, compliance, variety |
| Azure OpenAI | Enterprise OpenAI | GPT models | Enterprise features, SLAs |

</provider-selection-table>

<model-selection-table>

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Complex reasoning | GPT-5, Claude Opus | Best logical capabilities |
| Fast responses | Gemini Flash, GPT-4.1-mini | Low latency |
| Vision tasks | GPT-4.1, Claude Sonnet, Gemini | Multimodal support |
| Long context | Claude Opus, Gemini | 100k+ token windows |
| Cost-effective | GPT-4.1-mini, Gemini Flash | Lower pricing |
| Enterprise/compliance | Azure OpenAI, AWS Bedrock | Security features |

</model-selection-table>

<initialization-methods-table>

| Method | When to Use | Example |
|--------|-------------|---------|
| `initChatModel("provider:model")` | Quick switching between providers | `initChatModel("openai:gpt-4.1")` |
| Provider class | Need provider-specific features | `new ChatOpenAI({ model: "gpt-4.1" })` |
| With configuration | Custom parameters needed | Temperature, max tokens, etc. |

</initialization-methods-table>

<ex-basic-init>
```typescript
import { initChatModel } from "langchain";

// Universal initialization - easiest way
const model = await initChatModel("openai:gpt-4.1");

// Or with provider shorthand
const model2 = await initChatModel("gpt-4.1"); // Defaults to OpenAI

// Set API key (usually from environment)
process.env.OPENAI_API_KEY = "your-api-key";
const model3 = await initChatModel("openai:gpt-4.1");
```
</ex-basic-init>

<ex-provider-specific>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatAnthropic } from "@langchain/anthropic";
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

// OpenAI
const openai = new ChatOpenAI({
  model: "gpt-4.1",
  temperature: 0.7,
  maxTokens: 1000,
  apiKey: process.env.OPENAI_API_KEY,
});

// Anthropic
const anthropic = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
  maxTokens: 2000,
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Google
const google = new ChatGoogleGenerativeAI({
  model: "gemini-2.5-flash-lite",
  temperature: 0.5,
  apiKey: process.env.GOOGLE_API_KEY,
});
```
</ex-provider-specific>

<ex-simple-invoke>
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// String input (converted to HumanMessage)
const response = await model.invoke("What is LangChain?");
console.log(response.content);

// Message array input
const response2 = await model.invoke([
  { role: "user", content: "Hello!" }
]);
console.log(response2.content);
```
</ex-simple-invoke>

<ex-streaming>
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Stream tokens as they arrive
const stream = await model.stream("Explain quantum computing");

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```
</ex-streaming>

<ex-batch>
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Process multiple inputs in parallel
const results = await model.batch([
  "What is AI?",
  "What is ML?",
  "What is LangChain?"
]);

results.forEach((result, i) => {
  console.log(`Answer ${i + 1}:`, result.content);
});
```
</ex-batch>

<ex-multi-turn>
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Build conversation history
const messages = [
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "What's the capital of France?" },
];

const response1 = await model.invoke(messages);
messages.push({ role: "assistant", content: response1.content });

// Continue conversation
messages.push({ role: "user", content: "What's its population?" });
const response2 = await model.invoke(messages);

console.log(response2.content); // Knows we're talking about Paris
```
</ex-multi-turn>

<ex-config-options>
```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "gpt-4.1",

  // Control randomness (0 = deterministic, 1 = creative)
  temperature: 0.7,

  // Limit response length
  maxTokens: 500,

  // Alternative sampling method
  topP: 0.9,

  // Penalize repetition
  frequencyPenalty: 0.5,
  presencePenalty: 0.5,

  // Stop generation at these strings
  stop: ["\n\n", "END"],

  // Timeout for requests
  timeout: 30000, // 30 seconds

  // Max retries on failure
  maxRetries: 3,
});
```
</ex-config-options>

<ex-azure-openai>
```typescript
import { ChatOpenAI } from "@langchain/openai";

const azure = new ChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "your-instance-name",
  azureOpenAIApiDeploymentName: "your-deployment-name",
  azureOpenAIApiVersion: "2024-02-15-preview",
});
```
</ex-azure-openai>

<ex-aws-bedrock>
```typescript
import { ChatBedrock } from "@langchain/aws";

// AWS credentials from environment or ~/.aws/credentials
const bedrock = new ChatBedrock({
  model: "anthropic.claude-3-5-sonnet-20240620-v1:0",
  region: "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});
```
</ex-aws-bedrock>

<ex-model-selector>
```typescript
import { initChatModel } from "langchain";

function getModel(task: string) {
  const modelMap = {
    reasoning: "openai:gpt-5",
    fast: "google-genai:gemini-2.5-flash-lite",
    vision: "openai:gpt-4.1",
    long_context: "anthropic:claude-sonnet-4-5-20250929",
    cost_effective: "openai:gpt-4.1-mini",
  };

  return initChatModel(modelMap[task] || "openai:gpt-4.1");
}

// Usage
const reasoningModel = await getModel("reasoning");
const fastModel = await getModel("fast");
```
</ex-model-selector>

<ex-error-handling>
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

try {
  const response = await model.invoke("Hello!");
  console.log(response.content);
} catch (error) {
  if (error.status === 429) {
    console.error("Rate limit exceeded");
  } else if (error.status === 401) {
    console.error("Invalid API key");
  } else {
    console.error("Error:", error.message);
  }
}
```
</ex-error-handling>

<ex-capabilities-check>
```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Check if model supports features
console.log("Supports streaming:", typeof model.stream === "function");
console.log("Supports tool calling:", typeof model.bindTools === "function");
console.log("Supports structured output:", typeof model.withStructuredOutput === "function");
```
</ex-capabilities-check>

<boundaries>
**What You CAN Configure**

* Model Selection**: Any supported model from any provider
* Temperature**: Control randomness (0-1)
* Max Tokens**: Limit response length
* Stop Sequences**: Define where to stop generation
* Timeout/Retries**: Control request behavior
* API Keys**: Per-model or from environment
* Provider-specific Options**: Each provider has unique features

**What You CANNOT Configure**

* Model Training Data**: Models are pre-trained
* Model Architecture**: Can't modify internal structure
* Token Costs**: Set by provider
* Rate Limits**: Set by provider (can manage with queues)
* Model Capabilities**: Vision/tool support is model-specific
</boundaries>

<fix-api-key-not-found>
```typescript
// Problem: Missing API key
const model = await initChatModel("openai:gpt-4.1");
await model.invoke("Hello"); // Error: API key not found

// Solution: Set environment variable
process.env.OPENAI_API_KEY = "sk-...";
const model = await initChatModel("openai:gpt-4.1");

// OR pass directly
import { ChatOpenAI } from "@langchain/openai";
const model = new ChatOpenAI({
  model: "gpt-4.1",
  apiKey: "sk-...",
});
```
</fix-api-key-not-found>

<fix-model-name-typos>
```typescript
// Problem: Wrong model name
const model = await initChatModel("gpt4"); // Error!

// Solution: Use correct format
const model = await initChatModel("openai:gpt-4.1");
// Or provider shorthand
const model2 = await initChatModel("gpt-4.1");
```
</fix-model-name-typos>

<fix-response-content-access>
```typescript
// Problem: Wrong property access
const response = await model.invoke("Hello");
console.log(response); // AIMessage object, not string

// Solution: Access .content property
console.log(response.content); // "Hello! How can I help you?"

// Or use .toString()
console.log(response.toString());
```
</fix-response-content-access>

<fix-streaming-requires-async>
```typescript
// Problem: Not awaiting stream
const stream = model.stream("Hello");
console.log(stream); // Promise, not chunks

// Solution: Use for await
const stream = await model.stream("Hello");
for await (const chunk of stream) {
  console.log(chunk.content);
}
```
</fix-streaming-requires-async>

<fix-temperature-confusion>
```typescript
// Problem: Wrong temperature range
const model = new ChatOpenAI({
  temperature: 10, // Too high! Should be 0-1
});

// Solution: Use 0-1 range
const deterministic = new ChatOpenAI({ temperature: 0 }); // Always same
const balanced = new ChatOpenAI({ temperature: 0.7 }); // Default
const creative = new ChatOpenAI({ temperature: 1 }); // Maximum randomness
```
</fix-temperature-confusion>

<fix-token-limits>
```typescript
// Problem: Input + output exceeds model limit
const longText = "...50,000 words...";
const model = await initChatModel("gpt-4.1"); // 128k context
await model.invoke(longText); // May succeed

const model2 = await initChatModel("gpt-4.1-mini"); // 16k context
await model2.invoke(longText); // Error: context too long

// Solution: Check input length or use larger context model
import { encoding_for_model } from "tiktoken";

const enc = encoding_for_model("gpt-4.1");
const tokens = enc.encode(longText);
console.log(`Input tokens: ${tokens.length}`);

if (tokens.length > 100000) {
  // Use Claude with 200k context
  const model = await initChatModel("anthropic:claude-opus-4");
}
```
</fix-token-limits>

<fix-provider-specific-features>
```typescript
// Problem: Using provider-specific feature with wrong model
const google = await initChatModel("google-genai:gemini-2.5-flash");
google.bindTools([tool]); // May not work the same way

// Solution: Check documentation for each provider
// OpenAI has specific tool calling format
// Anthropic has specific tool calling format
// Google has specific tool calling format

// Use initChatModel for portability, but be aware of differences
```
</fix-provider-specific-features>

<documentation-links>
- [Chat Models Overview](https://docs.langchain.com/oss/javascript/langchain/models)
- [OpenAI Integration](https://docs.langchain.com/oss/javascript/integrations/chat/openai)
- [Anthropic Integration](https://docs.langchain.com/oss/javascript/integrations/chat/anthropic)
- [Google Integration](https://docs.langchain.com/oss/javascript/integrations/chat/google_generative_ai)
- [All Chat Model Integrations](https://docs.langchain.com/oss/javascript/integrations/chat/index)
- [Model Providers Overview](https://docs.langchain.com/oss/javascript/integrations/providers/all_providers)
</documentation-links>
