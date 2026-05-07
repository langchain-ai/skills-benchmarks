# Tracing AutoGen applications

AutoGen exposes OpenTelemetry spans. Use the `OtelSpanProcessor` from LangSmith plus the OpenAI OTel instrumentor.

## Install

```bash
pip install langsmith autogen-agentchat autogen-ext opentelemetry-instrumentation-openai
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
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(OtelSpanProcessor())
trace.set_tracer_provider(tracer_provider)

OpenAIInstrumentor().instrument()
```

## Pass `tracer_provider` into the runtime

For multi-agent/group-chat coverage:

```python
from autogen_core import SingleThreadedAgentRuntime
from autogen_agentchat.teams import SelectorGroupChat

runtime = SingleThreadedAgentRuntime(tracer_provider=trace.get_tracer_provider())
runtime.start()

team = SelectorGroupChat([...], runtime=runtime, ...)
```

Without this, only the OpenAI calls are captured — agent/team coordination spans are missing.

## Custom metadata

```python
with tracer.start_as_current_span("autogen_workflow") as span:
    span.set_attribute("langsmith.metadata.session_type", "multi_agent")
    span.set_attribute("langsmith.span.tags", "autogen,planning")
```

## Combine with other instrumentors

```python
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
OpenAIInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()
```
