#!/usr/bin/env bash
# Main experiment runner
# Source this file or run directly
#
# Usage:
#   ./run_experiment.sh <test_module> [options]
#
# Examples:
#   ./run_experiment.sh tests.langchain_agent.test_noise -r 1 -w 3
#   ./run_experiment.sh tests.langsmith_synergy.test_basic --treatments BASIC_CONTROL BASIC_SKILLS

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# =============================================================================
# EXPERIMENT RUNNER
# =============================================================================

run_experiment() {
    local module="$1"
    shift

    log_info "Running experiment: $module"

    # Load environment
    local project_root
    project_root="$(get_project_root)"
    load_env "$project_root/.env"

    # Run the Python test module
    run_python_module "$module" "$@"
}

# =============================================================================
# CLI MODE
# =============================================================================

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <test_module> [options]"
    echo ""
    echo "Arguments:"
    echo "  test_module    Python module path (e.g., tests.langchain_agent.test_noise)"
    echo ""
    echo "Options are passed through to the Python module."
    echo ""
    echo "Examples:"
    echo "  $0 tests.langchain_agent.test_noise -r 1 -w 3"
    echo "  $0 tests.langsmith_synergy.test_basic --treatments BASIC_CONTROL"
    exit 1
fi

run_experiment "$@"
