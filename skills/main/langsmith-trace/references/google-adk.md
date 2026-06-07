# Tracing Google ADK applications

Use LangSmith's first-party `configure_google_adk()` helper — no manual OTel wiring needed.

## Install

```bash
pip install "langsmith[google-adk]"
```

## Env

```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=<project>
GOOGLE_API_KEY=<key>
```

## Setup

```python
from langsmith.integrations.google_adk import configure_google_adk

configure_google_adk(
    project_name="my-adk-project",   # optional, defaults to LANGSMITH_PROJECT
    name="google_adk.session",       # optional root trace name
    metadata={"environment": "production", "team": "ml-platform"},
    tags=["adk", "v2"],
)
```

Call **once at startup, before** creating any `Agent`. The helper installs a `TracerProvider` + LangSmith exporter automatically.

`configure_google_adk()` parameters:
- `project_name` — LangSmith project. Defaults to `LANGSMITH_PROJECT`.
- `name` — root trace name. Defaults to `"google_adk.session"`.
- `metadata` — dict of key-value context.
- `tags` — list of strings.

## Run

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    instruction="Use the get_weather tool to answer weather questions.",
    tools=[get_weather],
)

runner = Runner(agent=agent, app_name="weather_app", session_service=InMemorySessionService())
async for event in runner.run_async(user_id="u", session_id="s",
        new_message=types.Content(role="user", parts=[types.Part(text="...")])):
    ...
```

## Multi-agent workflows

`SequentialAgent` and parallel agent compositions are auto-traced under the same root — no extra config:

```python
from google.adk.agents import Agent, SequentialAgent

translator = Agent(name="translator", model="gemini-2.0-flash",
                   description="Translates text to English.")
summarizer = Agent(name="summarizer", model="gemini-2.0-flash",
                   description="Summarizes text concisely.")

pipeline = SequentialAgent(
    name="translate_and_summarize",
    sub_agents=[translator, summarizer],
)
```

## What gets traced

- Agent invocations (full flow through ADK agents)
- Tool calls (individual function invocations)
- Gemini LLM requests/responses
- Multi-agent workflows (sequential + parallel compositions)
