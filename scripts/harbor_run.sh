#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The eval agent's Anthropic calls route through the LangSmith LLM Gateway.
# .env sets ANTHROPIC_BASE_URL (the gateway) and ANTHROPIC_API_KEY (the LangSmith
# key); the claude-code adapter forwards both into the run.

# Skills are injected natively via `--skills <dir>` (built by scripts/sweep.py),
# so nothing from this repo needs to be on harbor's path.

harbor run \
  --env-file "$REPO_DIR/.env" \
  --agent-setup-timeout-multiplier 3 \
  --environment-build-timeout-multiplier 5 \
  "$@"
