# Tracing Microsoft Agent Framework applications

MS Agent Framework has built-in OTel — point its OTLP exporter at LangSmith and call `configure_otel_providers()`.

## Install

```bash
pip install agent-framework opentelemetry-exporter-otlp-proto-http
```

## Env

```bash
ENABLE_INSTRUMENTATION=true
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.smith.langchain.com/otel/v1/traces
OTEL_EXPORTER_OTLP_HEADERS="x-api-key=<key>,Langsmith-Project=<project>"
```

## Setup

```python
from agent_framework import ChatAgent
from agent_framework.observability import configure_otel_providers
from agent_framework.openai import OpenAIChatClient

configure_otel_providers(enable_sensitive_data=True)  # False to redact prompts/completions

agent = ChatAgent(chat_client=OpenAIChatClient(model_id="gpt-4o"))
result = await agent.run("What's the capital of Bavaria?")
```

## Notes

- Set `enable_sensitive_data=False` if you can't ship prompts/completions to LangSmith (e.g. PII).
- The endpoint includes `/v1/traces` — don't add it again.
- `ENABLE_INSTRUMENTATION=true` is required; without it the framework's OTel hooks are inert.
