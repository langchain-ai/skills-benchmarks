# Tracing Semantic Kernel applications

Semantic Kernel has built-in OTel — wire LangSmith via `configure()` + the OpenAI instrumentor.

## Install

```bash
pip install langsmith semantic-kernel opentelemetry-instrumentation-openai
# or: uv add langsmith semantic-kernel opentelemetry-instrumentation-openai
```

## Env

```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=<project>
OPENAI_API_KEY=<key>
```

## Setup

```python
from langsmith.integrations.otel import configure
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

configure(project_name="semantic-kernel-demo")
OpenAIInstrumentor().instrument()
```

`configure()` handles endpoint/headers; you don't need `OTEL_EXPORTER_OTLP_*` env vars.

## Run

```python
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

kernel = Kernel()
kernel.add_service(OpenAIChatCompletion())

# ... add prompt template / function ...
result = await kernel.invoke(my_function, input=...)
```

## Custom metadata

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def analyze_with_metadata(code: str):
    with tracer.start_as_current_span("semantic_kernel_workflow") as span:
        span.set_attribute("langsmith.metadata.workflow_type", "code_analysis")
        span.set_attribute("langsmith.metadata.user_id", "developer_123")
        span.set_attribute("langsmith.span.tags", "semantic-kernel,code-analysis")
        return await kernel.invoke(code_analyzer, code=code)
```

See `otel.md` for the full attribute mapping table (`langsmith.metadata.*`, `langsmith.span.kind`, `langsmith.span.tags`, etc.).

## Combine with other instrumentors

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
OpenAIInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()
```
