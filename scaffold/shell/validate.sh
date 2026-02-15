#!/usr/bin/env bash
# Validation utilities for test orchestration
# Source this file after common.sh, or run directly
#
# Usage:
#   ./validate.sh python <module> <test_dir> <treatment> [outputs_json]
#   ./validate.sh script <script.py|script.js> <test_dir> <treatment> [outputs_json]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# =============================================================================
# VALIDATION RUNNERS
# =============================================================================

# Run Python validation module
# Usage: validate_python <module> <test_dir> <treatment_name> [outputs_json]
validate_python() {
    local module="$1"
    local test_dir="$2"
    local treatment="$3"
    local outputs_json="${4:-{}}"

    local python
    python="$(find_python)"
    local project_root
    project_root="$(get_project_root)"

    cd "$project_root"
    PYTHONPATH="$project_root" "$python" -c "
import json
import sys
from pathlib import Path
sys.path.insert(0, '$project_root')

from $module import validate_treatment

outputs = json.loads('$outputs_json')
events = {}  # Events would be passed in real usage
test_dir = Path('$test_dir')
treatment = '$treatment'

passed, failed = validate_treatment(events, test_dir, treatment, outputs)

print('PASSED:')
for p in passed:
    print(f'  {p}')
print('FAILED:')
for f in failed:
    print(f'  {f}')

sys.exit(0 if not failed else 1)
"
}

# Run a validation script directly (Python or JS)
# Usage: validate_script <script> <test_dir> <treatment_name> [outputs_json]
validate_script() {
    local script="$1"
    local test_dir="$2"
    local treatment="$3"
    local outputs_json="${4:-{}}"

    if [[ ! -f "$script" ]]; then
        die "Validation script not found: $script"
    fi

    local ext="${script##*.}"
    case "$ext" in
        py)
            local python
            python="$(find_python)"
            "$python" "$script" "$test_dir" "$treatment" "$outputs_json"
            ;;
        js)
            if command -v node &> /dev/null; then
                node "$script" "$test_dir" "$treatment" "$outputs_json"
            else
                die "Node.js not found. Please install Node.js to run JS validators."
            fi
            ;;
        sh)
            bash "$script" "$test_dir" "$treatment" "$outputs_json"
            ;;
        *)
            die "Unknown validator type: $ext (expected .py, .js, or .sh)"
            ;;
    esac
}

# =============================================================================
# CLI MODE
# =============================================================================

cmd="${1:-help}"
shift || true

case "$cmd" in
    python)
        module="${1:-}"
        test_dir="${2:-}"
        treatment="${3:-}"
        outputs="${4:-{}}"
        if [[ -z "$module" || -z "$test_dir" || -z "$treatment" ]]; then
            die "Usage: $0 python <module> <test_dir> <treatment> [outputs_json]"
        fi
        validate_python "$module" "$test_dir" "$treatment" "$outputs"
        ;;
    script)
        script="${1:-}"
        test_dir="${2:-}"
        treatment="${3:-}"
        outputs="${4:-{}}"
        if [[ -z "$script" || -z "$test_dir" || -z "$treatment" ]]; then
            die "Usage: $0 script <script> <test_dir> <treatment> [outputs_json]"
        fi
        validate_script "$script" "$test_dir" "$treatment" "$outputs"
        ;;
    help|*)
        echo "Usage: $0 <command> [args...]"
        echo ""
        echo "Commands:"
        echo "  python <module> <dir> <treatment> [outputs]   Run Python validator module"
        echo "  script <script> <dir> <treatment> [outputs]   Run validator script (.py/.js/.sh)"
        echo ""
        echo "Examples:"
        echo "  $0 python tests.langchain_agent.test_noise /tmp/test NOISE_1"
        echo "  $0 script validators.py /tmp/test NOISE_1 '{\"_run_id\": \"abc123\"}'"
        ;;
esac
