#!/usr/bin/env bash
set -euo pipefail

bump="${1:-}"

if [[ ! "$bump" =~ ^(major|minor|patch|alpha|beta|rc|stable|post|dev)$ ]]; then
    printf 'usage: %s major|minor|patch|alpha|beta|rc|stable|post|dev\n' \
        "${0##*/}" >&2
    exit 2
fi

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$root"

# shellcheck source=scripts/log.sh
source "$root/scripts/log.sh"

uv version --bump "$bump" --no-sync

version="$(uv version --short)"
log_success "Prepared version $version"
log_info "Commit pyproject.toml and uv.lock together."
