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

uv version --bump "$bump" --no-sync

version="$(uv version --short)"
printf 'Prepared version %s\n' "$version"
printf 'Commit pyproject.toml and uv.lock together.\n'
