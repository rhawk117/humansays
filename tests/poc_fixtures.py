"""Source fixtures.

Every snippet the tests analyze lives here, named for the rule it exercises, so
a test reads as "analyze this fixture, expect this signal" and a fixture can be
reused by more than one test. ``SMELLY_MODULE`` is also written to disk by the
CLI tests, which need a real path to feed through stdin.
"""

from pathlib import Path

FIXTURE_MODULE_PATH = Path(__file__).resolve().parent / 'fixture_module.py'

STATIC_METHOD = """
class Router:
    @staticmethod
    def classify(name):
        return name
"""

CLASSMETHOD_AND_FUNCTION = """
class Router:
    @classmethod
    def build(cls):
        return cls()


def classify(name):
    return name
"""

LAMBDAS_IN_THREE_SCOPES = """
KEY = lambda item: item


def sort_items(items):
    return sorted(items, key=lambda item: item.line)


class Holder:
    def pick(self, items):
        return max(items, key=lambda item: item.score)
"""

NAMED_FUNCTION = """
def key(item):
    return item.line
"""

MULTIPLE_INHERITANCE = """
class Reader:
    pass


class Writer:
    pass


class Store(Reader, Writer):
    pass
"""

SINGLE_INHERITANCE = """
class Reader:
    pass


class Store(Reader):
    pass
"""

FUTURE_ANNOTATIONS = """
from __future__ import annotations

VALUE = 1
"""

FUTURE_OTHER_FEATURE = """
from __future__ import generator_stop

VALUE = 1
"""

LAZY_IMPORT = """
def render(payload):
    import json
    from pathlib import Path

    return json.dumps(payload), Path(".")
"""

MODULE_LEVEL_IMPORT = """
import json


def render(payload):
    return json.dumps(payload)
"""

NESTED_LOOPS = """
def walk(value):
    for a in value:
        for b in a:
            for c in b:
                for d in c:
                    return d
"""

NESTED_LOOPS_IN_METHOD = """
class Walker:
    def walk(self, value):
        for a in value:
            for b in a:
                for c in b:
                    for d in c:
                        return d
"""

NESTED_LOOPS_IN_METHOD_DEEPER = """
class Walker:
    def walk(self, value):
        for a in value:
            for b in a:
                for c in b:
                    for d in c:
                        for e in d:
                            return e
"""


def branch_chain(count: int) -> str:
    """A function with ``count`` if/elif branches."""
    body = ''.join(
        f'    {"if" if index == 0 else "elif"} value == {index}:\n'
        f'        return {index}\n'
        for index in range(count)
    )
    return f'def route(value):\n{body}'


def line_padding(count: int) -> str:
    """A module of ``count`` trivial assignments."""
    return ''.join(f'VALUE_{index} = {index}\n' for index in range(count))


def padded_function(statements: int, blanks: int) -> str:
    """A function with ``statements`` real lines and ``blanks`` blank lines."""
    body = ''.join(f'    value_{index} = {index}\n' for index in range(statements))
    return f'def build():\n{body}{chr(10) * blanks}    return 0\n'


SMELLY_MODULE = '''"""Deliberately smelly fixture module.

Every construct here exists to trip a specific rule. Do not clean it up.
"""

from __future__ import annotations

REGISTRY = {}

SORT_KEY = lambda entry: entry["line"]


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

        if mode == "a":
            return 1
        elif mode == "b":
            return 2
        elif mode == "c":
            return 3
        elif mode == "d":
            return 4
        elif mode == "e":
            return 5
        elif mode == "f":
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
'''

CONFIG_TOML = """
[report]
min_score = 99.5
fail_on = "never"

[thresholds.functions]
max_branches = 2

[thresholds.modules]
max_lines = 10
"""
