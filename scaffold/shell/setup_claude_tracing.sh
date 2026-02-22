#!/bin/bash
###
# Setup Claude Code -> LangSmith Tracing
#
# This script configures Claude Code to send traces to LangSmith.
# Run once to set up tracing for all Claude Code sessions.
#
# Usage:
#   ./setup_claude_tracing.sh [project-name]
#
# Requirements:
#   - Claude Code CLI installed
#   - jq command-line tool
#   - LangSmith API key
###

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default project name
PROJECT_NAME="${1:-claude-code}"

# Check requirements
for cmd in jq claude; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: $cmd is required but not installed" >&2
        exit 1
    fi
done

# Check for API key
if [ -z "${LANGSMITH_API_KEY:-}" ] && [ -z "${CC_LANGSMITH_API_KEY:-}" ]; then
    echo "Error: LANGSMITH_API_KEY or CC_LANGSMITH_API_KEY must be set" >&2
    exit 1
fi

API_KEY="${CC_LANGSMITH_API_KEY:-$LANGSMITH_API_KEY}"

# Create hooks directory
HOOKS_DIR="$HOME/.claude/hooks"
mkdir -p "$HOOKS_DIR"

# Copy stop_hook.sh
cp "$SCRIPT_DIR/stop_hook.sh" "$HOOKS_DIR/stop_hook.sh"
chmod +x "$HOOKS_DIR/stop_hook.sh"
echo "Installed stop_hook.sh to $HOOKS_DIR/"

# Create or update settings.json with hook configuration
SETTINGS_FILE="$HOME/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    # Merge with existing settings
    EXISTING=$(cat "$SETTINGS_FILE")
    NEW_SETTINGS=$(echo "$EXISTING" | jq --arg script "$HOOKS_DIR/stop_hook.sh" '
        .hooks = (.hooks // {}) |
        .hooks.Stop = [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": ("bash " + $script)
                    }
                ]
            }
        ]
    ')
else
    # Create new settings
    NEW_SETTINGS=$(jq -n --arg script "$HOOKS_DIR/stop_hook.sh" '{
        hooks: {
            Stop: [
                {
                    hooks: [
                        {
                            type: "command",
                            command: ("bash " + $script)
                        }
                    ]
                }
            ]
        }
    }')
fi

echo "$NEW_SETTINGS" > "$SETTINGS_FILE"
echo "Updated $SETTINGS_FILE with hook configuration"

# Create state directory
mkdir -p "$HOME/.claude/state"

echo ""
echo "Claude Code tracing setup complete!"
echo ""
echo "To enable tracing for a project, add to .claude/settings.local.json:"
echo ""
echo "{"
echo "  \"env\": {"
echo "    \"TRACE_TO_LANGSMITH\": \"true\","
echo "    \"CC_LANGSMITH_API_KEY\": \"$API_KEY\","
echo "    \"CC_LANGSMITH_PROJECT\": \"$PROJECT_NAME\""
echo "  }"
echo "}"
echo ""
echo "Or set these environment variables before running Claude Code."
