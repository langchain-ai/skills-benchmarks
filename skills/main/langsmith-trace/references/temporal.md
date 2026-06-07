# Tracing Temporal workflows

Use Temporal's native OTel interceptors with LangSmith as the OTLP destination. Supported in Go, Python, and TypeScript.

Both client and worker need the interceptor — Temporal propagates trace context across process boundaries via workflow headers, so client-initiated spans nest under the worker's activity spans automatically.

## Env (all languages)

| Var | Required | Notes |
|---|---|---|
| `LANGSMITH_API_KEY` | yes | From LangSmith Settings |
| `LANGSMITH_PROJECT` | no | Defaults to `default` |
| `LANGCHAIN_BASE_URL` | EU / self-hosted | Override for non-US LangSmith instances |

## Python

```bash
pip install temporalio langsmith opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from temporalio.client import Client
from temporalio.contrib.opentelemetry import TracingInterceptor

def init_tracer_provider() -> TracerProvider:
    exporter = OTLPSpanExporter(
        endpoint="https://api.smith.langchain.com/otel/v1/traces",
        headers={
            "x-api-key": os.environ["LANGSMITH_API_KEY"],
            "Langsmith-Project": os.environ.get("LANGSMITH_PROJECT", "default"),
        },
    )
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "temporal-worker"}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider

# Then on both worker and client:
client = await Client.connect("localhost:7233", interceptors=[TracingInterceptor()])
worker = Worker(client, task_queue="my-task-queue", workflows=[MyWorkflow], activities=[process_activity])
```

Inside an activity, decorate the active span with `gen_ai.*` attributes so LangSmith renders it as an LLM run:

```python
from opentelemetry import trace
from temporalio import activity

@activity.defn
async def process_activity(input: str) -> str:
    span = trace.get_current_span()
    span.set_attribute("gen_ai.prompt", input)
    span.set_attribute("gen_ai.operation.name", "chat")
    result = f"Processed: {input}"
    span.set_attribute("gen_ai.completion", result)
    return result
```

## TypeScript

```bash
npm install @temporalio/client @temporalio/worker @temporalio/activity @temporalio/workflow \
            @temporalio/interceptors-opentelemetry \
            @opentelemetry/sdk-trace-node @opentelemetry/sdk-trace-base \
            @opentelemetry/exporter-trace-otlp-http \
            @opentelemetry/resources @opentelemetry/semantic-conventions @opentelemetry/api
```

```typescript
// tracer.ts
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

export function initTracerProvider(): NodeTracerProvider {
  const exporter = new OTLPTraceExporter({
    url: "https://api.smith.langchain.com/otel/v1/traces",
    headers: {
      "x-api-key": process.env.LANGSMITH_API_KEY!,
      "Langsmith-Project": process.env.LANGSMITH_PROJECT ?? "default",
    },
  });
  const provider = new NodeTracerProvider({
    resource: new Resource({ [ATTR_SERVICE_NAME]: "temporal-worker" }),
  });
  provider.addSpanProcessor(new BatchSpanProcessor(exporter));
  provider.register();
  return provider;
}
```

```typescript
// activities.ts — add gen_ai.* attributes for LangSmith visibility
import { trace } from "@opentelemetry/api";

export async function processActivity(input: string): Promise<string> {
  const span = trace.getActiveSpan();
  span?.setAttribute("gen_ai.prompt", input);
  span?.setAttribute("gen_ai.operation.name", "chat");
  const result = `Processed: ${input}`;
  span?.setAttribute("gen_ai.completion", result);
  return result;
}
```

```typescript
// worker.ts — workflow exporter + activity interceptor
import { Worker, NativeConnection } from "@temporalio/worker";
import { Resource } from "@opentelemetry/resources";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { trace } from "@opentelemetry/api";
import {
  makeWorkflowExporter,
  OpenTelemetryActivityInboundInterceptor,
} from "@temporalio/interceptors-opentelemetry";
import * as activities from "./activities";
import { initTracerProvider } from "./tracer";

const provider = initTracerProvider();
try {
  const connection = await NativeConnection.connect({ address: "localhost:7233" });
  const worker = await Worker.create({
    connection,
    namespace: "default",
    taskQueue: "my-task-queue",
    workflowsPath: require.resolve("./workflows"),
    activities,
    sinks: {
      exporter: makeWorkflowExporter(
        trace.getTracer("temporal-app"),
        new Resource({ [ATTR_SERVICE_NAME]: "temporal-worker" }),
      ),
    },
    interceptors: {
      activity: [() => ({ inbound: new OpenTelemetryActivityInboundInterceptor() })],
    },
  });
  await worker.run();
} finally {
  await provider.shutdown();
}
```

## Go

```bash
go get github.com/langchain-ai/langsmith-go@v0.1.0-alpha.7
go get go.temporal.io/sdk go.temporal.io/sdk/contrib/opentelemetry
```

```go
import (
    "context"
    "github.com/langchain-ai/langsmith-go"
    "go.temporal.io/sdk/client"
    "go.temporal.io/sdk/contrib/opentelemetry"
    "go.temporal.io/sdk/interceptor"
    "go.temporal.io/sdk/worker"
)

ctx := context.Background()
ls, _ := langsmith.NewTracer(langsmith.WithServiceName("temporal-worker"))
defer ls.Shutdown(ctx)

tracingInterceptor, _ := opentelemetry.NewTracingInterceptor(
    opentelemetry.TracerOptions{Tracer: ls.Tracer("temporal-app")},
)

c, _ := client.Dial(client.Options{
    Interceptors: []interceptor.ClientInterceptor{tracingInterceptor},
})
defer c.Close()

w := worker.New(c, "my-task-queue", worker.Options{})
w.RegisterWorkflow(MyWorkflow)
w.RegisterActivity(MyActivity)
_ = w.Run(worker.InterruptCh())
```

Inside an activity, attach `gen_ai.*` attributes to the span Temporal's interceptor created:

```go
import (
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
)

func MyActivity(ctx context.Context, input string) (string, error) {
    span := trace.SpanFromContext(ctx)
    span.SetAttributes(
        attribute.String("gen_ai.prompt", input),
        attribute.String("gen_ai.operation.name", "chat"),
    )
    result := "Processed: " + input
    span.SetAttributes(attribute.String("gen_ai.completion", result))
    return result, nil
}
```

The client that submits workflows needs the same interceptor — initialize a separate tracer (`langsmith.WithServiceName("temporal-client")`) and pass `tracingInterceptor` into `client.Dial`.

## Gotchas

- Provider must be initialized **before** `Client.connect()` and the worker — interceptors capture spans only against the active provider.
- `provider.shutdown()` (or `defer ls.Shutdown(ctx)` in Go) is mandatory to flush pending traces.
- Both client and worker need the interceptor; otherwise the workflow span won't link to the activity span.
- For LangSmith to render activities as LLM runs, decorate the activity's active span with `gen_ai.prompt`, `gen_ai.operation.name`, and `gen_ai.completion` (see per-language snippets above). Full attribute mapping in `otel.md`.
- TypeScript: workflow spans go through `makeWorkflowExporter` (sandboxed), activity spans through `OpenTelemetryActivityInboundInterceptor` — both are required.
