#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# The eval agent must talk directly to api.anthropic.com with ANTHROPIC_API_KEY.
# A shell-exported ANTHROPIC_BASE_URL (e.g. the LangSmith gateway) would route
# Claude Code through a proxy that rejects the Anthropic key with 403.
unset ANTHROPIC_BASE_URL

# Skills are injected natively via `--skills <dir>` (built by scripts/sweep.py),
# so nothing from this repo needs to be on harbor's path.

harbor run \
  --env-file "$REPO_DIR/.env" \
  --agent-setup-timeout-multiplier 3 \
  "$@"
