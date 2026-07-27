#!/usr/bin/env bash

# Test runner, split by scope. `unit`, `integration` and `tooling` run a
# single marker with coverage off, because `fail_under` applies to whatever
# ran and a partial run cannot reach it. `all` (default) runs everything and
# is the only subcommand that measures coverage.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck disable=SC1091 source=scripts/log.sh
source "$SCRIPT_DIR/log.sh"

run_marker() {
    local marker="$1"
    local failed=0

    log_step "pytest -m $marker"
    if ! uv run python -m pytest -m "$marker" --no-cov; then
        log_error "The $marker tests failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_unit() {
    run_marker unit
}

run_integration() {
    run_marker integration
}

run_tooling() {
    run_marker tooling
}

run_all() {
    local failed=0

    log_step "py-compile"
    if ! uv run python -m compileall -q src tests; then
        log_error "Compile check failed"
        failed=1
    fi
    log_step_end

    log_step "pytest"
    if ! uv run python -m pytest; then
        log_error "Tests failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

main() {
    case "${1:-all}" in
    unit) run_unit ;;
    integration) run_integration ;;
    tooling) run_tooling ;;
    all)
        if ! run_all; then
            log_error "One or more test checks failed"
            exit 1
        fi
        log_success "All tests passed"
        ;;
    *)
        echo "Usage: $(basename "$0") [unit|integration|tooling|all]" >&2
        exit 1
        ;;
    esac
}

main "$@"
