#!/usr/bin/env bash
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
python_version="${1:-3.11}"
dist_dir="${2:-$root/dist}"

cd -- "$root"

# shellcheck source=scripts/log.sh
source "$root/scripts/log.sh"

mapfile -t wheels < <(
    find "$dist_dir" -maxdepth 1 -type f -name '*.whl' -print
)

if ((${#wheels[@]} != 1)); then
    log_error "Expected exactly one wheel in $dist_dir, found ${#wheels[@]}"
    exit 1
fi

uv run \
    --python "$python_version" \
    --isolated \
    --no-project \
    --with "${wheels[0]}" \
    scripts/smoke_test_package.py
