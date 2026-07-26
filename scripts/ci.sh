#!/usr/bin/env bash

# Full continuous-integration gate: static analysis (delegated to lint.sh),
# then tests, then package validation. Every check is read-only. `all`
# (default) runs the complete gate and aggregates the result.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=scripts/log.sh
source "$SCRIPT_DIR/log.sh"

run_lint() {
    bash "$SCRIPT_DIR/lint.sh" all
}

run_test() {
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

run_validate() {
    local failed=0
    local build_dir

    build_dir="$(mktemp -d)"

    log_step "uv lock --check"
    if ! uv lock --check; then
        log_error "Lockfile is stale; run 'uv lock'"
        failed=1
    fi
    log_step_end

    log_step "package build"
    if ! uv build --out-dir "$build_dir"; then
        log_error "Package build failed"
        failed=1
    fi
    log_step_end

    rm -rf "$build_dir"
    return "$failed"
}

run_all() {
    local failed=0

    run_lint || failed=1
    run_test || failed=1
    run_validate || failed=1

    return "$failed"
}

main() {
    case "${1:-all}" in
    test) run_test ;;
    validate) run_validate ;;
    all)
        if ! run_all; then
            log_error "One or more CI checks failed"
            exit 1
        fi
        log_success "All CI checks passed"
        ;;
    *)
        echo "Usage: $(basename "$0") [test|validate|all]" >&2
        exit 1
        ;;
    esac
}

main "$@"
