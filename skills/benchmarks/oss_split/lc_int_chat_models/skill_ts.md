---
name: LangChain Chat Models Integration (TypeScript)
description: "[LangChain] Guide to using chat model integrations in LangChain including OpenAI, Anthropic, Google, Azure, and Bedrock"
---

<overview>
Chat models in LangChain provide a unified interface for interacting with various LLM providers. They take a sequence of messages as input and return AI-generated messages as output. Chat models support features like tool calling, structured output, and streaming.

**Key Concepts:**
- **Chat Models**: Accept messages (with roles: system, user, assistant) and return generated responses
- **Providers**: Different AI companies offering LLM APIs (OpenAI, Anthropic, Google, Azure, Bedrock, etc.)
- **Tool Calling**: Models can invoke functions/tools based on user queries
- **Streaming**: Real-time token-by-token response generation
- **Structured Output**: Models can return responses in specific formats (JSON, TypeScript types)
</overview>

<provider-selection>
| Provider | Best For | Model Examples | Package | Key Features |
|----------|----------|----------------|---------|--------------|
| **OpenAI** | General purpose, function calling | gpt-4, gpt-4-turbo, gpt-3.5-turbo | `@langchain/openai` | Strong function calling, vision, fast |
| **Anthropic** | Long context, safety, analysis | claude-3-opus, claude-3-sonnet, claude-3-haiku | `@langchain/anthropic` | 200k context, tool use, prompt caching |
| **Google GenAI** | Multimodal, free tier | gemini-pro, gemini-pro-vision | `@langchain/google-genai` | Vision, free tier available |
| **Azure OpenAI** | Enterprise, compliance | gpt-4, gpt-35-turbo (Azure deployed) | `@langchain/openai` | Enterprise SLAs, data residency |
| **AWS Bedrock** | AWS ecosystem, variety | claude, llama, titan models | `@langchain/aws` | Multiple models, AWS integration |
| **Google Vertex AI** | GCP ecosystem, enterprise | gemini-pro, palm models | `@langchain/google-vertexai` | Enterprise features, GCP integration |
</provider-selection>

<when-to-choose>
**Choose OpenAI if:**
- You need strong function/tool calling capabilities
- You want fast response times
- You're building general-purpose applications

**Choose Anthropic if:**
- You need very long context windows (100k-200k tokens)
- Safety and constitutional AI principles are important
- You want high-quality analysis and reasoning

**Choose Azure OpenAI if:**
- You need enterprise SLAs and support
- Data residency and compliance are critical
- You're already using Microsoft Azure

**Choose AWS Bedrock if:**
- You're in the AWS ecosystem
- You want access to multiple model providers
- You need variety (Claude, Llama, Titan, etc.)

**Choose Google (GenAI or Vertex) if:**
- You need strong multimodal capabilities
- You're in the GCP ecosystem
- You want access to Gemini models
</when-to-choose>

<ex-openai-chat-model>
```typescript
import { ChatOpenAI } from "@langchain/openai";

// Basic initialization
const model = new ChatOpenAI({
  modelName: "gpt-4",
  temperature: 0.7,
  openAIApiKey: process.env.OPENAI_API_KEY, // Optional if set in env
});

// Invoke the model
const response = await model.invoke([
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "What is LangChain?" }
]);

console.log(response.content);

// Streaming responses
const stream = await model.stream("Tell me a story");
for await (const chunk of stream) {
  process.stdout.write(chunk.content);
}
```
</ex-openai-chat-model>

<ex-anthropic-chat-model>
```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic({
  modelName: "claude-3-opus-20240229",
  temperature: 0.7,
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  maxTokens: 1024,
});

// Long context usage
const response = await model.invoke([
  { role: "user", content: "Analyze this long document..." }
]);

// With tool use
const modelWithTools = model.bindTools([
  {
    name: "get_weather",
    description: "Get weather for a location",
    input_schema: {
      type: "object",
      properties: {
        location: { type: "string" }
      },
      required: ["location"]
    }
  }
]);
```
</ex-anthropic-chat-model>

<ex-azure-openai-chat-model>
```typescript
import { AzureChatOpenAI } from "@langchain/openai";

const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: process.env.AZURE_OPENAI_API_INSTANCE_NAME,
  azureOpenAIApiDeploymentName: process.env.AZURE_OPENAI_API_DEPLOYMENT_NAME,
  azureOpenAIApiVersion: "2024-02-01",
  temperature: 0.7,
});

const response = await model.invoke("Hello, how are you?");
```
</ex-azure-openai-chat-model>

<ex-aws-bedrock-chat-model>
```typescript
import { ChatBedrockConverse } from "@langchain/aws";

const model = new ChatBedrockConverse({
  model: "anthropic.claude-3-sonnet-20240229-v1:0",
  region: "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});

const response = await model.invoke("What is AWS Bedrock?");
```
</ex-aws-bedrock-chat-model>

<ex-google-generative-ai>
```typescript
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

const model = new ChatGoogleGenerativeAI({
  modelName: "gemini-pro",
  apiKey: process.env.GOOGLE_API_KEY,
  temperature: 0.7,
});

const response = await model.invoke("Explain quantum computing");
```
</ex-google-generative-ai>

<ex-using-initchatmodel>
```typescript
import { initChatModel } from "langchain/chat_models/universal";

// Automatically select model based on environment
const model = await initChatModel("gpt-4", {
  modelProvider: "openai",
  temperature: 0.7,
});

// Or with Bedrock
const bedrockModel = await initChatModel(
  "anthropic.claude-3-sonnet-20240229-v1:0",
  { modelProvider: "bedrock" }
);
```
</ex-using-initchatmodel>

<ex-tool-calling>
```typescript
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";
import { tool } from "@langchain/core/tools";

// Define a tool
const weatherTool = tool(
  async ({ location }) => {
    return `The weather in ${location} is sunny and 72°F`;
  },
  {
    name: "get_weather",
    description: "Get the current weather for a location",
    schema: z.object({
      location: z.string().describe("The city name"),
    }),
  }
);

// Bind tools to model
const model = new ChatOpenAI({
  modelName: "gpt-4",
}).bindTools([weatherTool]);

const response = await model.invoke("What's the weather in San Francisco?");
console.log(response.tool_calls); // Model will suggest calling the weather tool
```
</ex-tool-calling>

<boundaries>
**What Agents CAN Do:**
- Initialize any supported chat model provider
- Install required packages (`@langchain/openai`, `@langchain/anthropic`, etc.)
- Configure models with API keys and parameters
- Set temperature, max tokens, top_p, frequency_penalty
- Configure streaming, timeout, and retry settings
- Send messages and receive responses
- Stream responses token-by-token
- Use system prompts and multi-turn conversations
- Bind tools to models that support it
- Parse tool call responses
- Execute tools and return results
- Use initChatModel for provider-agnostic code
- Change providers by updating configuration

**What Agents CANNOT Do:**
- Create new model providers (must use existing LangChain integrations)
- Bypass provider requirements (cannot use Azure OpenAI without deployment names)
- Add tool calling to models that don't support it
- Extend context windows beyond provider limits
- Use providers without valid API keys
- Bypass billing/quota limits
</boundaries>

<fix-api-keys-and-environment-variables>
```typescript
// WRONG: BAD: Hardcoding API keys
const model = new ChatOpenAI({
  openAIApiKey: "sk-..."  // Never commit this!
});

// CORRECT: GOOD: Use environment variables
const model = new ChatOpenAI({
  openAIApiKey: process.env.OPENAI_API_KEY
});
```

**Fix**: Always use environment variables or secure key management systems.
</fix-api-keys-and-environment-variables>

<fix-azure-openai-configuration-complexity>
```typescript
// WRONG: INCOMPLETE: Missing required fields
const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
});

// CORRECT: COMPLETE: All required fields
const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "my-instance",
  azureOpenAIApiDeploymentName: "gpt-4-deployment",
  azureOpenAIApiVersion: "2024-02-01",
});
```

**Fix**: Azure requires instance name, deployment name, and API version.
</fix-azure-openai-configuration-complexity>

<fix-model-name-variations>
```typescript
// Different providers have different model naming conventions
// OpenAI
const openai = new ChatOpenAI({ modelName: "gpt-4" });

// Bedrock (includes provider prefix)
const bedrock = new ChatBedrockConverse({
  model: "anthropic.claude-3-sonnet-20240229-v1:0"
});

// Anthropic (direct model name)
const anthropic = new ChatAnthropic({
  modelName: "claude-3-opus-20240229"
});
```

**Fix**: Check provider documentation for correct model identifiers.
</fix-model-name-variations>

<fix-tool-calling-support>
```typescript
// WRONG: Not all models support tool calling
const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo-instruct" });
// This older model doesn't support tools!

// CORRECT: Use models with tool support
const model = new ChatOpenAI({ modelName: "gpt-4" });
const withTools = model.bindTools([myTool]);
```

**Fix**: Verify model supports function/tool calling before binding tools. GPT-4, GPT-3.5-turbo, Claude 3, and Gemini Pro all support tools.
</fix-tool-calling-support>

<fix-rate-limits-and-quotas>
```typescript
// WRONG: No retry logic
const model = new ChatOpenAI();
const response = await model.invoke("Hello"); // May fail on rate limit

// CORRECT: Configure retries
const model = new ChatOpenAI({
  maxRetries: 3,
  timeout: 30000, // 30 seconds
});
```

**Fix**: Configure retry logic and handle rate limit errors gracefully.
</fix-rate-limits-and-quotas>

<fix-context-window-limits>
```typescript
// WRONG: Exceeding context limits
const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo" }); // 4k context
const longText = "...".repeat(10000);
await model.invoke(longText); // Will fail!

// CORRECT: Use appropriate models for long context
const model = new ChatOpenAI({ modelName: "gpt-4-turbo" }); // 128k context
// OR
const model = new ChatAnthropic({
  modelName: "claude-3-opus-20240229" // 200k context
});
```

**Fix**: Choose models with appropriate context windows for your use case.
</fix-context-window-limits>

<fix-streaming-vs-non-streaming>
```typescript
// WRONG: Mixing streaming and non-streaming incorrectly
const response = await model.stream("Hello");
console.log(response.content); // Won't work! response is an async iterable

// CORRECT: Handle streaming properly
const stream = await model.stream("Hello");
for await (const chunk of stream) {
  console.log(chunk.content);
}

// OR use invoke for non-streaming
const response = await model.invoke("Hello");
console.log(response.content);
```

**Fix**: Use `invoke()` for complete responses, `stream()` for token-by-token.
</fix-streaming-vs-non-streaming>

<documentation-links>
**Official Documentation:**
- [LangChain JS Chat Models Overview](https://js.langchain.com/docs/integrations/chat/)
- [OpenAI Integration](https://js.langchain.com/docs/integrations/chat/openai)
- [Anthropic Integration](https://js.langchain.com/docs/integrations/chat/anthropic)
- [Azure OpenAI Integration](https://js.langchain.com/docs/integrations/chat/azure)
- [AWS Bedrock Integration](https://js.langchain.com/docs/integrations/chat/bedrock)
- [Google GenAI Integration](https://js.langchain.com/docs/integrations/chat/google_generativeai)

**Provider Documentation:**
- [OpenAI API Docs](https://platform.openai.com/docs/introduction)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [Google AI Studio](https://ai.google.dev/)

**Package Installation:**
```bash
# OpenAI
npm install @langchain/openai

# Anthropic
npm install @langchain/anthropic

# AWS (Bedrock)
npm install @langchain/aws

# Google
npm install @langchain/google-genai
npm install @langchain/google-vertexai
```
</documentation-links>
