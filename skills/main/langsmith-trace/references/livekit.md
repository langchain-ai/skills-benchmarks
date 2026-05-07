# Tracing LiveKit applications

LiveKit Agents emits OTel spans, but they need a custom processor (`LangSmithSpanProcessor`) to be readable in LangSmith. Available via the LiveKit demo repo.

Python 3.9+.

## Install

```bash
pip install langsmith livekit livekit-agents \
    livekit-plugins-openai livekit-plugins-silero livekit-plugins-turn-detector \
    opentelemetry-exporter-otlp python-dotenv
```

Or with `uv`:

```bash
uv add langsmith livekit livekit-agents \
    livekit-plugins-openai livekit-plugins-silero livekit-plugins-turn-detector \
    opentelemetry-exporter-otlp python-dotenv
```

## Env (`.env`)

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.smith.langchain.com/otel
OTEL_EXPORTER_OTLP_HEADERS=x-api-key=<key>, Langsmith-Project=<project>
LIVEKIT_URL=<url>
LIVEKIT_API_KEY=<key>
LIVEKIT_API_SECRET=<secret>
OPENAI_API_KEY=<key>
```

## Setup

Get `langsmith_processor.py` from the LiveKit demo repo, drop it next to your agent, then enable tracing **before** creating `AgentServer`:

```python
import os
from dotenv import load_dotenv
from livekit.agents.telemetry import set_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from langsmith_processor import LangSmithSpanProcessor

load_dotenv()

def setup_langsmith():
    if not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or not os.getenv("OTEL_EXPORTER_OTLP_HEADERS"):
        print("OTEL env vars not set; tracing disabled.")
        return
    provider = TracerProvider()
    provider.add_span_processor(LangSmithSpanProcessor())
    set_tracer_provider(provider)

setup_langsmith()  # call BEFORE creating AgentServer
```

The processor:
- Maps LiveKit span types (`stt`, `llm`, `tts`, `agent`, `session`, `job`) to LangSmith run types
- Adds `gen_ai.prompt.*` / `gen_ai.completion.*` for message rendering
- Aggregates conversation messages across turns
- Uses multiple extraction strategies for varying LiveKit attribute formats

## Agent skeleton

```python
import sys
from livekit import agents
from livekit.agents import AgentServer, AgentSession, Agent
from livekit.plugins import openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

class Assistant(Agent):
    def __init__(self):
        super().__init__(instructions="You are a helpful voice AI assistant.")

server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        stt="deepgram/nova-2:en",
        llm="openai/gpt-4o-mini",
        tts=openai.TTS(model="tts-1", voice="alloy"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    await session.start(room=ctx.room, agent=Assistant())

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "console"]
    agents.cli.run_app(server)
```

Run locally: `python agent.py console`.

## Custom metadata and tags

```python
from opentelemetry import trace

span = trace.get_current_span()
span.set_attribute("langsmith.metadata.agent_type", "voice_assistant")
span.set_attribute("langsmith.metadata.version", "1.0")
span.set_attribute("langsmith.span.tags", "livekit,voice-ai,production")
```

## Gotchas

- **Spans missing**: confirm `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_HEADERS` are set, and that `setup_langsmith()` runs **before** `AgentServer()`.
- **Messages not rendering**: confirm `LangSmithSpanProcessor` is imported and registered; set `LANGSMITH_PROCESSOR_DEBUG=true` for verbose logs.
- **API key permissions**: LangSmith key needs write access on the target workspace.
- **Connection issues**: verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`; test with the LiveKit CLI first.
- **Agent not responding**: check provider keys (OpenAI/Deepgram/etc.) and that STT/LLM/TTS endpoints are reachable.
- **Import errors**: ensure all `livekit-plugins-*` packages match the providers your `AgentSession` references; Python 3.9+ required.
