#!/usr/bin/env bash
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
dist_dir="${1:-$root/dist}"

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
  printf 'Expected exactly one wheel, found %s\n' "${#wheels[@]}" >&2
  exit 1
fi

if ((${#sdists[@]} != 1)); then
  printf 'Expected exactly one source distribution, found %s\n' \
    "${#sdists[@]}" >&2
  exit 1
fi

printf 'Built %s\n' "${wheels[0]}"
printf 'Built %s\n' "${sdists[0]}"
