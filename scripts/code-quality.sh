#!/usr/bin/env bash

# quality gate for proj every command except `format` is
# check-only and never modifies repository files; CI runs `all`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=scripts/log.sh
source "$SCRIPT_DIR/log.sh"

SHELL_SCRIPTS=(scripts/*.sh)
BASHATE_IGNORES="E003,E006"

run_lint() {
    local failed=0

    log_step "ruff format --check"
    if ! uv run ruff format . --check; then
        log_error "Format check failed; run 'bash scripts/code-quality.sh format'"
        failed=1
    fi
    log_step_end

    log_step "ruff check (no fixes)"
    if ! uv run ruff check . --no-fix; then
        log_error "Lint check failed"
        failed=1
    fi
    log_step_end

    return "$failed"
}

run_shell() {
    local failed=0

    log_step "bashate"
    if ! uv run bashate -i "$BASHATE_IGNORES" "${SHELL_SCRIPTS[@]}"; then
        log_error "Shell lint failed"
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

# Mutating: local use only. Never wired into `all` or CI.
run_format() {
    log_step "ruff format"
    uv run ruff format .
    log_step_end

    log_step "ruff check --fix"
    uv run ruff check . --fix --unsafe-fixes
    log_step_end

    log_success "Formatting complete"
}

run_all() {
    local failed=0

    run_lint || failed=1
    run_shell || failed=1
    run_typecheck || failed=1
    run_test || failed=1
    run_validate || failed=1

    if [[ $failed -eq 1 ]]; then
        log_error "One or more quality checks failed"
        exit 1
    fi

    log_success "All quality checks passed"
}

case "${1:-all}" in
lint) run_lint || exit 1 ;;
shell) run_shell || exit 1 ;;
typecheck) run_typecheck || exit 1 ;;
test) run_test || exit 1 ;;
validate) run_validate || exit 1 ;;
format) run_format ;;
all) run_all ;;
*)
    echo "Usage: $(basename "$0") [lint|shell|typecheck|test|validate|format|all]" >&2
    exit 1
    ;;
esac
