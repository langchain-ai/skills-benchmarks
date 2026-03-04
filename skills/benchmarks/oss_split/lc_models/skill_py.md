---
name: langchain-models-py
description: "[LangChain] Initialize and use LangChain chat models - includes provider selection (OpenAI, Anthropic, Google), model configuration, and invocation patterns"
---

<overview>
Chat models are the core of LangChain applications. They take messages as input and return AI-generated messages as output. LangChain provides a unified interface across multiple providers (OpenAI, Anthropic, Google, etc.).

**Key Concepts:**
- **init_chat_model()**: Universal initialization for any provider
- **Provider-specific classes**: Direct initialization (ChatOpenAI, ChatAnthropic, etc.)
- **Messages**: Structured input/output format (HumanMessage, AIMessage, etc.)
- **Invocation patterns**: invoke(), stream(), batch()
</overview>

<when-to-use-each-provider>

| Provider | Best For | Models | Strengths |
|----------|----------|--------|-----------|
| OpenAI | General purpose, reasoning | GPT-4.1, GPT-5 | Strong reasoning, large context |
| Anthropic | Safety, analysis | Claude Sonnet/Opus | Safety, long context, vision |
| Google | Multimodal, speed | Gemini 2.5 | Fast, multimodal, cost-effective |
| AWS Bedrock | Enterprise, compliance | Multiple providers | Security, compliance, variety |
| Azure OpenAI | Enterprise OpenAI | GPT models | Enterprise features, SLAs |

</when-to-use-each-provider>

<model-selection>

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Complex reasoning | GPT-5, Claude Opus | Best logical capabilities |
| Fast responses | Gemini Flash, GPT-4.1-mini | Low latency |
| Vision tasks | GPT-4.1, Claude Sonnet, Gemini | Multimodal support |
| Long context | Claude Opus, Gemini | 100k+ token windows |
| Cost-effective | GPT-4.1-mini, Gemini Flash | Lower pricing |
| Enterprise/compliance | Azure OpenAI, AWS Bedrock | Security features |

</model-selection>

<initialization-methods>

| Method | When to Use | Example |
|--------|-------------|---------|
| `init_chat_model("provider:model")` | Quick switching between providers | `init_chat_model("openai:gpt-4.1")` |
| Provider class | Need provider-specific features | `ChatOpenAI(model="gpt-4.1")` |
| With configuration | Custom parameters needed | Temperature, max tokens, etc. |

</initialization-methods>

<ex-basic-model-initialization>
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
</ex-basic-model-initialization>

<ex-provider-specific-initialization>
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
</ex-provider-specific-initialization>

<ex-simple-invocation>
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
</ex-simple-invocation>

<ex-streaming-responses>
```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing"):
    print(chunk.content, end="", flush=True)
```
</ex-streaming-responses>

<ex-batch-processing>
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
</ex-batch-processing>

<ex-multi-turn-conversation>
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
</ex-multi-turn-conversation>

<ex-model-configuration-options>
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
</ex-model-configuration-options>

<ex-azure-openai>
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
</ex-azure-openai>

<ex-aws-bedrock>
```python
from langchain_aws import ChatBedrock

# AWS credentials from environment or ~/.aws/credentials
bedrock = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    # Credentials automatically loaded from environment
)
```
</ex-aws-bedrock>

<ex-model-selection-helper>
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
</ex-model-selection-helper>

<ex-error-handling>
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
</ex-error-handling>

<ex-async-invocation>
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
</ex-async-invocation>

<ex-checking-model-capabilities>
```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-4.1")

# Check if model supports features
print("Supports streaming:", hasattr(model, "stream"))
print("Supports tool calling:", hasattr(model, "bind_tools"))
print("Supports structured output:", hasattr(model, "with_structured_output"))
```
</ex-checking-model-capabilities>

<boundaries>
### What You CAN Configure

* Model Selection**: Any supported model from any provider
* Temperature**: Control randomness (0-1)
* Max Tokens**: Limit response length
* Stop Sequences**: Define where to stop generation
* Timeout/Retries**: Control request behavior
* API Keys**: Per-model or from environment
* Provider-specific Options**: Each provider has unique features

### What You CANNOT Configure

* Model Training Data**: Models are pre-trained
* Model Architecture**: Can't modify internal structure
* Token Costs**: Set by provider
* Rate Limits**: Set by provider (can manage with queues)
* Model Capabilities**: Vision/tool support is model-specific
</boundaries>

<fix-api-key-not-found>
```python
# WRONG: Problem: Missing API key
model = init_chat_model("openai:gpt-4.1")
model.invoke("Hello")  # Error: API key not found

# CORRECT: Solution: Set environment variable
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
</fix-api-key-not-found>

<fix-model-name-typos>
```python
# WRONG: Problem: Wrong model name
model = init_chat_model("gpt4")  # Error!

# CORRECT: Solution: Use correct format
model = init_chat_model("openai:gpt-4.1")
# Or provider shorthand
model2 = init_chat_model("gpt-4.1")
```
</fix-model-name-typos>

<fix-response-content-access>
```python
# WRONG: Problem: Wrong property access
response = model.invoke("Hello")
print(response)  # AIMessage object, not string

# CORRECT: Solution: Access .content property
print(response.content)  # "Hello! How can I help you?"

# Or convert to string
print(str(response))
```
</fix-response-content-access>

<fix-streaming-requires-iteration>
```python
# WRONG: Problem: Not iterating stream
stream = model.stream("Hello")
print(stream)  # Generator object, not chunks

# CORRECT: Solution: Use for loop
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)
```
</fix-streaming-requires-iteration>

<fix-temperature-confusion>
```python
# WRONG: Problem: Wrong temperature range
model = ChatOpenAI(
    temperature=10,  # Too high! Should be 0-1
)

# CORRECT: Solution: Use 0-1 range
deterministic = ChatOpenAI(temperature=0)  # Always same
balanced = ChatOpenAI(temperature=0.7)  # Default
creative = ChatOpenAI(temperature=1)  # Maximum randomness
```
</fix-temperature-confusion>

<fix-token-limits>
```python
# WRONG: Problem: Input + output exceeds model limit
long_text = "..." * 50000  # Very long text
model = init_chat_model("gpt-4.1")  # 128k context
model.invoke(long_text)  # May succeed

model2 = init_chat_model("gpt-4.1-mini")  # 16k context
model2.invoke(long_text)  # Error: context too long

# CORRECT: Solution: Check input length or use larger context model
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4.1")
tokens = enc.encode(long_text)
print(f"Input tokens: {len(tokens)}")

if len(tokens) > 100000:
    # Use Claude with 200k context
    model = init_chat_model("anthropic:claude-opus-4")
```
</fix-token-limits>

<fix-sync-vs-async-confusion>
```python
# WRONG: Problem: Using sync in async context
async def process():
    model = init_chat_model("gpt-4.1")
    response = model.invoke("Hello")  # Blocks async loop!

# CORRECT: Solution: Use async methods
async def process():
    model = init_chat_model("gpt-4.1")
    response = await model.ainvoke("Hello")  # Non-blocking

    async for chunk in model.astream("Hello"):
        print(chunk.content)
```
</fix-sync-vs-async-confusion>

<links>
- [Chat Models Overview](https://docs.langchain.com/oss/python/langchain/models)
- [OpenAI Integration](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [Anthropic Integration](https://docs.langchain.com/oss/python/integrations/chat/anthropic)
- [Google Integration](https://docs.langchain.com/oss/python/integrations/chat/google_generative_ai)
- [All Chat Model Integrations](https://docs.langchain.com/oss/python/integrations/chat/index)
- [Model Providers Overview](https://docs.langchain.com/oss/python/integrations/providers/all_providers)
</links>
