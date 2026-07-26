#!/usr/bin/env bash
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
python_version="${1:-3.11}"
dist_dir="${2:-$root/dist}"

cd -- "$root"

# shellcheck source=scripts/log.sh
source "$root/scripts/log.sh"

mapfile -t artifacts < <(
    find "$dist_dir" -maxdepth 1 -type f \( -name '*.whl' -o -name '*.tar.gz' \) -print | sort
)

if ((${#artifacts[@]} != 2)); then
    log_error "Expected one wheel and one sdist in $dist_dir, found ${#artifacts[@]}"
    exit 1
fi

for artifact in "${artifacts[@]}"; do
    log_step "Smoke testing $(basename -- "$artifact")"
    uv run \
        --python "$python_version" \
        --isolated \
        --no-project \
        --with "$artifact" \
        scripts/smoke_test_package.py
    log_step_end
done
