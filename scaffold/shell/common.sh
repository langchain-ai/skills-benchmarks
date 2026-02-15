#!/usr/bin/env bash
# Common shell utilities for test orchestration
# Source this file: source "$(dirname "$0")/../../scaffold/shell/common.sh"

set -euo pipefail

# =============================================================================
# COLORS
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# LOGGING
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# =============================================================================
# ERROR HANDLING
# =============================================================================

die() {
    log_error "$@"
    exit 1
}

# =============================================================================
# PATH UTILITIES
# =============================================================================

# Get the absolute path to the scaffold directory
get_scaffold_dir() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

# Get the absolute path to the project root
get_project_root() {
    local scaffold_dir
    scaffold_dir="$(get_scaffold_dir)"
    echo "$(dirname "$scaffold_dir")"
}

# =============================================================================
# PYTHON HELPERS
# =============================================================================

# Find python3 executable
find_python() {
    if command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        die "Python not found. Please install Python 3."
    fi
}

# Run a Python module from the project root
run_python_module() {
    local module="$1"
    shift
    local python
    python="$(find_python)"
    local project_root
    project_root="$(get_project_root)"

    cd "$project_root"
    PYTHONPATH="$project_root" "$python" -m "$module" "$@"
}

# Run a Python script
run_python_script() {
    local script="$1"
    shift
    local python
    python="$(find_python)"
    local project_root
    project_root="$(get_project_root)"

    PYTHONPATH="$project_root" "$python" "$script" "$@"
}

# =============================================================================
# ENVIRONMENT
# =============================================================================

# Load .env file if it exists
load_env() {
    local env_file="${1:-.env}"
    if [[ -f "$env_file" ]]; then
        set -a
        # shellcheck source=/dev/null
        source "$env_file"
        set +a
        log_info "Loaded environment from $env_file"
    fi
}

# Check required environment variables
require_env() {
    local var_name="$1"
    if [[ -z "${!var_name:-}" ]]; then
        die "Required environment variable $var_name is not set"
    fi
}
