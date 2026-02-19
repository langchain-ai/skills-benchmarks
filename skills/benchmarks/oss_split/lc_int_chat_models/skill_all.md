---
name: LangChain Chat Models Integration
description: "[LangChain] Guide to using chat model integrations in LangChain including OpenAI, Anthropic, Google, Azure, and Bedrock"
---

<oneliner>
Chat models provide a unified interface for interacting with various LLM providers, supporting features like tool calling, structured output, and streaming.
</oneliner>

<overview>
Key Concepts:
- **Chat Models**: Accept messages (with roles: system, user, assistant) and return generated responses
- **Providers**: Different AI companies offering LLM APIs (OpenAI, Anthropic, Google, Azure, Bedrock, etc.)
- **Tool Calling**: Models can invoke functions/tools based on user queries
- **Streaming**: Real-time token-by-token response generation
- **Structured Output**: Models can return responses in specific formats (JSON, Pydantic/Zod schemas)
</overview>

<provider-selection>

| Provider | Best For | Models | Python Package | TypeScript Package |
|----------|----------|--------|----------------|-------------------|
| **OpenAI** | General purpose, function calling | gpt-4, gpt-4-turbo | `langchain-openai` | `@langchain/openai` |
| **Anthropic** | Long context, safety | claude-3-opus, claude-3-sonnet | `langchain-anthropic` | `@langchain/anthropic` |
| **Google GenAI** | Multimodal, free tier | gemini-pro | `langchain-google-genai` | `@langchain/google-genai` |
| **Azure OpenAI** | Enterprise, compliance | gpt-4 (Azure deployed) | `langchain-openai` | `@langchain/openai` |
| **AWS Bedrock** | AWS ecosystem | claude, llama, titan | `langchain-aws` | `@langchain/aws` |
| **Google Vertex AI** | GCP ecosystem | gemini-pro | `langchain-google-vertexai` | `@langchain/google-vertexai` |

</provider-selection>

<when-to-choose-provider>
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
</when-to-choose-provider>

<ex-openai>
<python>

Initialize OpenAI chat model and stream responses.

```python
from langchain_openai import ChatOpenAI
import os

# Basic initialization
model = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY"),  # Optional if set in env
)

# Invoke the model
response = model.invoke([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is LangChain?"}
])

print(response.content)

# Streaming responses
for chunk in model.stream("Tell me a story"):
    print(chunk.content, end="", flush=True)
```

</python>

<typescript>

Initialize OpenAI chat model and stream responses.

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

</typescript>
</ex-openai>

<ex-anthropic>
<python>

Anthropic Claude with tool binding.

```python
from langchain_anthropic import ChatAnthropic
import os

model = ChatAnthropic(
    model="claude-3-opus-20240229",
    temperature=0.7,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=1024,
)

# Long context usage
response = model.invoke([
    {"role": "user", "content": "Analyze this long document..."}
])

# With tool use
from langchain_core.tools import tool

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"The weather in {location} is sunny"

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("What's the weather in SF?")
```

</python>

<typescript>

Anthropic Claude with tool binding.

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

</typescript>
</ex-anthropic>

<ex-azure>
<python>

Configure Azure OpenAI with deployment settings.

```python
from langchain_openai import AzureChatOpenAI
import os

model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="gpt-4-deployment",
    api_version="2024-02-01",
    temperature=0.7,
)

response = model.invoke("Hello, how are you?")
print(response.content)
```

</python>

<typescript>

Configure Azure OpenAI with deployment settings.

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

</typescript>
</ex-azure>

<ex-bedrock>
<python>

Set up AWS Bedrock with Claude model.

```python
from langchain_aws import ChatBedrock
import boto3

model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1",
    credentials_profile_name="default",  # Or use boto3 session
)

response = model.invoke("What is AWS Bedrock?")
print(response.content)
```

</python>

<typescript>

Set up AWS Bedrock with Claude model.

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

</typescript>
</ex-bedrock>

<ex-google>
<python>

Initialize Google Gemini model.

```python
from langchain_google_genai import ChatGoogleGenerativeAI
import os

model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

response = model.invoke("Explain quantum computing")
print(response.content)
```

</python>

<typescript>

Initialize Google Gemini model.

```typescript
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

const model = new ChatGoogleGenerativeAI({
  modelName: "gemini-pro",
  apiKey: process.env.GOOGLE_API_KEY,
  temperature: 0.7,
});

const response = await model.invoke("Explain quantum computing");
```

</typescript>
</ex-google>

<ex-init>
<python>

Provider-agnostic model initialization.

```python
from langchain.chat_models import init_chat_model

# Automatically select model based on environment
model = init_chat_model(
    "gpt-4",
    model_provider="openai",
    temperature=0.7,
)

# Or with Bedrock
bedrock_model = init_chat_model(
    "anthropic.claude-3-sonnet-20240229-v1:0",
    model_provider="bedrock",
)
```

</python>

<typescript>

Provider-agnostic model initialization.

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

</typescript>
</ex-init>

<ex-tools>
<python>

Define and bind tools using decorators.

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Define a tool using decorator
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location.

    Args:
        location: The city name
    """
    return f"The weather in {location} is sunny and 72°F"

# Or define with Pydantic
class WeatherInput(BaseModel):
    location: str = Field(description="The city name")

@tool("get_weather", args_schema=WeatherInput)
def get_weather_pydantic(location: str) -> str:
    """Get the current weather for a location."""
    return f"The weather in {location} is sunny and 72°F"

# Bind tools to model
model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke("What's the weather in San Francisco?")
print(response.tool_calls)  # Model will suggest calling the weather tool
```

</python>

<typescript>

Define and bind tools with Zod schemas.

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

</typescript>
</ex-tools>

<ex-structured>
<python>

Generate structured output with Pydantic schema.

```python
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

class Person(BaseModel):
    name: str = Field(description="Person's name")
    age: int = Field(description="Person's age")
    hobbies: List[str] = Field(description="List of hobbies")

model = ChatOpenAI(model="gpt-4")
structured_model = model.with_structured_output(Person)

response = structured_model.invoke(
    "Tell me about a person named Alice who is 30 years old and likes reading"
)
print(response)  # Returns Person object
print(f"Name: {response.name}, Age: {response.age}")
```
</python>
</ex-structured>

<boundaries>
What You CAN Do:
- **Initialize any supported chat model provider** - Install required packages and configure with API keys
- **Configure model parameters** - Set temperature, max_tokens, top_p, frequency_penalty
- **Use models for text generation** - Send messages, receive responses, stream tokens
- **Implement tool/function calling** - Bind tools to models that support it
- **Generate structured output** - Use Pydantic/Zod schemas for type-safe responses
- **Switch between providers** - Use init_chat_model for provider-agnostic code

What You CANNOT Do:
- **Create new model providers** - Must use existing LangChain integrations
- **Bypass provider requirements** - Cannot skip required authentication credentials
- **Modify model capabilities** - Cannot add tool calling to models that don't support it
- **Access models without proper setup** - Cannot use providers without valid API keys
</boundaries>

<fix-api-keys>
<python>

Use environment variables for API keys.

```python
# BAD: Hardcoding API keys
model = ChatOpenAI(
    api_key="sk-..."  # Never commit this!
)

# GOOD: Use environment variables
import os
model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# BETTER: Let LangChain auto-detect from environment
model = ChatOpenAI()  # Reads OPENAI_API_KEY automatically
```
</python>

<typescript>

Use environment variables for API keys.

```typescript
// BAD: Hardcoding API keys
const model = new ChatOpenAI({
  openAIApiKey: "sk-..."  // Never commit this!
});

// GOOD: Use environment variables
const model = new ChatOpenAI({
  openAIApiKey: process.env.OPENAI_API_KEY
});
```
</typescript>
</fix-api-keys>

<fix-azure-configuration>
<python>

Updated Azure configuration syntax.

```python
# OLD WAY (deprecated)
from langchain_openai import AzureChatOpenAI
model = AzureChatOpenAI(
    deployment_name="gpt-4",
    openai_api_base="https://my-instance.openai.azure.com/",
)

# NEW WAY
model = AzureChatOpenAI(
    azure_endpoint="https://my-instance.openai.azure.com/",
    azure_deployment="gpt-4",
    api_version="2024-02-01",
)
```
</python>

<typescript>

Complete Azure configuration with all fields.

```typescript
// INCOMPLETE: Missing required fields
const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
});

// COMPLETE: All required fields
const model = new AzureChatOpenAI({
  azureOpenAIApiKey: process.env.AZURE_OPENAI_API_KEY,
  azureOpenAIApiInstanceName: "my-instance",
  azureOpenAIApiDeploymentName: "gpt-4-deployment",
  azureOpenAIApiVersion: "2024-02-01",
});
```
</typescript>
</fix-azure-configuration>

<fix-message-formats>
<python>

Dict and message class formats both work.

```python
# Different message formats that all work
from langchain_core.messages import HumanMessage, SystemMessage

# Dictionary format
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"}
]

# Message class format
messages = [
    SystemMessage(content="You are helpful"),
    HumanMessage(content="Hello")
]

# Both work!
response = model.invoke(messages)
```
</python>
</fix-message-formats>

<fix-tool-calling-support>
<python>

Check model supports tool calling.

```python
# Not all models support tool calling
model = ChatOpenAI(model="gpt-3.5-turbo-instruct")
# This older model doesn't support tools!

# Use models with tool support
model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([my_tool])
```
</python>

<typescript>

Check model supports tool calling.

```typescript
// Not all models support tool calling
const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo-instruct" });
// This older model doesn't support tools!

// Use models with tool support
const model = new ChatOpenAI({ modelName: "gpt-4" });
const withTools = model.bindTools([myTool]);
```
</typescript>
</fix-tool-calling-support>

<fix-import-errors>
<python>

Use provider-specific packages for imports.

```python
# WRONG: Using old community package
from langchain.chat_models import ChatOpenAI  # Deprecated!

# CORRECT: Use provider-specific package
from langchain_openai import ChatOpenAI
```
</python>
</fix-import-errors>

<fix-context-window-limits>
<python>

Choose models with sufficient context window.

```python
# Exceeding context limits
model = ChatOpenAI(model="gpt-3.5-turbo")  # 4k context
long_text = "..." * 10000
model.invoke(long_text)  # Will fail!

# Use appropriate models for long context
model = ChatOpenAI(model="gpt-4-turbo")  # 128k context
# OR
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-opus-20240229")  # 200k context
```
</python>

<typescript>

Choose models with sufficient context window.

```typescript
// Exceeding context limits
const model = new ChatOpenAI({ modelName: "gpt-3.5-turbo" }); // 4k context
const longText = "...".repeat(10000);
await model.invoke(longText); // Will fail!

// Use appropriate models for long context
const model = new ChatOpenAI({ modelName: "gpt-4-turbo" }); // 128k context
// OR
const model = new ChatAnthropic({
  modelName: "claude-3-opus-20240229" // 200k context
});
```
</typescript>
</fix-context-window-limits>

<fix-streaming-confusion>
<python>

Iterate over stream or use invoke.

```python
# Wrong: Treating stream like regular response
response = model.stream("Hello")
print(response.content)  # AttributeError!

# Correct: Iterate over stream
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)

# OR use invoke for complete response
response = model.invoke("Hello")
print(response.content)
```
</python>

<typescript>

Iterate over stream or use invoke.

```typescript
// Mixing streaming and non-streaming incorrectly
const response = await model.stream("Hello");
console.log(response.content); // Won't work! response is an async iterable

// Handle streaming properly
const stream = await model.stream("Hello");
for await (const chunk of stream) {
  console.log(chunk.content);
}

// OR use invoke for non-streaming
const response = await model.invoke("Hello");
console.log(response.content);
```
</typescript>
</fix-streaming-confusion>

<fix-bedrock-model-ids>
<python>

Use full Bedrock model ID format.

```python
# Wrong model ID format
model = ChatBedrock(model_id="claude-3-sonnet")  # Won't work!

# Correct: Full Bedrock model ID
model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)
```
</python>
</fix-bedrock-model-ids>

<fix-model-name-variations>
<typescript>

Provider-specific model naming conventions.

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
</typescript>
</fix-model-name-variations>

<fix-rate-limits>
<typescript>

Configure retries for rate limit handling.

```typescript
// No retry logic
const model = new ChatOpenAI();
const response = await model.invoke("Hello"); // May fail on rate limit

// Configure retries
const model = new ChatOpenAI({
  maxRetries: 3,
  timeout: 30000, // 30 seconds
});
```
</typescript>
</fix-rate-limits>

<fix-pydantic-version>
<python>

Ensure Pydantic v2 is installed.

```python
# Some LangChain versions require Pydantic v2
# May cause errors with Pydantic v1
from pydantic import BaseModel

class Output(BaseModel):
    name: str

# Ensure Pydantic v2 is installed
# pip install "pydantic>=2.0"
```
</python>
</fix-pydantic-version>

<links>
Python:
- [Chat Models Overview](https://python.langchain.com/docs/integrations/chat/)
- [OpenAI Integration](https://python.langchain.com/docs/integrations/chat/openai)
- [Anthropic Integration](https://python.langchain.com/docs/integrations/chat/anthropic)
- [Azure OpenAI Integration](https://python.langchain.com/docs/integrations/chat/azure_chat_openai)
- [AWS Bedrock Integration](https://python.langchain.com/docs/integrations/chat/bedrock)
- [Google GenAI Integration](https://python.langchain.com/docs/integrations/chat/google_generative_ai)

TypeScript:
- [Chat Models Overview](https://js.langchain.com/docs/integrations/chat/)
- [OpenAI Integration](https://js.langchain.com/docs/integrations/chat/openai)
- [Anthropic Integration](https://js.langchain.com/docs/integrations/chat/anthropic)
- [Azure OpenAI Integration](https://js.langchain.com/docs/integrations/chat/azure)
- [AWS Bedrock Integration](https://js.langchain.com/docs/integrations/chat/bedrock)
- [Google GenAI Integration](https://js.langchain.com/docs/integrations/chat/google_generativeai)
</links>

<installation>
Python:
```bash
pip install langchain-openai langchain-anthropic langchain-aws langchain-google-genai langchain-google-vertexai
```

TypeScript:
```bash
npm install @langchain/openai @langchain/anthropic @langchain/aws @langchain/google-genai @langchain/google-vertexai
```
</installation>
