"""Value factories.

Functions that derive data used as model defaults. Kept out of ``const`` so
that module stays literal data, and out of ``models`` so the dataclasses there
can reference these as ``default_factory`` without a cycle.
"""

import inspect
from collections import defaultdict
from collections.abc import Iterable

from .const import (
    MUTABLE_COLLECTION_TYPES,
    MUTABLE_METHOD_PAIRS,
    NON_MUTATING_METHOD_DIFFERENCES,
)


def qualified_type_name(subject: type) -> str:
    if subject.__module__ == "builtins":
        return subject.__name__
    return f"{subject.__module__}.{subject.__name__}"


def public_callables(subject: type) -> frozenset[str]:
    return frozenset(
        name
        for name, member in inspect.getmembers(subject)
        if not name.startswith("_") and callable(member)
    )


def mutable_constructors(
    types: Iterable[type] = MUTABLE_COLLECTION_TYPES,
) -> frozenset[str]:
    return frozenset(qualified_type_name(subject) for subject in types)


def mutating_methods(
    pairs: Iterable[tuple[type, type]] = MUTABLE_METHOD_PAIRS,
) -> frozenset[str]:
    names: set[str] = set()
    for mutable_type, immutable_type in pairs:
        difference = public_callables(mutable_type) - public_callables(immutable_type)
        names.update(difference - NON_MUTATING_METHOD_DIFFERENCES)
    return frozenset(names)


def string_set_map() -> dict[str, set[str]]:
    return defaultdict(set)


def incident_map() -> dict:
    return defaultdict(list)
