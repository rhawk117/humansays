#!/usr/bin/env bash

# Prepare a checkout for agent execution: install hooks, verify they work.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# shellcheck source=scripts/log.sh
source "$SCRIPT_DIR/log.sh"

require_cmd pre-commit

log_step "syncing dependency groups"
uv sync --all-groups
log_step_end

log_step "installing pre-commit and commit-msg hooks"
pre-commit install --hook-type pre-commit --hook-type commit-msg
log_step_end

for hook in pre-commit commit-msg; do
    if [[ ! -f ".git/hooks/${hook}" ]]; then
        log_error ".git/hooks/${hook} was not installed"
        exit 1
    fi
done

log_step "verifying the commit message validator"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

printf 'chore(precheck): probe\n' >"$tmp"
uv run python scripts/check_commit_msg.py "$tmp"

printf 'doc(precheck): probe\n' >"$tmp"
if uv run python scripts/check_commit_msg.py "$tmp" 2>/dev/null; then
    log_error "validator accepted an invalid prefix"
    exit 1
fi
log_step_end

log_success "ready"
