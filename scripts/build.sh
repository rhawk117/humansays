#!/usr/bin/env bash
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
dist_dir="${1:-$root/dist}"

# shellcheck source=scripts/log.sh
source "$root/scripts/log.sh"

cd -- "$root"
rm -rf -- "$dist_dir"
mkdir -p -- "$dist_dir"

uv build --no-sources --out-dir "$dist_dir"
uv run --locked --group package twine check "$dist_dir"/*

mapfile -t wheels < <(
    find "$dist_dir" -maxdepth 1 -type f -name '*.whl' -print
)
mapfile -t sdists < <(
    find "$dist_dir" -maxdepth 1 -type f -name '*.tar.gz' -print
)

if ((${#wheels[@]} != 1)); then
    log_error "Expected exactly one wheel, found ${#wheels[@]}"
    exit 1
fi

if ((${#sdists[@]} != 1)); then
    log_error "Expected exactly one source distribution, found ${#sdists[@]}"
    exit 1
fi

log_info "Built ${wheels[0]}"
log_info "Built ${sdists[0]}"
