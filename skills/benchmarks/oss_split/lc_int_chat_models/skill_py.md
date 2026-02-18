---
name: LangChain Chat Models Integration (Python)
description: [LangChain] Guide to using chat model integrations in LangChain including OpenAI, Anthropic, Google, Azure, and Bedrock
---

# langchain-chat-models (Python)

## Overview

Chat models in LangChain provide a unified interface for interacting with various LLM providers. They take a sequence of messages as input and return AI-generated messages as output. Chat models support features like tool calling, structured output, and streaming.

### Key Concepts

- **Chat Models**: Accept messages (with roles: system, user, assistant) and return generated responses
- **Providers**: Different AI companies offering LLM APIs (OpenAI, Anthropic, Google, Azure, Bedrock, etc.)
- **Tool Calling**: Models can invoke functions/tools based on user queries
- **Streaming**: Real-time token-by-token response generation
- **Structured Output**: Models can return responses in specific formats (JSON, Pydantic models)

## Provider Selection Decision Table

| Provider | Best For | Model Examples | Package | Key Features |
|----------|----------|----------------|---------|--------------|
| **OpenAI** | General purpose, function calling | gpt-4, gpt-4-turbo, gpt-3.5-turbo | `langchain-openai` | Strong function calling, vision, fast |
| **Anthropic** | Long context, safety, analysis | claude-3-opus, claude-3-sonnet, claude-3-haiku | `langchain-anthropic` | 200k context, tool use, prompt caching |
| **Google GenAI** | Multimodal, free tier | gemini-pro, gemini-pro-vision | `langchain-google-genai` | Vision, free tier available |
| **Azure OpenAI** | Enterprise, compliance | gpt-4, gpt-35-turbo (Azure deployed) | `langchain-openai` | Enterprise SLAs, data residency |
| **AWS Bedrock** | AWS ecosystem, variety | claude, llama, titan models | `langchain-aws` | Multiple models, AWS integration |
| **Google Vertex AI** | GCP ecosystem, enterprise | gemini-pro, palm models | `langchain-google-vertexai` | Enterprise features, GCP integration |

### When to Choose Each Provider

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

## Code Examples

### OpenAI Chat Model

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

### Anthropic Chat Model

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

### Azure OpenAI Chat Model

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

### AWS Bedrock Chat Model

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

### Google Generative AI

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

### Using init_chat_model (Recommended)

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

### Tool Calling Example

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

### Structured Output Example

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

## Boundaries

### What Agents CAN Do

✅ **Initialize any supported chat model provider**
- Install required packages (`langchain-openai`, `langchain-anthropic`, etc.)
- Configure models with API keys and parameters

✅ **Configure model parameters**
- Set temperature, max_tokens, top_p, frequency_penalty
- Configure streaming, timeout, and retry settings

✅ **Use models for text generation**
- Send messages and receive responses
- Stream responses token-by-token
- Use system prompts and multi-turn conversations

✅ **Implement tool/function calling**
- Bind tools to models that support it
- Parse tool call responses
- Execute tools and return results

✅ **Generate structured output**
- Use Pydantic models for type-safe responses
- Extract structured data from text

✅ **Switch between providers**
- Use init_chat_model for provider-agnostic code
- Change providers by updating configuration

### What Agents CANNOT Do

❌ **Create new model providers**
- Cannot add support for unlisted LLM providers
- Must use existing LangChain integrations

❌ **Bypass provider requirements**
- Cannot use Azure OpenAI without deployment names
- Cannot skip required authentication credentials

❌ **Modify model capabilities**
- Cannot add tool calling to models that don't support it
- Cannot extend context windows beyond provider limits

❌ **Access models without proper setup**
- Cannot use providers without valid API keys
- Cannot bypass billing/quota limits

## Gotchas

### 1. **API Keys and Environment Variables**

```python
# ❌ BAD: Hardcoding API keys
model = ChatOpenAI(
    api_key="sk-..."  # Never commit this!
)

# ✅ GOOD: Use environment variables
import os
model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ✅ BETTER: Let LangChain auto-detect from environment
model = ChatOpenAI()  # Reads OPENAI_API_KEY automatically
```

**Fix**: Always use environment variables or secure key management systems.

### 2. **Azure OpenAI Configuration Changes**

```python
# ❌ OLD WAY (deprecated)
from langchain_openai import AzureChatOpenAI
model = AzureChatOpenAI(
    deployment_name="gpt-4",
    openai_api_base="https://my-instance.openai.azure.com/",
)

# ✅ NEW WAY
model = AzureChatOpenAI(
    azure_endpoint="https://my-instance.openai.azure.com/",
    azure_deployment="gpt-4",
    api_version="2024-02-01",
)
```

**Fix**: Use `azure_endpoint` and `azure_deployment` instead of older parameters.

### 3. **Message Format Variations**

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

**Fix**: Use whichever format is clearer for your use case. Message classes provide type safety.

### 4. **Tool Calling Support**

```python
# ❌ Not all models support tool calling
model = ChatOpenAI(model="gpt-3.5-turbo-instruct")
# This older model doesn't support tools!

# ✅ Use models with tool support
model = ChatOpenAI(model="gpt-4")
model_with_tools = model.bind_tools([my_tool])
```

**Fix**: Verify model supports function/tool calling before binding tools. GPT-4, GPT-3.5-turbo, Claude 3, and Gemini Pro all support tools.

### 5. **Import Errors - Wrong Package**

```python
# ❌ WRONG: Using old community package
from langchain.chat_models import ChatOpenAI  # Deprecated!

# ✅ CORRECT: Use provider-specific package
from langchain_openai import ChatOpenAI
```

**Fix**: Use provider-specific packages (`langchain-openai`, `langchain-anthropic`, etc.) instead of `langchain-community`.

### 6. **Context Window Limits**

```python
# ❌ Exceeding context limits
model = ChatOpenAI(model="gpt-3.5-turbo")  # 4k context
long_text = "..." * 10000
model.invoke(long_text)  # Will fail!

# ✅ Use appropriate models for long context
model = ChatOpenAI(model="gpt-4-turbo")  # 128k context
# OR
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-opus-20240229")  # 200k context
```

**Fix**: Choose models with appropriate context windows for your use case.

### 7. **Streaming Confusion**

```python
# ❌ Wrong: Treating stream like regular response
response = model.stream("Hello")
print(response.content)  # AttributeError!

# ✅ Correct: Iterate over stream
for chunk in model.stream("Hello"):
    print(chunk.content, end="", flush=True)

# OR use invoke for complete response
response = model.invoke("Hello")
print(response.content)
```

**Fix**: Use `invoke()` for complete responses, `stream()` for token-by-token.

### 8. **AWS Bedrock Model IDs**

```python
# ❌ Wrong model ID format
model = ChatBedrock(model_id="claude-3-sonnet")  # Won't work!

# ✅ Correct: Full Bedrock model ID
model = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)
```

**Fix**: Use complete Bedrock model identifiers from AWS documentation.

### 9. **Pydantic Version Compatibility**

```python
# Some LangChain versions require Pydantic v2
# ❌ May cause errors with Pydantic v1
from pydantic import BaseModel

class Output(BaseModel):
    name: str

# ✅ Ensure Pydantic v2 is installed
# pip install "pydantic>=2.0"
```

**Fix**: Use Pydantic v2 for best compatibility with LangChain.

## Links and Resources

### Official Documentation
- [LangChain Python Chat Models Overview](https://python.langchain.com/docs/integrations/chat/)
- [OpenAI Integration](https://python.langchain.com/docs/integrations/chat/openai)
- [Anthropic Integration](https://python.langchain.com/docs/integrations/chat/anthropic)
- [Azure OpenAI Integration](https://python.langchain.com/docs/integrations/chat/azure_chat_openai)
- [AWS Bedrock Integration](https://python.langchain.com/docs/integrations/chat/bedrock)
- [Google GenAI Integration](https://python.langchain.com/docs/integrations/chat/google_generative_ai)

### Provider Documentation
- [OpenAI API Docs](https://platform.openai.com/docs/introduction)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [AWS Bedrock](https://docs.aws.amazon.com/bedrock/)
- [Google AI Studio](https://ai.google.dev/)

### Package Installation
```bash
# OpenAI
pip install langchain-openai

# Anthropic
pip install langchain-anthropic

# AWS (Bedrock)
pip install langchain-aws

# Google
pip install langchain-google-genai
pip install langchain-google-vertexai
```
