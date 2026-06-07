# Tracing n8n workflows

n8n's AI nodes are built on LangChain, so tracing is **env-var-only** — no code changes. **Self-hosted n8n only.**

## Required env (on the n8n host)

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<your-langsmith-api-key>
```

## Optional

```bash
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com  # set for EU/AWS/self-hosted LangSmith
# EU:  https://eu.api.smith.langchain.com
# AWS: https://aws.api.smith.langchain.com
LANGCHAIN_PROJECT=my-project
LANGCHAIN_CALLBACKS_BACKGROUND=true   # async upload (default); false for sync
```

Restart the n8n instance for env vars to take effect.

## Notes

- The variable names use the legacy `LANGCHAIN_*` prefix (not `LANGSMITH_*`) — this is what n8n's AI runtime reads.
- Cloud-hosted n8n does **not** support tracing.
- All AI workflow runs land in the configured project; non-AI workflows are not traced.
