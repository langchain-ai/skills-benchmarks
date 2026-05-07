# Tracing OpenCode sessions

The `@langchain/langsmith-opencode` plugin captures OpenCode session turns, tool calls, and subagent activity. Tracing is disabled by default — enable via env var or config file.

## Prerequisites

- OpenCode installed and configured
- A LangSmith API key
- Access to edit `opencode.json` or `~/.config/opencode/opencode.json`

## Install and enable the plugin

Add the plugin to `opencode.json` (project) or `~/.config/opencode/opencode.json` (global):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@langchain/langsmith-opencode"]
}
```

## Env

```bash
TRACE_TO_LANGSMITH=true
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=opencode
```

Run OpenCode as usual; the plugin sends completed user turns to the configured project.

OpenCode-specific overrides take precedence over generic LangSmith vars:

| Variable | Required | Default | Falls back to | Description |
|---|---|---|---|---|
| `TRACE_TO_LANGSMITH` | Yes | `false` | — | Set to `"true"` to enable tracing |
| `LANGSMITH_OPENCODE_API_KEY` | Conditional | — | `LANGSMITH_API_KEY` | Required unless every replica supplies its own key |
| `LANGSMITH_OPENCODE_ENDPOINT` | No | LangSmith SDK default | `LANGSMITH_ENDPOINT` | LangSmith API URL |
| `LANGSMITH_OPENCODE_PROJECT` | No | `opencode` | `LANGSMITH_PROJECT` | Project name |
| `LANGSMITH_OPENCODE_METADATA` | No | — | — | JSON object merged into root trace metadata |
| `LANGSMITH_OPENCODE_RUNS_ENDPOINTS` | No | — | — | JSON array of replica destinations |

```bash
export LANGSMITH_OPENCODE_METADATA='{"team":"agents","environment":"dev"}'
```

## Config file

`.opencode/langsmith.json` (project) or `~/.config/opencode/langsmith.json` (global):

```json
{
  "enabled": true,
  "api_key": "<key>",
  "api_url": "https://api.smith.langchain.com",
  "project": "opencode",
  "metadata": {"team": "agents", "environment": "dev"}
}
```

| Field | Required | Default | Description |
|---|---|---|---|
| `enabled` | Yes | `false` | Set to `true` to enable from config |
| `api_key` | Conditional | — | Required unless provided via env or replicas |
| `api_url` | No | LangSmith SDK default | Usually `https://api.smith.langchain.com` |
| `project` | No | `opencode` | Project name |
| `metadata` | No | — | Object merged into root trace metadata |
| `replicas` | No | — | Additional destinations to fan-out to |

Keep config files containing API keys out of version control.

## Multi-destination replicas

Set `replicas` in `langsmith.json` or `LANGSMITH_OPENCODE_RUNS_ENDPOINTS` to send the same trace to additional workspaces or projects:

```json
{
  "enabled": true,
  "api_key": "<key>",
  "project": "opencode",
  "replicas": [
    {
      "api_url": "https://api.smith.langchain.com",
      "api_key": "<replica-key>",
      "project": "opencode-replica",
      "updates": {"metadata": {"replica": true}}
    }
  ]
}
```

Replica objects accept both `snake_case` and SDK-style `camelCase` field names. Prefer `snake_case` in config files.

| Field | Description |
|---|---|
| `api_url` / `apiUrl` | LangSmith API URL for the destination |
| `api_key` / `apiKey` | API key for the destination workspace |
| `project` / `projectName` | Project name in the destination |
| `updates` | Optional run-field overrides (e.g. extra metadata) |

## What gets traced

- Root: `opencode.session` runs (one per completed user turn)
- Children: `opencode.assistant.turn`, tool calls (inputs/outputs/errors/timing/attachments), nested subagent sessions
- Metadata: model, provider, invocation params, token usage, thread/session ID
- Messages: user, assistant, reasoning blocks, file parts, system prompts
- Trace closes on `step-finish` events; pending batches flush on shutdown
- Session ID is stored as `thread_id` metadata — filter/group related turns in LangSmith with it

## Troubleshooting

- Confirm `TRACE_TO_LANGSMITH=true` (or `"enabled": true` in config)
- Confirm the API key is set in the same shell/config OpenCode uses
- Confirm the plugin package is resolvable by OpenCode
- Check the configured project — if none, traces go to `opencode`
- Restart OpenCode after editing `opencode.json`, `langsmith.json`, or env vars
- The plugin only sends **completed** turns — incomplete turns are dropped
