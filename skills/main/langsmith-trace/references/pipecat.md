# Tracing Pipecat applications

Pipecat emits OTel spans but needs a custom `langsmith_processor` to map them to LangSmith. Available from the Pipecat demo repo.

## Install

```bash
pip install langsmith "pipecat-ai[whisper,openai,local]" \
    opentelemetry-exporter-otlp python-dotenv
# or: uv add langsmith "pipecat-ai[whisper,openai,local]" opentelemetry-exporter-otlp python-dotenv

# Optional, for audio attachments:
pip install scipy numpy
```

Requires Python 3.9+.

## Env (`.env`)

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://api.smith.langchain.com/otel
OTEL_EXPORTER_OTLP_HEADERS=x-api-key=<key>, Langsmith-Project=pipecat-voice
OPENAI_API_KEY=<key>
```

## Setup

Drop `langsmith_processor.py` next to your agent (the demo repo file). Importing it auto-registers the processor.

```python
import asyncio, uuid
from dotenv import load_dotenv
load_dotenv()    # MUST run before importing Pipecat components

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.whisper.stt import WhisperSTTService
from pipecat.services.openai import OpenAILLMService, OpenAITTSService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from langsmith_processor import span_processor   # auto-registers on import

async def main():
    conversation_id = str(uuid.uuid4())

    transport = LocalAudioTransport(LocalAudioTransportParams(
        audio_in_enabled=True, audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ))
    stt = WhisperSTTService()
    llm = OpenAILLMService(model="gpt-4o-mini")
    tts = OpenAITTSService(voice="alloy")

    context = OpenAILLMContext(messages=[
        {"role": "system", "content": "You are a helpful voice assistant."}
    ])
    ctx = llm.create_context_aggregator(context)

    pipeline = Pipeline([
        transport.input(), stt, ctx.user(),
        llm, tts,
        transport.output(), ctx.assistant(),
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(enable_metrics=True),
        enable_tracing=True,
        enable_turn_tracking=True,    # required for per-turn audio
        conversation_id=conversation_id,
    )
    await PipelineRunner().run(task)

if __name__ == "__main__":
    asyncio.run(main())
```

## What the processor does

- Maps Pipecat span types (`stt`, `llm`, `tts`, `turn`, `conversation`) to LangSmith run types
- Adds `gen_ai.prompt.*` / `gen_ai.completion.*` so messages render
- Aggregates messages across turns
- Handles audio file attachments

## Custom metadata and tags

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("voice_conversation") as span:
    span.set_attribute("langsmith.metadata.session_type", "voice_assistant")
    span.set_attribute("langsmith.metadata.user_id", "user_123")
    span.set_attribute("langsmith.span.tags", "pipecat,voice-ai,stt-llm-tts")
```

## Audio attachments

`AudioRecorder` (full conversation) and `TurnAudioRecorder` (per-turn) — both register with `span_processor` and attach `.wav` files to the trace. `AudioRecorder` handles sample-rate mismatches between mic input and TTS output.

```python
from pathlib import Path
from datetime import datetime
from audio_recorder import AudioRecorder

recordings_dir = Path(__file__).parent / "recordings"
recordings_dir.mkdir(exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
recording_path = recordings_dir / f"conversation_{ts}.wav"

audio_recorder = AudioRecorder(str(recording_path))
span_processor.register_recording(conversation_id, str(recording_path), audio_recorder=audio_recorder)

pipeline = Pipeline([
    transport.input(), stt, ctx.user(),
    llm, tts,
    audio_recorder,             # full conversation
    transport.output(), ctx.assistant(),
])

try:
    await PipelineRunner().run(task)
finally:
    audio_recorder.save_recording()   # MUST run before conversation span closes
```

Per-turn:

```python
from turn_audio_recorder import TurnAudioRecorder

turn_audio_recorder = TurnAudioRecorder(
    span_processor=span_processor,
    conversation_id=conversation_id,
    recordings_dir=recordings_dir,
    turn_tracker=None,
)
span_processor.register_turn_audio_recorder(conversation_id, turn_audio_recorder)

pipeline = Pipeline([
    transport.input(), stt, ctx.user(),
    llm, tts,
    audio_recorder,
    turn_audio_recorder,        # per-turn snippets
    transport.output(), ctx.assistant(),
])

# After PipelineTask creation:
if task.turn_tracking_observer:
    turn_audio_recorder.connect_to_turn_tracker(task.turn_tracking_observer)
```

## Common issues

- **Spans missing**: verify `OTEL_EXPORTER_OTLP_ENDPOINT` + `OTEL_EXPORTER_OTLP_HEADERS` in `.env`; confirm API key has write permissions; ensure `langsmith_processor` is imported.
- **`load_dotenv()` order**: must run **before** importing Pipecat components.
- **Messages don't render**: confirm `langsmith_processor.py` is present and imported; set a unique `conversation_id`; pass `enable_turn_tracking=True` to `PipelineTask`.
- **Per-turn audio**: requires `enable_turn_tracking=True`.
- **Audio not working**: check mic permissions, test devices in another app, adjust `SileroVADAnalyzer()` settings, validate OpenAI API access for Whisper/TTS.
- **Slow responses**: use `gpt-4o-mini`, check network, consider local Whisper.
