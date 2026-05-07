# Tracing with OpenTelemetry

LangSmith ingests OTel traces. Use this path when:
- You're tracing a non-LangChain framework that has built-in OTel
- You need to fan out traces to LangSmith **and** another backend (hybrid)
- You want to bring your own `TracerProvider`
- You need distributed tracing across services

For the simple "Python/JS function with `@traceable`" path, see `traceable.md`.

## Version requirements

- LangChain/LangGraph integration: `langsmith>=0.3.18`
- Hybrid mode (`LANGSMITH_OTEL_ONLY`, alternate providers): `langsmith>=0.4.1`
- **Recommended throughout: `langsmith>=0.4.25`** (important OTel fixes around export and hybrid fan-out stability)

## Endpoints

| Region | Endpoint |
|---|---|
| US (default) | `https://api.smith.langchain.com/otel` |
| EU (GCP) | `https://eu.api.smith.langchain.com/otel` |
| US (AWS SaaS) | `https://aws.api.smith.langchain.com/otel` |
| Self-hosted | `https://<your-host>/api/v1/otel` |

Append `/v1/traces` if your exporter sends traces only (not metrics/logs). Most OTLP HTTP exporters do.

## LangChain / LangGraph apps (auto-OTel export)

```bash
pip install "langsmith[otel]"  # langsmith>=0.3.18 minimum, >=0.4.25 recommended
pip install langchain
```

```bash
LANGSMITH_OTEL_ENABLED=true
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<key>
LANGSMITH_WORKSPACE_ID=<workspace-id>   # only if API key spans multiple workspaces
```

Run your app — spans are exported automatically. Set `LANGSMITH_OTEL_ONLY=true` (requires `>=0.4.1`) to skip the native LangSmith exporter and emit OTel only.

## Non-LangChain apps (manual OTel SDK)

```bash
pip install openai opentelemetry-sdk opentelemetry-exporter-otlp
```

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.smith.langchain.com/otel
OTEL_EXPORTER_OTLP_HEADERS="x-api-key=<key>,Langsmith-Project=<project>"
```

For self-hosted, the endpoint takes the form `<your-host>/api/v1/otel` (then append `/v1/traces` if exporting traces only):
```
OTEL_EXPORTER_OTLP_ENDPOINT=https://ai-company.com/api/v1/otel
```

```python
import os
from openai import OpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(timeout=10))
)
tracer = trace.get_tracer(__name__)

def call_openai():
    model = "gpt-4o-mini"
    with tracer.start_as_current_span("call_open_ai") as span:
        span.set_attribute("langsmith.span.kind", "LLM")
        span.set_attribute("langsmith.metadata.user_id", "user_123")
        span.set_attribute("gen_ai.system", "OpenAI")
        span.set_attribute("gen_ai.request.model", model)

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a haiku about recursion."},
        ]
        for i, m in enumerate(messages):
            span.set_attribute(f"gen_ai.prompt.{i}.role", m["role"])
            span.set_attribute(f"gen_ai.prompt.{i}.content", m["content"])

        completion = client.chat.completions.create(model=model, messages=messages)

        span.set_attribute("gen_ai.response.model", completion.model)
        span.set_attribute("gen_ai.completion.0.role", "assistant")
        span.set_attribute("gen_ai.completion.0.content", completion.choices[0].message.content)
        span.set_attribute("gen_ai.usage.prompt_tokens", completion.usage.prompt_tokens)
        span.set_attribute("gen_ai.usage.completion_tokens", completion.usage.completion_tokens)
        span.set_attribute("gen_ai.usage.total_tokens", completion.usage.total_tokens)

        return completion.choices[0].message
```

## Global OTel env vars

The LangSmith exporter respects standard OTel env vars:

| Var | Notes |
|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Override endpoint |
| `OTEL_EXPORTER_OTLP_HEADERS` | LangSmith API key + project added automatically when using LangSmith exporter |
| `OTEL_SERVICE_NAME` | Defaults to `"langsmith"` |

You can also set a global `TracerProvider` **before** initializing LangChain components — LangSmith detects it and uses it instead of creating its own.

## SDK helper: `configure()`

```python
from langsmith.integrations.otel import configure
configure(project_name="my-project")
```

Wires endpoint, headers, and `TracerProvider` for LangSmith automatically. Use when:
- You want zero env-var setup (e.g. PydanticAI, Semantic Kernel, Google ADK)
- You're combining with an instrumentor like `GoogleADKInstrumentor` that creates the spans

## Send traces to an alternate / hybrid provider

```python
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

os.environ["LANGSMITH_OTEL_ENABLED"] = "true"
os.environ["LANGSMITH_TRACING"] = "true"

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint="https://otel.your-provider.com/v1/traces",
    headers={"api-key": "<key>"},
)))
trace.set_tracer_provider(provider)

# LangChain app runs as normal; spans go to BOTH LangSmith and the other provider
chain = ChatPromptTemplate.from_template("Joke about {topic}") | ChatOpenAI()
chain.invoke({"topic": "programming"})
```

To send to **only** the alternate provider (skip LangSmith): set `LANGSMITH_OTEL_ONLY=true` (requires `langsmith>=0.4.1`).

## OTel Collector fan-out

For multi-destination at scale, emit OTel once and let a Collector fan out:

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }
processors:
  batch:
exporters:
  otlphttp/langsmith:
    endpoint: https://api.smith.langchain.com/otel/v1/traces
    headers:
      x-api-key: ${env:LANGSMITH_API_KEY}
      Langsmith-Project: my_project
  otlphttp/other_provider:
    endpoint: https://otel.your-provider.com/v1/traces
    headers:
      api-key: ${env:OTHER_PROVIDER_API_KEY}
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlphttp/langsmith, otlphttp/other_provider]
```

App points to the collector (`http://localhost:4318/v1/traces`); collector routes. Use this when you'd otherwise be configuring multiple exporters in app code.

## Distributed tracing (context propagation)

When a request crosses service boundaries, propagate trace context via HTTP headers using OTel's `inject`/`extract`. Both services share the same trace ID.

```python
# Service A
from opentelemetry.propagate import inject

with tracer.start_as_current_span("service_a_operation"):
    result = chain.invoke({"text": "..."})
    headers = {}
    inject(headers)            # injects traceparent / tracestate
    requests.post("http://service-b/process", headers=headers, json={...})
```

```python
# Service B
from opentelemetry.propagate import extract
from flask import request

@app.route("/process", methods=["POST"])
def endpoint():
    context = extract(request.headers)
    with tracer.start_as_current_span("service_b_operation", context=context):
        return jsonify({"analysis": chain.invoke({...}).content})
```

The propagated context carries: trace ID, span ID, sampling decision. Service B's spans nest under Service A's root in LangSmith.

## Attachments (multimodal inputs/outputs)

Attach files to a span by writing JSON to `langsmith.attachments` in a custom `SpanProcessor.on_end()`. The custom processor must run **before** `OtelSpanProcessor` so the attribute is on the span when LangSmith sees it.

```python
import base64, json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from langsmith.integrations.otel import OtelSpanProcessor

class AttachmentSpanProcessor(SpanProcessor):
    def __init__(self):
        self.attachment_data = None

    def set_attachment(self, data):
        self.attachment_data = data

    def on_end(self, span):
        if span.name == "invocation" and self.attachment_data:
            span._attributes["langsmith.attachments"] = json.dumps([self.attachment_data])

provider = TracerProvider()
trace.set_tracer_provider(provider)

attachment_processor = AttachmentSpanProcessor()
provider.add_span_processor(attachment_processor)            # FIRST: mutates span
provider.add_span_processor(OtelSpanProcessor(project="…"))  # SECOND: reads + exports

with open("receipt.png", "rb") as f:
    attachment_processor.set_attachment({
        "name": "receipt",
        "content": base64.b64encode(f.read()).decode("ascii"),
        "mime_type": "image/jpeg",
    })
# ...run your agent; the parent span gets the attachment...
```

Order matters: span processors fire in registration order. Reverse the order and `OtelSpanProcessor` exports the span before the attachment is set.

## Attribute mapping

LangSmith maps OTel attributes from several conventions onto its run model. Set these on spans (or rely on instrumentors that emit them) to get rich rendering.

### Core LangSmith attributes

| OTel attribute | LangSmith field | Notes |
|---|---|---|
| `langsmith.trace.name` | run name | Overrides span name |
| `langsmith.span.kind` | run type | `llm`, `chain`, `tool`, `retriever`, `embedding`, `prompt`, `parser` |
| `langsmith.trace.session_id` | session ID | |
| `langsmith.trace.session_name` | session name | |
| `langsmith.span.tags` | tags | Comma-separated |
| `langsmith.metadata.{key}` | `metadata.{key}` | |
| `langsmith.attachments` | attachments | JSON array (see above) |

### GenAI standard attributes

| OTel attribute | LangSmith field |
|---|---|
| `gen_ai.system` | `metadata.ls_provider` (e.g. "openai") |
| `gen_ai.operation.name` | run type (`chat`/`completion`→`llm`, `embedding`→`embedding`) |
| `gen_ai.prompt` | inputs |
| `gen_ai.completion` | outputs |
| `gen_ai.prompt.{n}.role` / `.content` | `inputs.messages[n].role` / `.content` |
| `gen_ai.prompt.{n}.message.role` / `.content` | (alternative form, same target) |
| `gen_ai.completion.{n}.role` / `.content` | `outputs.messages[n].role` / `.content` |
| `gen_ai.completion.{n}.message.role` / `.content` | (alternative form) |
| `gen_ai.input.messages` | `inputs.messages` (array) |
| `gen_ai.output.messages` | `outputs.messages` (array) |
| `gen_ai.tool.name` | sets run type to `tool` + `invocation_params.tool_name` |

### GenAI request parameters

`gen_ai.request.{model, temperature, top_p, top_k, max_tokens, frequency_penalty, presence_penalty, seed, stop_sequences, encoding_formats}` → `invocation_params.{...}`. `gen_ai.response.model` also maps to `invocation_params.model`.

### GenAI usage metrics

| OTel attribute | LangSmith field |
|---|---|
| `gen_ai.usage.input_tokens` | `usage_metadata.input_tokens` |
| `gen_ai.usage.output_tokens` | `usage_metadata.output_tokens` |
| `gen_ai.usage.total_tokens` | `usage_metadata.total_tokens` |
| `gen_ai.usage.prompt_tokens` | `usage_metadata.input_tokens` (deprecated) |
| `gen_ai.usage.completion_tokens` | `usage_metadata.output_tokens` (deprecated) |
| `gen_ai.usage.details.reasoning_tokens` | `usage_metadata.reasoning_tokens` |

### TraceLoop attributes

| OTel attribute | LangSmith field |
|---|---|
| `traceloop.entity.input` | inputs |
| `traceloop.entity.output` | outputs |
| `traceloop.entity.name` | run name |
| `traceloop.span.kind` | run type |
| `traceloop.llm.request.type` | run type (`embedding`→`embedding`, else `llm`) |
| `traceloop.association.properties.{key}` | `metadata.{key}` |

### OpenInference attributes (Arize/Phoenix)

| OTel attribute | LangSmith field |
|---|---|
| `input.value` | inputs (string or JSON) |
| `output.value` | outputs (string or JSON) |
| `openinference.span.kind` | run type |
| `llm.system` | `metadata.ls_provider` |
| `llm.model_name` | `metadata.ls_model_name` |
| `tool.name` | run name (when span kind is `TOOL`) |
| `metadata` | `metadata.*` (JSON string, merged) |

### LLM attributes

| OTel attribute | LangSmith field |
|---|---|
| `llm.input_messages` | `inputs.messages` |
| `llm.output_messages` | `outputs.messages` |
| `llm.token_count.prompt` / `.completion` / `.total` | `usage_metadata.*` |
| `llm.invocation_parameters` | `invocation_params.*` (JSON string) |
| `llm.presence_penalty` / `llm.frequency_penalty` | `invocation_params.*` |
| `llm.request.functions` | `invocation_params.functions` |

### Prompt template / Retriever / Tool / Logfire

- `llm.prompt_template.variables` → run type `prompt` (with `input.value`)
- `retrieval.documents.{n}.document.content` → `outputs.documents[n].page_content`
- `retrieval.documents.{n}.document.metadata` → `outputs.documents[n].metadata`
- `tools` → `invocation_params.tools`; `tool_arguments` → `invocation_params.tool_arguments`
- Logfire: `prompt` → inputs, `all_messages_events` → outputs, `events` → split into inputs/outputs

## Event mapping

LangSmith also reads OTel **events** (distinct from attributes). Useful for instrumentors that emit message events instead of `gen_ai.prompt.{n}.*` attributes.

| Event name | LangSmith field |
|---|---|
| `gen_ai.content.prompt` | inputs |
| `gen_ai.content.completion` | outputs |
| `gen_ai.system.message` | `inputs.messages[]` (system) |
| `gen_ai.user.message` | `inputs.messages[]` (user) |
| `gen_ai.assistant.message` | `outputs.messages[]` (assistant) |
| `gen_ai.tool.message` | `outputs.messages[]` (tool response) |
| `gen_ai.choice` | outputs (with finish reason) |
| `exception` | sets status to `error`, extracts `exception.message` + `exception.stacktrace` |

### Event attribute extraction

For message events: `content` → message content, `role` → role, `id` → tool_call_id (tool messages), `gen_ai.event.content` → full message JSON.

For `gen_ai.choice` events: `finish_reason`, `message.content`, `message.role`, `tool_calls.{n}.id`, `tool_calls.{n}.function.name`, `tool_calls.{n}.function.arguments`, `tool_calls.{n}.type`.

For `exception` events: `exception.message` → error message; `exception.stacktrace` → appended to message.
