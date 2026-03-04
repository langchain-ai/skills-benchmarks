---
name: langchain-models
description: "[LangChain] Initialize and use LangChain chat models - includes provider selection (OpenAI, Anthropic, Google), model configuration, and invocation patterns"
---

<oneliner>
Initialize and use LangChain chat models with providers like OpenAI, Anthropic, and Google - includes model configuration, invocation patterns, and error handling.
</oneliner>

<overview>
Chat models are the core of LangChain applications. They take messages as input and return AI-generated messages as output. LangChain provides a unified interface across multiple providers (OpenAI, Anthropic, Google, etc.).

Key Concepts:
- **init_chat_model() / initChatModel()**: Universal initialization for any provider
- **Provider-specific classes**: Direct initialization (ChatOpenAI, ChatAnthropic, etc.)
- **Messages**: Structured input/output format (HumanMessage, AIMessage, etc.)
- **Invocation patterns**: invoke(), stream(), batch()
</overview>

<when-to-use>

| Provider | Best For | Models | Strengths |
|----------|----------|--------|-----------|
| OpenAI | General purpose, reasoning | GPT-4.1, GPT-5 | Strong reasoning, large context |
| Anthropic | Safety, analysis | Claude Sonnet/Opus | Safety, long context, vision |
| Google | Multimodal, speed | Gemini 2.5 | Fast, multimodal, cost-effective |
| AWS Bedrock | Enterprise, compliance | Multiple providers | Security, compliance, variety |
| Azure OpenAI | Enterprise OpenAI | GPT models | Enterprise features, SLAs |

</when-to-use>

<choosing-a-model>

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Complex reasoning | GPT-5, Claude Opus | Best logical capabilities |
| Fast responses | Gemini Flash, GPT-4.1-mini | Low latency |
| Vision tasks | GPT-4.1, Claude Sonnet, Gemini | Multimodal support |
| Long context | Claude Opus, Gemini | 100k+ token windows |
| Cost-effective | GPT-4.1-mini, Gemini Flash | Lower pricing |
| Enterprise/compliance | Azure OpenAI, AWS Bedrock | Security features |

</choosing-a-model>

<initialization-methods>

| Method | When to Use | Python Example | TypeScript Example |
|--------|-------------|----------------|-------------------|
| Universal init | Quick switching between providers | `init_chat_model("openai:gpt-4.1")` | `initChatModel("openai:gpt-4.1")` |
| Provider class | Need provider-specific features | `ChatOpenAI(model="gpt-4.1")` | `new ChatOpenAI({ model: "gpt-4.1" })` |
| With configuration | Custom parameters needed | Temperature, max tokens, etc. | Temperature, max tokens, etc. |

</initialization-methods>

<ex-basic-init>
<python>
Universal model initialization:

```python
from langchain.chat_models import init_chat_model

# Universal initialization - easiest way
model = init_chat_model("openai:gpt-4.1")

# Or with provider shorthand
model2 = init_chat_model("gpt-4.1")  # Defaults to OpenAI

# API key from environment (recommended)
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
model3 = init_chat_model("openai:gpt-4.1")
```
</python>

<typescript>
Universal model initialization:

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
</typescript>
</ex-basic-init>

<ex-providers>
<python>
Provider-specific class initialization:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# OpenAI
openai = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.7,
    max_tokens=1000,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Anthropic
anthropic = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0,
    max_tokens=2000,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# Google
google = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
```
</python>

<typescript>
Provider-specific class initialization:

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
</typescript>
</ex-providers>

<ex-invoke>
<python>
Basic invoke with string and messages:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# String input (converted to HumanMessage)
response = model.invoke("What is LangChain?")
print(response.content)

# Message array input
response2 = model.invoke([
    {"role": "user", "content": "Hello!"}
])
print(response2.content)
```
</python>

<typescript>
Basic invoke with string and messages:

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
</typescript>
</ex-invoke>

<ex-streaming>
<python>
Stream tokens in real-time:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing"):
    print(chunk.content, end="", flush=True)
```
</python>

<typescript>
Stream tokens in real-time:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Stream tokens as they arrive
const stream = await model.stream("Explain quantum computing");

for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```
</typescript>
</ex-streaming>

<ex-batch>
<python>
Batch process multiple inputs:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Process multiple inputs in parallel
results = model.batch([
    "What is AI?",
    "What is ML?",
    "What is LangChain?"
])

for i, result in enumerate(results):
    print(f"Answer {i + 1}: {result.content}")
```
</python>

<typescript>
Batch process multiple inputs:

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
</typescript>
</ex-batch>

<ex-multi-turn>
<python>
Multi-turn conversation with history:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Build conversation history
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
]

response1 = model.invoke(messages)
messages.append({"role": "assistant", "content": response1.content})

# Continue conversation
messages.append({"role": "user", "content": "What's its population?"})
response2 = model.invoke(messages)

print(response2.content)  # Knows we're talking about Paris
```
</python>

<typescript>
Multi-turn conversation with history:

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
</typescript>
</ex-multi-turn>

<ex-config>
<python>
Configure model parameters:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4.1",

    # Control randomness (0 = deterministic, 1 = creative)
    temperature=0.7,

    # Limit response length
    max_tokens=500,

    # Alternative sampling method
    top_p=0.9,

    # Penalize repetition
    frequency_penalty=0.5,
    presence_penalty=0.5,

    # Stop generation at these strings
    stop=["\n\n", "END"],

    # Timeout for requests (seconds)
    request_timeout=30,

    # Max retries on failure
    max_retries=3,
)
```
</python>

<typescript>
Configure model parameters:

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
</typescript>
</ex-config>

<ex-azure>
<python>
Azure OpenAI setup:

```python
from langchain_openai import AzureChatOpenAI
import os

azure = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-15-preview",
    deployment_name="your-deployment-name",
)
```
</python>

<typescript>
Azure OpenAI setup:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const azure = new ChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "your-instance-name",
  azureOpenAIApiDeploymentName: "your-deployment-name",
  azureOpenAIApiVersion: "2024-02-15-preview",
});
```
</typescript>
</ex-azure>

<ex-bedrock>
<python>
AWS Bedrock setup:

```python
from langchain_aws import ChatBedrock

# AWS credentials from environment or ~/.aws/credentials
bedrock = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    # Credentials automatically loaded from environment
)
```
</python>

<typescript>
AWS Bedrock setup:

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
</typescript>
</ex-bedrock>

<ex-model-select>
<python>
Dynamic model selection by task:

```python
from langchain.chat_models import init_chat_model

def get_model(task: str):
    model_map = {
        "reasoning": "openai:gpt-5",
        "fast": "google_genai:gemini-2.5-flash-lite",
        "vision": "openai:gpt-4.1",
        "long_context": "anthropic:claude-sonnet-4-5-20250929",
        "cost_effective": "openai:gpt-4.1-mini",
    }

    return init_chat_model(model_map.get(task, "openai:gpt-4.1"))

# Usage
reasoning_model = get_model("reasoning")
fast_model = get_model("fast")
```
</python>

<typescript>
Dynamic model selection by task:

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
</typescript>
</ex-model-select>

<ex-errors>
<python>
Handle API errors:

```python
from langchain.chat_models import init_chat_model
from openai import RateLimitError, AuthenticationError

model = init_chat_model("gpt-4.1")

try:
    response = model.invoke("Hello!")
    print(response.content)
except RateLimitError:
    print("Rate limit exceeded")
except AuthenticationError:
    print("Invalid API key")
except Exception as e:
    print(f"Error: {e}")
```
</python>

<typescript>
Handle API errors:

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
</typescript>
</ex-errors>

<ex-async>
<python>
Async invoke, stream, and batch:

```python
from langchain.chat_models import init_chat_model
import asyncio

async def main():
    model = init_chat_model("gpt-4.1")

    # Async invoke
    response = await model.ainvoke("Hello!")
    print(response.content)

    # Async stream
    async for chunk in model.astream("Explain AI"):
        print(chunk.content, end="", flush=True)

    # Async batch
    results = await model.abatch([
        "What is AI?",
        "What is ML?",
    ])
    for result in results:
        print(result.content)

asyncio.run(main())
```
</python>
</ex-async>

<ex-capabilities>
<python>
Check model capabilities:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Check if model supports features
print("Supports streaming:", hasattr(model, "stream"))
print("Supports tool calling:", hasattr(model, "bind_tools"))
print("Supports structured output:", hasattr(model, "with_structured_output"))
```
</python>

<typescript>
Check model capabilities:

```typescript
import { initChatModel } from "langchain";

const model = await initChatModel("gpt-4.1");

// Check if model supports features
console.log("Supports streaming:", typeof model.stream === "function");
console.log("Supports tool calling:", typeof model.bindTools === "function");
console.log("Supports structured output:", typeof model.withStructuredOutput === "function");
```
</typescript>
</ex-capabilities>

<boundaries>
What You CAN Configure:
- **Model Selection**: Any supported model from any provider
- **Temperature**: Control randomness (0-1)
- **Max Tokens**: Limit response length
- **Stop Sequences**: Define where to stop generation
- **Timeout/Retries**: Control request behavior
- **API Keys**: Per-model or from environment
- **Provider-specific Options**: Each provider has unique features

What You CANNOT Configure:
- **Model Training Data**: Models are pre-trained
- **Model Architecture**: Can't modify internal structure
- **Token Costs**: Set by provider
- **Rate Limits**: Set by provider (can manage with queues)
- **Model Capabilities**: Vision/tool support is model-specific
</boundaries>

<fix-api-key-not-found>
<python>
Fix missing API key:

```python
# Problem: Missing API key
model = init_chat_model("openai:gpt-4.1")
model.invoke("Hello")  # Error: API key not found

# Solution: Set environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
model = init_chat_model("openai:gpt-4.1")

# OR pass directly
from langchain_openai import ChatOpenAI
model = ChatOpenAI(
    model="gpt-4.1",
    api_key="sk-...",
)
```
</python>

<typescript>
Fix missing API key:

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
</typescript>
</fix-api-key-not-found>

<fix-model-name-typos>
<python>
Fix model name format:

```python
# Problem: Wrong model name
model = init_chat_model("gpt4")  # Error!

# Solution: Use correct format
model = init_chat_model("openai:gpt-4.1")
# Or provider shorthand
model2 = init_chat_model("gpt-4.1")
```
</python>

<typescript>
Fix model name format:

```typescript
// Problem: Wrong model name
const model = await initChatModel("gpt4"); // Error!

// Solution: Use correct format
const model = await initChatModel("openai:gpt-4.1");
// Or provider shorthand
const model2 = await initChatModel("gpt-4.1");
```
</typescript>
</fix-model-name-typos>

<fix-response-content-access>
<python>
Access response content correctly:

```python
# Problem: Wrong property access
response = model.invoke("Hello")
print(response)  # AIMessage object, not string

# Solution: Access .content property
print(response.content)  # "Hello! How can I help you?"

# Or convert to string
print(str(response))
```
</python>

<typescript>
Access response content correctly:

```typescript
// Problem: Wrong property access
const response = await model.invoke("Hello");
console.log(response); // AIMessage object, not string

// Solution: Access .content property
console.log(response.content); // "Hello! How can I help you?"

// Or use .toString()
console.log(response.toString());
```
</typescript>
</fix-response-content-access>

<fix-streaming-requires-iteration>
<python>
Iterate over stream correctly:

```python
# Problem: Not iterating stream
stream = model.stream("Hello")
print(stream)  # Generator object, not chunks

# Solution: Use for loop
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)
```
</python>

<typescript>
Iterate over stream correctly:

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
</typescript>
</fix-streaming-requires-iteration>

<fix-temperature-confusion>
<python>
Use correct temperature range:

```python
# Problem: Wrong temperature range
model = ChatOpenAI(
    temperature=10,  # Too high! Should be 0-1
)

# Solution: Use 0-1 range
deterministic = ChatOpenAI(temperature=0)  # Always same
balanced = ChatOpenAI(temperature=0.7)  # Default
creative = ChatOpenAI(temperature=1)  # Maximum randomness
```
</python>

<typescript>
Use correct temperature range:

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
</typescript>
</fix-temperature-confusion>

<fix-token-limits>
<python>
Handle context length limits:

```python
# Problem: Input + output exceeds model limit
long_text = "..." * 50000  # Very long text
model = init_chat_model("gpt-4.1")  # 128k context
model.invoke(long_text)  # May succeed

model2 = init_chat_model("gpt-4.1-mini")  # 16k context
model2.invoke(long_text)  # Error: context too long

# Solution: Check input length or use larger context model
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4.1")
tokens = enc.encode(long_text)
print(f"Input tokens: {len(tokens)}")

if len(tokens) > 100000:
    # Use Claude with 200k context
    model = init_chat_model("anthropic:claude-opus-4")
```
</python>

<typescript>
Handle context length limits:

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
</typescript>
</fix-token-limits>

<fix-sync-vs-async>
<python>
Use async methods in async context:

```python
# Problem: Using sync in async context
async def process():
    model = init_chat_model("gpt-4.1")
    response = model.invoke("Hello")  # Blocks async loop!

# Solution: Use async methods
async def process():
    model = init_chat_model("gpt-4.1")
    response = await model.ainvoke("Hello")  # Non-blocking

    async for chunk in model.astream("Hello"):
        print(chunk.content)
```
</python>
</fix-sync-vs-async>

<fix-provider-specific-features>
<typescript>
Check provider-specific feature compatibility:

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
</typescript>
</fix-provider-specific-features>

<documentation-links>
Python:
- [Chat Models Overview](https://docs.langchain.com/oss/python/langchain/models)
- [OpenAI Integration](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [Anthropic Integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic)
- [Google Integration](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)
- [All Chat Model Integrations](https://docs.langchain.com/oss/python/integrations/chat/index)
- [Model Providers Overview](https://docs.langchain.com/oss/python/integrations/providers/all_providers)

TypeScript:
- [Chat Models Overview](https://docs.langchain.com/oss/javascript/langchain/models)
- [OpenAI Integration](https://docs.langchain.com/oss/javascript/integrations/chat/openai)
- [Anthropic Integration](https://docs.langchain.com/oss/javascript/integrations/chat/anthropic)
- [Google Integration](https://docs.langchain.com/oss/javascript/integrations/chat/google_generative_ai)
- [All Chat Model Integrations](https://docs.langchain.com/oss/javascript/integrations/chat/index)
- [Model Providers Overview](https://docs.langchain.com/oss/javascript/integrations/providers/all_providers)
</documentation-links>
