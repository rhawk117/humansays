#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=../../../scripts/log.sh
source "$GITHUB_WORKSPACE/scripts/log.sh"

log_step "Exporting locked requirements"
uv export --frozen --no-hashes --no-emit-project --color never > requirements.txt
log_step_end

log_step "Running pip-audit (OSV vulnerability service)"
set +e
uv tool run pip-audit \
  --vulnerability-service osv \
  -r requirements.txt \
  --format markdown > pip-audit-output.md
audit_exit=$?
set -e
log_step_end

if [[ $audit_exit -ne 0 ]]; then
  log_error "pip-audit reported findings in the locked dependency graph"
  cat pip-audit-output.md
  exit "$audit_exit"
fi

log_success "No known vulnerabilities found"
