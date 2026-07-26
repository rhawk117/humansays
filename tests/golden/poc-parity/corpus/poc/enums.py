"""Enumerations.

``SignalName`` is the identity of a rule: the member name is the stable rule id
used in reports and configuration, the member value is the human-readable
indicator printed next to a target.
"""

from enum import StrEnum


class Severity(StrEnum):
    WARNING = "warning"
    ADVISORY = "advisory"


class FailOn(StrEnum):
    NEVER = "never"
    WARNING = "warning"
    ANY = "any"


class OutputFormat(StrEnum):
    TEXT = "text"
    JSON = "json"


class Grade(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class SignalName(StrEnum):
    PY001 = "many-arguments"
    PY002 = "boolean-modes"
    PY003 = "deep-nesting"
    PY004 = "shared-mutable-state"
    PY005 = "broad-exception"
    PY006 = "multiple-mutation-owners"
    PY007 = "mixed-boundaries"
    PY008 = "low-class-cohesion"
    PY009 = "long-function"
    PY010 = "comments"
    PY011 = "docstring"
    PY012 = "many-class-attributes"
    PY013 = "attribute-prefix-cluster"
    PY014 = "validated-argument-bundle"
    PY015 = "static-method"
    PY016 = "lambda-expression"
    PY017 = "long-file"
    PY018 = "many-base-classes"
    PY019 = "many-branches"
    PY020 = "future-annotations"
    PY021 = "lazy-import"
    PY022 = "dense-function"
