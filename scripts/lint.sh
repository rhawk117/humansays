#!/usr/bin/env bash

# Static analysis. Every check is read-only and never modifies repository
# files. Run a single check by name, or `all` (default) to run every check
# and aggregate the result.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=scripts/log.sh
source "$SCRIPT_DIR/log.sh"

run_format() {
    local failed=0

    log_step "ruff format --check"
    if ! uv run ruff format . --check; then
        log_error "Format check failed; run 'make format'"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_ruff() {
    local failed=0

    log_step "ruff check (no fixes)"
    if ! uv run ruff check . --no-fix; then
        log_error "Lint check failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_typecheck() {
    local failed=0

    log_step "ty check"
    if ! uv run ty check; then
        log_error "Type check failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_shell() {
    local failed=0

    require_cmd shellcheck
    require_cmd shfmt

    log_step "shellcheck"
    if ! shellcheck scripts/*.sh; then
        log_error "Shell lint failed"
        failed=1
    fi
    log_step_end

    log_step "shfmt --diff"
    if ! shfmt -d scripts/*.sh; then
        log_error "Shell format check failed; run 'make format'"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_security() {
    local failed=0

    log_step "bandit"
    if ! uv run bandit -c .bandit.yaml -r src; then
        log_error "Security scan failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_deps() {
    local failed=0

    log_step "deptry"
    if ! uv run deptry src; then
        log_error "Dependency check failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_imports() {
    local failed=0

    log_step "import-linter"
    if ! uv run lint-imports --config .importlinter.ini; then
        log_error "Import contract check failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_deadcode() {
    local failed=0

    log_step "vulture"
    if ! uv run vulture; then
        log_error "Dead code check failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_all() {
    local failed=0

    run_format || failed=1
    run_ruff || failed=1
    run_typecheck || failed=1
    run_shell || failed=1
    run_security || failed=1
    run_deps || failed=1
    run_imports || failed=1
    run_deadcode || failed=1

    return "$failed"
}

main() {
    case "${1:-all}" in
    format) run_format ;;
    ruff) run_ruff ;;
    typecheck) run_typecheck ;;
    shell) run_shell ;;
    security) run_security ;;
    deps) run_deps ;;
    imports) run_imports ;;
    deadcode) run_deadcode ;;
    all)
        if ! run_all; then
            log_error "One or more lint checks failed"
            exit 1
        fi
        log_success "All lint checks passed"
        ;;
    *)
        echo "Usage: $(basename "$0") [format|ruff|typecheck|shell|security|deps|imports|deadcode|all]" >&2
        exit 1
        ;;
    esac
}

main "$@"
