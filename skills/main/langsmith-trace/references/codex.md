# Tracing OpenAI Codex sessions

The `langsmith-codex-plugins` marketplace provides a tracing plugin for Codex CLI v0.128+. Tracing is disabled until either `TRACE_TO_LANGSMITH=true` or `enabled: true` is set in a config file.

## Prerequisites

- Codex CLI v0.128 or later
- A LangSmith API key

## Install and enable

```bash
codex plugin marketplace add langchain-ai/langsmith-codex-plugins
```

Enable plugin hooks and the tracing plugin in `~/.codex/config.toml` (global) or `<project>/.codex/config.toml` (project):

```toml
[features]
plugin_hooks = true

[plugins."tracing@langsmith-codex-plugins"]
enabled = true
```

## Env

```bash
export TRACE_TO_LANGSMITH="true"
export LANGSMITH_CODEX_API_KEY="<key>"   # or LANGSMITH_API_KEY
export LANGSMITH_CODEX_PROJECT="codex"
```

Codex-specific overrides take precedence over generic LangSmith vars:

| Variable | Required | Default | Falls back to | Description |
|---|---|---|---|---|
| `TRACE_TO_LANGSMITH` | Yes | — | — | Set to `"true"` to enable tracing |
| `LANGSMITH_CODEX_API_KEY` | Conditional | — | `LANGSMITH_API_KEY` | Required unless every replica supplies its own key |
| `LANGSMITH_CODEX_ENDPOINT` | No | `https://api.smith.langchain.com` | `LANGSMITH_ENDPOINT` | LangSmith API URL |
| `LANGSMITH_CODEX_PROJECT` | No | `codex` | `LANGSMITH_PROJECT` | Project name |
| `LANGSMITH_CODEX_METADATA` | No | — | `LANGSMITH_METADATA` | JSON object merged into root trace metadata |
| `LANGSMITH_CODEX_RUNS_ENDPOINTS` | No | — | `LANGSMITH_RUNS_ENDPOINTS` | JSON array of replica destinations |

## Config file

`<project>/.codex/langsmith.json` (project) or `~/.codex/langsmith.json` (global):

```json
{
  "enabled": true,
  "api_key": "<key>",
  "api_url": "https://api.smith.langchain.com",
  "project": "codex",
  "metadata": {"team": "agents", "environment": "dev"}
}
```

Loading order: global file → project file → environment variables. Each layer overrides the prior. Keep config files with API keys out of version control.

| Field | Env var | Default | Description |
|---|---|---|---|
| `enabled` | `TRACE_TO_LANGSMITH` | `false` | Enable tracing |
| `api_key` | `LANGSMITH_CODEX_API_KEY`, `LANGSMITH_API_KEY` | — | LangSmith API key |
| `api_url` | `LANGSMITH_CODEX_ENDPOINT`, `LANGSMITH_ENDPOINT` | LangSmith default | API URL |
| `project` | `LANGSMITH_CODEX_PROJECT`, `LANGSMITH_PROJECT` | `codex` | Project name |
| `metadata` | `LANGSMITH_CODEX_METADATA`, `LANGSMITH_METADATA` | — | Root trace metadata |
| `replicas` | `LANGSMITH_CODEX_RUNS_ENDPOINTS`, `LANGSMITH_RUNS_ENDPOINTS` | — | Replica destinations |

## Multi-destination replicas

When `replicas` is set, it **replaces** (not augments) the single-destination client settings. Useful for prod+staging fan-out, multi-workspace tracing, or per-destination metadata.

Config file:

```json
{
  "enabled": true,
  "replicas": [
    {
      "apiUrl": "https://api.smith.langchain.com",
      "apiKey": "lsv2_pt_workspace_a",
      "projectName": "project-prod"
    },
    {
      "apiUrl": "https://api.smith.langchain.com",
      "apiKey": "lsv2_pt_workspace_b",
      "projectName": "project-staging",
      "updates": {"metadata": {"environment": "staging"}}
    }
  ]
}
```

Shell env-var alternative:

```bash
export LANGSMITH_CODEX_RUNS_ENDPOINTS='[{"apiUrl":"https://api.smith.langchain.com","apiKey":"lsv2_pt_workspace_a","projectName":"project-prod"},{"apiUrl":"https://api.smith.langchain.com","apiKey":"lsv2_pt_workspace_b","projectName":"project-staging","updates":{"metadata":{"environment":"staging"}}}]'
```

Generate the escaped JSON string with `jq -c .`:

```bash
echo '[{"apiUrl":"...","apiKey":"...","projectName":"..."}]' | jq -c .
```

Each replica object:

| Field | Required | Description |
|---|---|---|
| `apiUrl` | Yes | LangSmith API URL |
| `apiKey` | Yes | API key for the destination workspace |
| `projectName` | Yes | Project name in the destination |
| `updates` | No | Optional run-field overrides (e.g. extra metadata) |

## What gets traced

- Per LLM run: accumulated messages (inputs), assistant content (outputs), provider/model/stop-reason/token-usage metadata
- Tool calls: function calls, shell calls, computer calls, file reads, web searches — with inputs/outputs
- Subagent threads as nested child runs under the parent turn
- Cancelled/interrupted turns are still uploaded once the session completes

> The plugin uploads full Codex transcripts. Don't enable for sessions containing data you don't want stored in LangSmith.

## Troubleshooting

- Confirm `plugin_hooks = true` and the tracing plugin is enabled in `config.toml`
- Confirm `TRACE_TO_LANGSMITH=true` is visible to the Codex process
- Confirm `LANGSMITH_CODEX_API_KEY` or `LANGSMITH_API_KEY` is set and valid
- Wrong project? set `LANGSMITH_CODEX_PROJECT` or `project` in config
- Custom endpoint not used? set `LANGSMITH_CODEX_ENDPOINT` or `api_url` in config
