"""Loading rule definitions from per-group ``rules.toml`` package data.

Definitions are addressed as ``files('humansays.rules').joinpath(group, ...)``
rather than ``files(f'humansays.rules.{group}')``. Traversal into a
subdirectory does not import the subpackage, and the subpackages hold the
detection code that depends on this module -- addressing them by name would
close an import cycle.

The load is lazy and cached rather than a module-level constant, so nothing
reads package data at import time.
"""

import tomllib
from collections.abc import Iterable, Mapping
from functools import cache
from importlib.resources import files
from string import Formatter
from types import MappingProxyType

from humansays.enums import Severity, SignalName
from humansays.findings.models import RuleSpec
from humansays.rules.models import RuleDefinition

GROUPS = (
    'contract',
    'encap',
    'err',
    'idiom',
    'kiss',
    'smell',
    'solid',
    'yagni',
)

# The whole vocabulary of a rule entry. Anything else is rejected, which is what
# keeps detection logic out of the data: a `when`, `threshold` or `min_lines`
# key is a load error, and no RuleDefinition field could hold one anyway.
RULE_KEYS = frozenset({
    'id',
    'severity',
    'confidence',
    'weight',
    'message',
    'review_question',
})


class RuleDefinitionError(Exception):
    """A shipped ``rules.toml`` is malformed."""


def placeholders(template: str, where: str) -> frozenset[str]:
    """The ``{name}`` fields of a message template.

    Only plain identifiers are allowed. Positional fields, attribute and index
    access, conversions and format specs all make the rendered text depend on
    something other than the value an adapter measured.
    """
    names: set[str] = set()
    for _, field, spec, conversion in Formatter().parse(template):
        if field is None:
            continue

        if conversion is not None:
            raise RuleDefinitionError(f'{where}: conversion !{conversion} in message')

        if spec:
            raise RuleDefinitionError(f'{where}: format spec :{spec} in message')

        if not field.isidentifier():
            raise RuleDefinitionError(
                f'{where}: message placeholder must be a plain name, got {field!r}'
            )

        names.add(field)

    return frozenset(names)


def _number(entry: Mapping[str, object], key: str, where: str) -> float:
    value = entry[key]
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise RuleDefinitionError(f'{where}: {key} must be a number, got {value!r}')

    return float(value)


def _text(entry: Mapping[str, object], key: str, where: str) -> str:
    value = entry[key]
    if not isinstance(value, str):
        raise RuleDefinitionError(f'{where}: {key} must be a string, got {value!r}')

    return value


def _signal(entry: Mapping[str, object], where: str) -> SignalName:
    name = _text(entry, 'id', where)
    try:
        return SignalName[name]
    except KeyError:
        raise RuleDefinitionError(f'{where}: {name} is not a SignalName member') from None


def _severity(entry: Mapping[str, object], where: str) -> Severity:
    value = _text(entry, 'severity', where)
    try:
        return Severity(value)
    except ValueError:
        raise RuleDefinitionError(f'{where}: unknown severity {value!r}') from None


def _check_keys(entry: Mapping[str, object], where: str) -> None:
    unknown = sorted(set(entry) - RULE_KEYS)
    if unknown:
        raise RuleDefinitionError(f'{where}: unknown keys {unknown}')

    missing = sorted(RULE_KEYS - set(entry))
    if missing:
        raise RuleDefinitionError(f'{where}: missing keys {missing}')


def build_definition(entry: Mapping[str, object], group: str) -> RuleDefinition:
    where = f'{group}/rules.toml: {entry.get("id", "<no id>")}'
    _check_keys(entry, where)
    signal = _signal(entry, where)
    message = _text(entry, 'message', where)
    try:
        spec = RuleSpec(
            signal=signal,
            severity=_severity(entry, where),
            confidence=_number(entry, 'confidence', where),
            weight=_number(entry, 'weight', where),
            review_question=_text(entry, 'review_question', where),
        )
    except ValueError as error:
        raise RuleDefinitionError(f'{where}: {error}') from None

    return RuleDefinition(spec, message, placeholders(message, where))


def collect_definitions(
    entries: Iterable[Mapping[str, object]],
    group: str,
) -> Mapping[SignalName, RuleDefinition]:
    """One group's entries, keyed by signal, rejecting a repeated id."""
    definitions: dict[SignalName, RuleDefinition] = {}
    for entry in entries:
        definition = build_definition(entry, group)
        signal = definition.spec.signal
        if signal in definitions:
            raise RuleDefinitionError(f'{group}/rules.toml: {signal.name} defined twice')

        definitions[signal] = definition

    return MappingProxyType(definitions)


def read_group(group: str) -> Mapping[SignalName, RuleDefinition]:
    """Every definition in one group's ``rules.toml``, keyed by signal."""
    resource = files('humansays.rules').joinpath(group, 'rules.toml')
    document = tomllib.loads(resource.read_text(encoding='utf-8'))
    return collect_definitions(document.get('rule', ()), group)


def merge_groups(
    by_group: Mapping[str, Mapping[SignalName, RuleDefinition]],
) -> Mapping[SignalName, RuleDefinition]:
    """One map over every group, total over ``SignalName``.

    Raises if a signal is defined in two groups or has no definition at all,
    so a caller never has to ask whether a lookup can miss.
    """
    merged: dict[SignalName, RuleDefinition] = {}
    owners: dict[SignalName, str] = {}
    for group, definitions in by_group.items():
        for signal, definition in definitions.items():
            if signal in merged:
                raise RuleDefinitionError(
                    f'{signal.name} is defined in both {owners[signal]} and {group}'
                )

            merged[signal] = definition
            owners[signal] = group

    undefined = sorted(signal.name for signal in SignalName if signal not in merged)
    if undefined:
        raise RuleDefinitionError(f'no rule definition for {undefined}')

    return MappingProxyType(merged)


@cache
def rule_definitions() -> Mapping[SignalName, RuleDefinition]:
    """Every shipped definition, merged across groups."""
    return merge_groups({group: read_group(group) for group in GROUPS})
