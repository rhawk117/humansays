"""Validate a commit message against the conventions in
`.agent-specs/process/agent-protocol.md` section 8.

Two accepted forms:

    prefix(scope): summary
    prefix(short-title): summary [merges #N]

Usage: check_commit_msg.py <path-to-message-file>
Exit 0 valid, 1 invalid, 2 usage error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PREFIXES = ('feat', 'chore', 'ops', 'fix', 'release', 'docs')

SUBJECT = re.compile(r'^(?P<prefix>[a-z]+)\((?P<scope>[^()\s]+)\): (?P<summary>\S.*)$')
MERGES = re.compile(r' \[merges #\d+\]$')


def is_valid(message: str) -> str | None:
    """Return None when the message is valid, else the reason it is not."""
    lines = [ln for ln in message.splitlines() if not ln.startswith('#')]
    subject = lines[0].strip() if lines else ''

    if not subject:
        return 'empty commit message'

    match = SUBJECT.match(MERGES.sub('', subject))
    if match is None:
        return (
            f'subject must be "prefix(scope): summary", got: {subject!r}\n'
            f'  valid prefixes: {"|".join(PREFIXES)}'
        )

    prefix = match.group('prefix')
    if prefix not in PREFIXES:
        return f'prefix {prefix!r} is not one of: {"|".join(PREFIXES)}'

    summary = match.group('summary')
    if summary[0].isupper():
        return f'summary must start lowercase, got: {summary!r}'

    if summary.endswith('.'):
        return f'summary must not end with a period, got: {summary!r}'

    return None


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    problem = is_valid(Path(sys.argv[1]).read_text(encoding='utf-8'))
    if problem is None:
        return 0

    print(f'INVALID COMMIT MESSAGE\n\n  {problem}\n', file=sys.stderr)
    print(
        'See .agent-specs/process/agent-protocol.md section 8.',
        file=sys.stderr,
    )
    return 1


if __name__ == '__main__':
    sys.exit(main())
