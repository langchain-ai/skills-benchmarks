#!/usr/bin/env bash
# Main entry point for running experiments
#
# Usage:
#   ./run.sh <experiment> [options]
#
# Experiments:
#   noise          Run langchain_agent noise experiment
#   guidance       Run langchain_agent guidance experiment
#   claudemd       Run langchain_agent CLAUDE.md experiment
#   basic          Run langsmith_synergy basic experiment
#   advanced       Run langsmith_synergy advanced experiment
#
# Examples:
#   ./run.sh noise -r 1 -w 3
#   ./run.sh basic --treatments BASIC_CONTROL BASIC_SKILLS
#   ./run.sh advanced -r 2

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/scaffold/shell/common.sh"

# Map experiment names to Python modules
get_module() {
    local exp="$1"
    case "$exp" in
        noise)    echo "tests.langchain_agent.test_noise" ;;
        guidance) echo "tests.langchain_agent.test_guidance" ;;
        claudemd) echo "tests.langchain_agent.test_claudemd" ;;
        basic)    echo "tests.langsmith_synergy.test_basic" ;;
        advanced) echo "tests.langsmith_synergy.test_advanced" ;;
        *)        echo "" ;;
    esac
}

show_help() {
    echo "Usage: $0 <experiment> [options]"
    echo ""
    echo "Experiments:"
    echo "  noise          Langchain agent noise experiment"
    echo "  guidance       Langchain agent guidance experiment"
    echo "  claudemd       Langchain agent CLAUDE.md experiment"
    echo "  basic          LangSmith synergy basic experiment"
    echo "  advanced       LangSmith synergy advanced experiment"
    echo ""
    echo "Common options:"
    echo "  -r, --repeat N     Number of repetitions (default: 1)"
    echo "  -w, --workers N    Number of parallel workers (default: 3)"
    echo "  -t, --treatments   Specific treatments to run"
    echo "  --timeout N        Timeout per run in seconds"
    echo ""
    echo "Examples:"
    echo "  $0 noise -r 1 -w 3"
    echo "  $0 basic --treatments BASIC_CONTROL BASIC_SKILLS"
    echo "  $0 advanced -r 2"
}

# Parse experiment name
experiment="${1:-}"
if [[ -z "$experiment" || "$experiment" == "-h" || "$experiment" == "--help" ]]; then
    show_help
    exit 0
fi
shift

# Look up module
module="$(get_module "$experiment")"
if [[ -z "$module" ]]; then
    log_error "Unknown experiment: $experiment"
    echo ""
    show_help
    exit 1
fi

# Load environment
load_env "$SCRIPT_DIR/.env"

# Run the experiment
log_info "Running $experiment experiment..."
run_python_module "$module" "$@"
