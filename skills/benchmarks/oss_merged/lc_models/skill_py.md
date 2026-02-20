---
name: LangChain Models & Streaming (Python)
description: "INVOKE THIS SKILL when configuring chat models OR implementing streaming. Covers init_chat_model, provider setup (OpenAI/Anthropic/Azure), streaming tokens, and multimodal inputs. CRITICAL: Fixes for messages mode tuple unpacking (token, metadata), sync vs async streaming, and multi-mode handling."
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

| Provider | Best For | Models | Package |
|----------|----------|--------|---------|
| **OpenAI** | General purpose, reasoning | GPT-4.1, GPT-5 | `langchain-openai` |
| **Anthropic** | Safety, analysis, long context | Claude Sonnet/Opus | `langchain-anthropic` |
| **Google** | Multimodal, speed | Gemini 2.5 | `langchain-google-genai` |
| **Azure OpenAI** | Enterprise, compliance | GPT models | `langchain-openai` |
| **AWS Bedrock** | Enterprise, variety | Multiple providers | `langchain-aws` |

</provider-selection>

<stream-mode-selection>

| Mode | Use When | Returns |
|------|----------|---------|
| `"values"` | Need full state after each step | Complete state dict |
| `"updates"` | Need only what changed | State deltas |
| `"messages"` | Need LLM token stream | (token, metadata) tuples |
| `"custom"` | Need custom progress signals | User-defined data |

</stream-mode-selection>

---

## Model Initialization

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
)
```
</ex-aws-bedrock>

---

## Invocation Patterns

<ex-simple-invocation>
```python
model = init_chat_model("gpt-4.1")

# String input (converted to HumanMessage)
response = model.invoke("What is LangChain?")
print(response.content)

# Message array input
response2 = model.invoke([
    {"role": "user", "content": "Hello!"}
])
```
</ex-simple-invocation>

<ex-multi-turn-conversation>
```python
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
# Model knows we're talking about Paris
```
</ex-multi-turn-conversation>

---

## Streaming

<ex-basic-token-streaming>
```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1")

# Stream tokens as they arrive
for chunk in model.stream("Explain quantum computing in simple terms"):
    print(chunk.content, end="", flush=True)
```
</ex-basic-token-streaming>

<ex-agent-progress-streaming>
```python
from langchain.agents import create_agent

agent = create_agent(model="gpt-4.1", tools=[search_tool])

# Stream agent steps with "updates" mode
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Search for AI news"}]},
    stream_mode=["updates"],
):
    print(f"Step: {chunk}")
```
</ex-agent-progress-streaming>

<ex-combined-streaming>
```python
# Stream both LLM tokens AND agent progress
for mode, chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Research LangChain"}]},
    stream_mode=["updates", "messages"],
):
    if mode == "messages":
        # LLM token stream
        token, metadata = chunk
        if token.content:
            print(token.content, end="", flush=True)
    elif mode == "updates":
        # Agent step updates
        print(f"\nStep update: {chunk}")
```
</ex-combined-streaming>

<ex-async-streaming>
```python
import asyncio

async def main():
    model = init_chat_model("gpt-4.1")

    async for chunk in model.astream("Explain AI"):
        print(chunk.content, end="", flush=True)

asyncio.run(main())
```
</ex-async-streaming>

---

## Multimodal

<ex-image-input>
```python
from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage
import base64

model = ChatOpenAI(model="gpt-4.1")

# From URL
message = HumanMessage(content_blocks=[
    {"type": "text", "text": "What's in this image?"},
    {"type": "image", "url": "https://example.com/photo.jpg"},
])

# From base64
with open("./photo.jpg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Describe this image"},
    {"type": "image", "base64": base64_image, "mime_type": "image/jpeg"},
])

response = model.invoke([message])
```
</ex-image-input>

<ex-pdf-document-analysis>
```python
from langchain_anthropic import ChatAnthropic
import base64

model = ChatAnthropic(model="claude-sonnet-4-5-20250929")

with open("./document.pdf", "rb") as pdf_file:
    base64_pdf = base64.b64encode(pdf_file.read()).decode("utf-8")

message = HumanMessage(content_blocks=[
    {"type": "text", "text": "Summarize this PDF document"},
    {"type": "file", "base64": base64_pdf, "mime_type": "application/pdf"},
])

response = model.invoke([message])
```
</ex-pdf-document-analysis>

<boundaries>
### What You CAN Configure

- Model Selection: Any supported model from any provider
- Temperature: Control randomness (0-1)
- Max Tokens: Limit response length
- Stream modes: Choose which data to stream
- API Keys: Per-model or from environment

### What You CANNOT Configure

- Model Training Data: Models are pre-trained
- Token Costs: Set by provider
- Rate Limits: Set by provider
- Chunk size/timing: Determined by model/provider
</boundaries>

<fix-api-key-not-found>
```python
# WRONG: Missing API key
model = init_chat_model("openai:gpt-4.1")
model.invoke("Hello")  # Error: API key not found

# CORRECT: Set environment variable
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
model = init_chat_model("openai:gpt-4.1")

# OR pass directly
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4.1", api_key="sk-...")
```
</fix-api-key-not-found>

<fix-response-content-access>
```python
# WRONG: Wrong property access
response = model.invoke("Hello")
print(response)  # AIMessage object, not string

# CORRECT: Access .content property
print(response.content)  # "Hello! How can I help you?"
```
</fix-response-content-access>

<fix-streaming-requires-iteration>
```python
# WRONG: Not iterating stream
stream = model.stream("Hello")
print(stream)  # Generator object, not chunks

# CORRECT: Use for loop with flush
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)
```
</fix-streaming-requires-iteration>

<fix-tuple-unpacking-for-messages-mode>
```python
# WRONG: Not unpacking messages mode
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    print(chunk.content)  # AttributeError!

# CORRECT: Messages mode returns (token, metadata) tuple
for mode, chunk in agent.stream(input, stream_mode=["messages"]):
    token, metadata = chunk
    print(token.content)
```
</fix-tuple-unpacking-for-messages-mode>

<fix-sync-vs-async>
```python
# WRONG: Using sync in async context
async def process():
    for chunk in model.stream("Hello"):  # Blocks async loop!
        print(chunk.content)

# CORRECT: Use async methods
async def process():
    async for chunk in model.astream("Hello"):
        print(chunk.content, flush=True)
```
</fix-sync-vs-async>

<fix-import-errors>
```python
# WRONG: Using old community package
from langchain.chat_models import ChatOpenAI  # Deprecated!

# CORRECT: Use provider-specific package
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
```
</fix-import-errors>

<fix-azure-configuration>
```python
# WRONG: Missing required fields
from langchain_openai import AzureChatOpenAI
model = AzureChatOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"))

# CORRECT: All required fields
model = AzureChatOpenAI(
    azure_endpoint="https://my-instance.openai.azure.com/",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment="gpt-4",
    api_version="2024-02-01",
)
```
</fix-azure-configuration>

<fix-model-doesnt-support-multimodal>
```python
# WRONG: Using text-only model for images
model = ChatOpenAI(model="gpt-3.5-turbo")
model.invoke([image_message])  # Error!

# CORRECT: Use vision-capable model
model = ChatOpenAI(model="gpt-4.1")
```
</fix-model-doesnt-support-multimodal>

<fix-missing-mime-type-for-base64>
```python
# WRONG: No MIME type for base64 image
{"type": "image", "base64": base64_data}  # May fail

# CORRECT: Always include MIME type
{"type": "image", "base64": base64_data, "mime_type": "image/jpeg"}
```
</fix-missing-mime-type-for-base64>
