# Tracing PydanticAI applications

PydanticAI has built-in OTel. Use `langsmith.integrations.otel.configure()` + `Agent.instrument_all()`.

## Install

```bash
pip install langsmith pydantic-ai opentelemetry-exporter-otlp
# or: uv add langsmith pydantic-ai opentelemetry-exporter-otlp
```

`langsmith>=0.4.26` recommended for optimal OTel support.

## Env

```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=<project>
OPENAI_API_KEY=<key>
```

`configure()` wires the LangSmith OTel exporter automatically — **no need** to set `OTEL_EXPORTER_OTLP_*` env vars or build exporters manually.

## Setup

```python
from langsmith.integrations.otel import configure
from pydantic_ai import Agent

configure(project_name="pydantic-ai-demo")
Agent.instrument_all()

agent = Agent("openai:gpt-4o")
result = agent.run_sync("What is the capital of France?")
print(result.output)
```

Call `configure()` + `Agent.instrument_all()` **once at startup**, before constructing agents. `instrument_all()` patches every PydanticAI `Agent` class. Per-agent instrumentation is also available via `Agent(..., instrument=True)`.

## Custom metadata and tags

Add metadata via OTel span attributes:

```python
from opentelemetry import trace
from pydantic_ai import Agent
from langsmith.integrations.otel import configure

configure(project_name="pydantic-ai-metadata")
Agent.instrument_all()

tracer = trace.get_tracer(__name__)
agent = Agent("openai:gpt-4o")

with tracer.start_as_current_span("pydantic_ai_workflow") as span:
    span.set_attribute("langsmith.metadata.user_id", "user_123")
    span.set_attribute("langsmith.metadata.workflow_type", "question_answering")
    span.set_attribute("langsmith.span.tags", "pydantic-ai,production")

    result = agent.run_sync("Explain quantum computing in simple terms")
    print(result.output)
```

See `otel.md` for the full attribute mapping table (`langsmith.metadata.*`, `langsmith.span.tags`, `langsmith.span.kind`, etc.).
