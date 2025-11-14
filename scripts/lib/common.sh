#!/bin/bash
# Common utilities for all scripts
# Source this file in other scripts: source "$(dirname "$0")/lib/common.sh"

# ==================== Color Definitions ====================
# ANSI color codes for terminal output
export GREEN='\033[0;32m'
export BLUE='\033[0;34m'
export YELLOW='\033[1;33m'
export RED='\033[0;31m'
export NC='\033[0m' # No Color

# ==================== Logging Functions ====================

# Print a blue header with border
# Usage: print_header "Title Text"
print_header() {
    local title="$1"
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  ${title}${NC}"
    echo -e "${BLUE}================================================${NC}"
}

# Print an info message in green with [INFO] prefix
# Usage: log_info "Processing started..."
log_info() {
    echo -e "${GREEN}[INFO] $*${NC}"
}

# Print a success message in green with checkmark
# Usage: log_success "Operation completed!"
log_success() {
    echo -e "\n${GREEN}✅ $*${NC}"
}

# Print a warning message in yellow with [WARNING] prefix
# Usage: log_warning "This might take a while..."
log_warning() {
    echo -e "${YELLOW}[WARNING] $*${NC}"
}

# Print an error message in red with [ERROR] prefix
# Usage: log_error "Failed to connect"
log_error() {
    echo -e "${RED}[ERROR] $*${NC}" >&2
}

# Print a note/tip in yellow
# Usage: log_note "Tip: Use --help for more options"
log_note() {
    echo -e "${YELLOW}$*${NC}"
}

# ==================== Pytest Helpers ====================

# Run pytest with consistent formatting and error handling
# Usage: run_pytest "test_k8s/" "-v -s"
# Usage: run_pytest "app/tests/" "-v" "Testing Flask application"
run_pytest() {
    local test_path="${1:-test_k8s/}"
    local pytest_args="${2:--v}"
    local description="${3:-}"
    
    if [ -n "$description" ]; then
        log_note "$description"
        echo ""
    fi
    
    # Run pytest and capture exit code
    # Use eval to properly handle quoted arguments in pytest_args
    if eval pytest '"$test_path"' $pytest_args; then
        return 0
    else
        log_error "Pytest failed with exit code $?"
        return 1
    fi
}

# ==================== Validation Helpers ====================

# Check if a command exists
# Usage: command_exists "kubectl" || { log_error "kubectl not found"; exit 1; }
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're in a git repository
# Usage: check_git_repo
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not a git repository"
        return 1
    fi
    return 0
}

# ==================== Script Initialization ====================

# Get the absolute path to the scripts directory
# Usage: SCRIPTS_DIR=$(get_scripts_dir)
get_scripts_dir() {
    local script_path
    script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    echo "$script_path"
}

# Get the project root directory (parent of scripts/)
# Usage: PROJECT_ROOT=$(get_project_root)
get_project_root() {
    local script_path
    script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    echo "$script_path"
}
