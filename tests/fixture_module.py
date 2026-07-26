"""Deliberately smelly fixture module.

Every construct here exists to trip a specific rule. Do not clean it up.
"""

from __future__ import annotations

REGISTRY = {}

SORT_KEY = lambda entry: entry['line']


class Reader:
    pass


class Writer:
    pass


class Store(Reader, Writer):
    """Two parents: PY018."""

    @staticmethod
    def normalize(name):
        """Static method: PY015."""
        return name.strip()

    def dispatch(self, mode, target, payload, retries, verbose=False):
        """Many arguments, a boolean mode, and a wall of branches."""
        import json

        if mode == 'a':
            return 1
        elif mode == 'b':
            return 2
        elif mode == 'c':
            return 3
        elif mode == 'd':
            return 4
        elif mode == 'e':
            return 5
        elif mode == 'f':
            return 6
        if verbose:
            return json.dumps(sorted(payload, key=lambda item: item))
        return retries + len(target)

    def walk(self, values):
        for first in values:
            for second in first:
                for third in second:
                    for fourth in third:
                        for fifth in fourth:
                            return fifth
        return None
