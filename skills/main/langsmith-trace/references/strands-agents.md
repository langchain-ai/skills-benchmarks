# Tracing Strands Agents applications

LangSmith ships `langsmith.integrations.strands_agents.setup_langsmith_telemetry()` — sets up Strands' OTel pipeline pointing at LangSmith.

## Install

```bash
pip install "langsmith[strands-agents]"
# or: uv add "langsmith[strands-agents]"
```

The extra pulls in `langsmith`, `strands-agents`, `strands-agents-tools`, and the OTLP-HTTP exporter.

## Env

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.smith.langchain.com/otel/v1/traces
OTEL_EXPORTER_OTLP_HEADERS="x-api-key=<key>,Langsmith-Project=<project>"
AWS_REGION=<region>   # if using Amazon Bedrock as the model provider
```

## Setup

```python
from langsmith.integrations.strands_agents import setup_langsmith_telemetry
from strands import Agent

setup_langsmith_telemetry()                 # call once at startup
# setup_langsmith_telemetry(console=True)   # also print spans to stdout for debugging

agent = Agent(system_prompt="You are a concise assistant.")
response = agent("Explain LangSmith tracing in one sentence.")
```

## Custom OTLP exporter

If you need to set exporter options in code (instead of env vars):

```python
from langsmith.integrations.strands_agents import create_langsmith_exporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from strands.telemetry import StrandsTelemetry

telemetry = StrandsTelemetry()
exporter = create_langsmith_exporter(
    endpoint="https://api.smith.langchain.com/otel/v1/traces",
    headers={"x-api-key": "<key>", "Langsmith-Project": "<project>"},
)
telemetry.tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
```

## What gets traced

Agent invocations, event-loop cycle spans, LLM call spans (prompts, completions, token usage), tool call spans (inputs/outputs).
