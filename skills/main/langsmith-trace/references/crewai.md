# Tracing CrewAI applications

CrewAI is captured via two OTel instrumentors (`crewai` + `openai`) routed through LangSmith's `OtelSpanProcessor`.

## Install

```bash
pip install langsmith crewai opentelemetry-instrumentation-crewai opentelemetry-instrumentation-openai
```

## Env

```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=<project>
OPENAI_API_KEY=<key>
```

## Setup

```python
from langsmith.integrations.otel import OtelSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.crewai import CrewAIInstrumentor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

# Reuse existing TracerProvider if one is already set
current = trace.get_tracer_provider()
if isinstance(current, TracerProvider):
    tracer_provider = current
else:
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

tracer_provider.add_span_processor(OtelSpanProcessor())

CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

Pass `tracer_provider=` to **both** instrumentors. Skipping it on one of them causes mixed spans where some calls land in the global provider instead of LangSmith.

## Custom metadata

```python
with tracer.start_as_current_span("crewai_workflow") as span:
    span.set_attribute("langsmith.metadata.crew_type", "code_generation")
    span.set_attribute("langsmith.span.tags", "crewai,code-generation")
    crew.kickoff()
```
