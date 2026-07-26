#!/usr/bin/env python3
"""Fail if a change touches files outside the current phase's scope.

Checks four sources, because a committed-diff-only check is trivially bypassed:
committed changes on the branch, staged changes, unstaged changes, and
untracked files.

Pattern file format (docs/phases/<phase>/allowed-paths.txt):

    # comment
    src/humansays/**          allow
    !src/humansays/analysis/signature*   deny, overrides any allow

Glob semantics are POSIX-like, not bash `[[ ]]`:
    *   matches within one path segment (does not cross /)
    **  matches any number of segments
    ?   matches one character within a segment

Usage: check_scope.py <phase> [--base REF]
Exit 0 clean, 1 violation, 2 usage or environment error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SELF = 'scripts/check_scope.py'
ALLOWLIST_NAME = 'allowed-paths.txt'


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    out: list[str] = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith('**/', i):
            out.append('(?:[^/]+/)*')
            i += 3
        elif pattern.startswith('**', i):
            out.append('.*')
            i += 2
        elif c == '*':
            out.append('[^/]*')
            i += 1
        elif c == '?':
            out.append('[^/]')
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile('^' + ''.join(out) + '$')


def load_patterns(path: Path) -> tuple[list[re.Pattern[str]], list[re.Pattern[str]]]:
    allow: list[re.Pattern[str]] = []
    deny: list[re.Pattern[str]] = []
    for raw in path.read_text().splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        if line.startswith('!'):
            deny.append(glob_to_regex(line[1:].strip()))
        else:
            allow.append(glob_to_regex(line))
    return allow, deny


def git(*args: str) -> list[str]:
    result = subprocess.run(  # noqa: S603
        ['git', *args],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f'git {" ".join(args)}: {result.stderr.strip()}')
    return [line for line in result.stdout.splitlines() if line.strip()]


def changed_files(base: str) -> dict[str, str]:
    """Map path -> which source flagged it. All four sources are checked."""
    sources = {
        'committed': ['diff', '--name-only', f'{base}...HEAD'],
        'staged': ['diff', '--name-only', '--cached'],
        'unstaged': ['diff', '--name-only'],
        'untracked': ['ls-files', '--others', '--exclude-standard'],
    }
    found: dict[str, str] = {}
    for label, argv in sources.items():
        for path in git(*argv):
            found.setdefault(path, label)
    return found


def widening_commits_are_isolated(base: str, phase: str) -> list[str]:
    """An allowlist change must be the only change in its commit."""
    allowlist = f'docs/phases/{phase}/{ALLOWLIST_NAME}'
    problems: list[str] = []
    for sha in git('rev-list', f'{base}..HEAD'):
        files = git('show', '--name-only', '--pretty=format:', sha)
        if allowlist in files and len(files) > 1:
            others = [f for f in files if f != allowlist]
            problems.append(
                f'{sha[:9]} changes the allowlist alongside {len(others)} '
                f'other file(s): {", ".join(others[:3])}'
                f'{" ..." if len(others) > 3 else ""}'
            )
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('phase')
    ap.add_argument('--base', default='origin/main')
    args = ap.parse_args()

    allowlist = Path(f'docs/phases/{args.phase}/{ALLOWLIST_NAME}')
    if not allowlist.is_file():
        print(f'no allowlist for phase {args.phase}', file=sys.stderr)
        return 2

    allow, deny = load_patterns(allowlist)
    try:
        changes = changed_files(args.base)
        widening = widening_commits_are_isolated(args.base, args.phase)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2

    violations: list[tuple[str, str, str]] = []
    for path, source in sorted(changes.items()):
        if path == SELF:
            violations.append((
                path,
                source,
                'the scope guard is not editable during a phase',
            ))
            continue
        if any(p.match(path) for p in deny):
            violations.append((path, source, 'explicitly denied for this phase'))
            continue
        if not any(p.match(path) for p in allow):
            violations.append((path, source, 'outside the allowlist'))

    if violations or widening:
        print(f'SCOPE VIOLATION — phase {args.phase}\n', file=sys.stderr)
        for path, source, why in violations:
            print(f'  {path}\n      [{source}] {why}', file=sys.stderr)
        for problem in widening:
            print(
                f'  allowlist widened in a mixed commit:\n      {problem}',
                file=sys.stderr,
            )
        print(
            f'\nIf a path is genuinely required, add it to {allowlist} in a commit\n'
            'containing nothing else, with a one-line reason.',
            file=sys.stderr,
        )
        return 1

    print(
        f'scope ok — {len(changes)} changed file(s) checked against '
        f'{len(allow)} allow / {len(deny)} deny pattern(s)'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
