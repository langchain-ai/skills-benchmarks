# Tracing via raw REST API

**Last resort** — only use when you can't run a LangSmith SDK (e.g. unsupported language/runtime). Synchronous REST calls block your app's request path; the SDKs do batched background sending and have lighter rate limits.

For Python/TS see `traceable.md`. For OTel-native frameworks see `otel.md`.

## Auth

```
x-api-key: <LANGSMITH_API_KEY>
x-tenant-id: <LANGSMITH_WORKSPACE_ID>   # if API key spans multiple workspaces
```

## Base URL

| Region | URL |
|---|---|
| US (default) | `https://api.smith.langchain.com` |
| EU (GCP) | `https://eu.api.smith.langchain.com` |
| US (AWS SaaS) | `https://aws.api.smith.langchain.com` |
| Self-hosted | `https://<your-host>/api` |

## Run IDs

Use **UUID v7** for `id`. UUIDv7 embeds a timestamp so runs sort correctly within a trace. The LangSmith SDK exports a `uuid7` helper, or use the `uuid_utils` package directly.

## Basic tracing — `POST /runs` + `PATCH /runs/{id}`

`POST /runs` to start, `PATCH /runs/{id}` to finish. Server auto-computes `dotted_order` and `trace_id` — you only set `parent_run_id` to nest. Slower, lower rate limits than batch.

```python
import os, requests
from datetime import datetime, timezone
from langsmith import uuid7

headers = {
    "x-api-key": os.environ["LANGSMITH_API_KEY"],
    "x-tenant-id": os.environ.get("LANGSMITH_WORKSPACE_ID", ""),
}
BASE = "https://api.smith.langchain.com"

def post_run(run_id, name, run_type, inputs, parent_id=None):
    data = {
        "id": str(run_id),
        "name": name,
        "run_type": run_type,
        "inputs": inputs,
        "start_time": datetime.now(timezone.utc).isoformat(),
        # "session_name": "<project>",   # or "session_id": "<project-uuid>"
    }
    if parent_id:
        data["parent_run_id"] = str(parent_id)
    requests.post(f"{BASE}/runs", json=data, headers=headers)

def patch_run(run_id, outputs):
    requests.patch(f"{BASE}/runs/{run_id}", json={
        "outputs": outputs,
        "end_time": datetime.now(timezone.utc).isoformat(),
    }, headers=headers)

parent = uuid7()
post_run(parent, "Chat Pipeline", "chain", {"question": "…"})

child = uuid7()
post_run(child, "OpenAI Call", "llm", {"messages": [...]}, parent_id=parent)
# ... do work, get response ...
patch_run(child, {"choices": [...]})
patch_run(parent, {"answer": "…"})
```

## Batch ingestion — `POST /runs/multipart`

Higher throughput, higher rate limits. **You must compute `dotted_order` and `trace_id` yourself.**

- `trace_id` — UUID of the root run.
- `dotted_order` — `<YYYYMMDDTHHMMSSffffffZ><uuid>` per run, joined by dots, e.g.
  `20240101T000000000000Z<root>.20240101T000001000000Z<child>`.

The format encodes both ordering and parent-child relationships. The id field of a run equals the last 36 chars of its dotted order (after the final `Z`); `trace_id` equals the first UUID; `parent_run_id` equals the penultimate UUID.

Python deps: `requests-toolbelt`, `uuid-utils`.

The multipart body sends each run's main JSON plus separate parts for `inputs`, `outputs`, and `events`, all in one request:

```
post.<run_id>            -> run JSON (without inputs/outputs/events)
post.<run_id>.inputs     -> inputs JSON
post.<run_id>.outputs    -> outputs JSON   (optional)
post.<run_id>.events     -> events JSON    (optional)
patch.<run_id>           -> patch JSON     (for updates)
```

Sketch:

```python
import json, os, uuid, requests
from datetime import datetime, timezone
from requests_toolbelt import MultipartEncoder
from uuid_utils.compat import uuid7

def dotted(start_time, run_id):
    return f"{start_time.strftime('%Y%m%dT%H%M%S%fZ')}{run_id}"

def make_run(name, run_type, inputs, parent_dotted=None):
    rid = uuid7()
    st = datetime.now(timezone.utc)
    run = {
        "id": str(rid),
        "trace_id": str(rid),
        "name": name,
        "run_type": run_type,
        "inputs": inputs,
        "start_time": st.isoformat(),
        "dotted_order": dotted(st, rid),
    }
    if parent_dotted:
        run["dotted_order"] = f"{parent_dotted}.{run['dotted_order']}"
        run["trace_id"] = parent_dotted.split(".")[0].split("Z")[1]
        run["parent_run_id"] = parent_dotted.split(".")[-1].split("Z")[1]
    return run

def serialize(op, run):
    rid = run["id"]
    inputs = run.pop("inputs", None)
    outputs = run.pop("outputs", None)
    events = run.pop("events", None)
    parts = [(f"{op}.{rid}", (None, json.dumps(run).encode(), "application/json"))]
    for k, v in [("inputs", inputs), ("outputs", outputs), ("events", events)]:
        if v is not None:
            parts.append((f"{op}.{rid}.{k}", (None, json.dumps(v).encode(), "application/json")))
    return parts

def batch(posts=None, patches=None):
    parts = []
    for op, runs in (("post", posts or []), ("patch", patches or [])):
        for r in runs:
            parts.extend(serialize(op, dict(r)))
    enc = MultipartEncoder(fields=parts, boundary=uuid.uuid4().hex)
    requests.post(
        "https://api.smith.langchain.com/runs/multipart",
        data=enc,
        headers={"Content-Type": enc.content_type, "x-api-key": os.environ["LANGSMITH_API_KEY"]},
    ).raise_for_status()

parent = make_run("Parent", "chain", {"q": "…"})
child  = make_run("Child",  "llm",   {"messages": [...]}, parent_dotted=parent["dotted_order"])
batch(posts=[parent, child])

# Later: patch with end_time + outputs
batch(patches=[
    {**parent, "end_time": datetime.now(timezone.utc).isoformat(), "outputs": {"answer": "…"}},
    {**child,  "end_time": datetime.now(timezone.utc).isoformat(), "outputs": {"choices": [...]}},
])
```

Getting `dotted_order` wrong silently breaks the trace tree. Use the SDK if you can.

## Run schema fields (most-used)

| Field | Type | Notes |
|---|---|---|
| `id` | UUID | UUIDv7 recommended. |
| `name` | string | Display name. |
| `run_type` | string | `chain`, `llm`, `tool`, `retriever`, `embedding`, `prompt`, `parser`. |
| `inputs` / `outputs` | object | Free-form JSON. For `llm`, typically `{ "messages": [...] }`. |
| `start_time` / `end_time` | ISO 8601 | Required on POST / PATCH respectively. |
| `parent_run_id` | UUID | Set to nest under a parent. |
| `trace_id` | UUID | Required for multipart. Equals root run's `id`. |
| `dotted_order` | string | Required for multipart. `<ts>Z<uuid>` joined by dots. |
| `session_name` | string | Project name to log to. |
| `session_id` | UUID | Project ID (alternative to `session_name`). |
| `tags` | string[] | Free-form. |
| `extra.metadata` | object | Free-form metadata dict. |
| `events` | object[] | Streaming / intermediate events. |
| `error` | string | Error message; sets status to error. |
| `status` | string | `pending`, `success`, `error`. |
| `reference_example_id` | UUID | For evaluation runs. |

Full schema: see the LangSmith API reference (`/runs` POST/PATCH) and the run data format reference. Token-usage / cost fields (`prompt_tokens`, `completion_tokens`, `total_tokens`, `total_cost`, `first_token_time`) are populated by the server from `outputs` for `run_type="llm"`.

## Rate limits

Per service key / PAT, per 1-minute window:

| Endpoints | Limit |
|---|---|
| `POST` or `PATCH /runs*` | 5000 / min |
| `GET /runs/:id` | 30 / min |
| `POST /feedbacks*` | 5000 / min |
| `DELETE /sessions*` | 30 / min |

Exceeding returns `429`. The SDK batches up to 100 runs per session into a single request to stay well under these limits — direct REST callers should implement retry with exponential backoff and jitter.
