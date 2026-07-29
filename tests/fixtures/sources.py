"""Source snippets the analyzer tests run against.

Each is named for the rule it exercises, so a test reads as "analyze this
snippet, expect this signal". These stay plain module constants rather than
fixtures: they are immutable strings with no setup cost and no per-test state.
"""

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
'''

MULTIPLE_MUTATION_OWNERS = """
REGISTRY = {}


def record(bucket, cache):
    REGISTRY['seen'] = 1
    bucket.append(2)
    cache['key'] = 3
    return bucket
"""

SINGLE_MUTATION_OWNER = """
def record(bucket):
    bucket.append(1)
    bucket.append(2)
    return bucket
"""

MULTIPLE_BOUNDARIES = """
import os
import socket
import subprocess


def sync(path):
    os.stat(path)
    socket.gethostname()
    subprocess.run(['ls'])
"""

SINGLE_BOUNDARY = """
import os


def sync(path):
    os.stat(path)
    os.listdir(path)
"""

VALIDATED_ARGUMENT_BUNDLE = """
def configure(alpha, beta, gamma, delta):
    assert alpha
    if beta is None:
        raise ValueError('beta')
    return alpha, beta, gamma, delta
"""

UNVALIDATED_ARGUMENT_BUNDLE = """
def configure(alpha, beta, gamma, delta):
    return alpha, beta, gamma, delta
"""

WIDE_CLASS_SURFACE = """
class Registry:
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_size = 0
        self.queue_head = None
        self.queue_tail = None
        self.queue_depth = 0
        self.name = ''
"""

NARROW_CLASS_SURFACE = """
class Registry:
    def __init__(self):
        self.name = ''
        self.size = 0
"""

DISCONNECTED_CLASS = """
class Split:
    def __init__(self):
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        self.delta = 0

    def read_left(self):
        return self.alpha + self.beta

    def write_left(self, value):
        self.alpha = value
        self.beta = value

    def read_right(self):
        return self.gamma + self.delta

    def write_right(self, value):
        self.gamma = value
        self.delta = value
"""

COHESIVE_CLASS = """
class Joined:
    def __init__(self):
        self.alpha = 0
        self.beta = 0
        self.gamma = 0

    def read_all(self):
        return self.alpha + self.beta + self.gamma

    def write_left(self, value):
        self.alpha = value
        self.beta = value

    def write_right(self, value):
        self.beta = value
        self.gamma = value

    def total(self):
        return self.alpha * self.gamma
"""

CONFIG_TOML = """
[report]
min_score = 99.5
fail_on = "never"

[thresholds.functions]
max_branches = 2

[thresholds.modules]
max_lines = 10
"""
