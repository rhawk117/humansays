"""Enumerations.

``SignalName`` is the identity of a rule: the member name is the stable rule id
used in reports and configuration, the member value is the human-readable
indicator printed next to a target.
"""

from enum import StrEnum


class Severity(StrEnum):
    WARNING = 'warning'
    ADVISORY = 'advisory'


class Disposition(StrEnum):
    """Whether a rule scores, and whether it is shown.

    Distinct from ``Severity``, which says how much a finding scores once it
    scores at all. A rule that is not ``ON`` contributes no penalty, so a file
    can print findings and still score 100.
    """

    ON = 'on'
    HINT = 'hint'
    EVIDENCE = 'evidence'
    OFF = 'off'


class FailOn(StrEnum):
    NEVER = 'never'
    WARNING = 'warning'
    ANY = 'any'


class OutputFormat(StrEnum):
    TEXT = 'text'
    JSON = 'json'


class Grade(StrEnum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    F = 'F'


class SignalName(StrEnum):
    HS001 = 'many-arguments'
    HS002 = 'boolean-modes'
    HS003 = 'deep-nesting'
    HS004 = 'shared-mutable-state'
    HS005 = 'broad-exception'
    HS006 = 'multiple-mutation-owners'
    HS007 = 'mixed-boundaries'
    HS008 = 'low-class-cohesion'
    HS009 = 'long-function'
    HS012 = 'many-class-attributes'
    HS013 = 'attribute-prefix-cluster'
    HS014 = 'validated-argument-bundle'
    HS015 = 'static-method'
    HS016 = 'lambda-expression'
    HS017 = 'long-file'
    HS018 = 'many-base-classes'
    HS019 = 'many-branches'
    HS021 = 'lazy-import'
    HS022 = 'dense-function'
