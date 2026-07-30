"""Message templates and the payloads adapters supply for them.

``RuleDefinition.render`` rejects any payload whose keys are not exactly the
template's placeholders, in both directions. That makes the invariant a
coverage problem rather than a parsing one: if every rule renders at least once
across the fixtures and the parity corpus, then every template's placeholders
were supplied and no adapter passed a value the template ignores.

The reverse direction is the one that needs the strict check. ``str.format``
drops surplus keyword arguments silently, so an adapter that keeps measuring a
value the template stopped using would otherwise never be noticed.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from humansays.analysis.extraction import extract
from humansays.analysis.models import ParsedModule
from humansays.config.models import Thresholds
from humansays.enums import SignalName
from humansays.rules.loading import rule_definitions
from humansays.signals import evaluate
from tests.fixtures import sources

CORPUS = Path(__file__).resolve().parents[1] / 'golden/poc-parity/corpus'

# HS005 has no microfixture under tests/fixtures: it is observed only in the
# self-scan baseline, against humansays' own source. Covered here so the
# invariant does not depend on that.
BROAD_EXCEPT = """
def load(path):
    try:
        return open(path).read()
    except Exception:
        return ''
"""

# Rules gated on size need input larger than any hand-written fixture.
GENERATED = (
    sources.line_padding(600),
    sources.padded_function(30, 30),
    sources.padded_function(70, 0),
    BROAD_EXCEPT,
)


def fixture_sources() -> list[str]:
    named = [
        value
        for name, value in vars(sources).items()
        if not name.startswith('_') and isinstance(value, str)
    ]
    return [*named, *GENERATED]


def analyze(source: str, origin: str) -> list:
    module = ParsedModule(Path(origin), source, ast.parse(source))
    return evaluate(extract(module), Thresholds())


def rendered_signals() -> set[SignalName]:
    fired: set[SignalName] = set()
    for source in fixture_sources():
        fired.update(finding.rule.signal for finding in analyze(source, '<fixture>'))

    for path in sorted(CORPUS.rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        fired.update(finding.rule.signal for finding in analyze(text, str(path)))

    return fired


def test_message_placeholders_match_payloads() -> None:
    """Every rule renders, so every template agrees with its adapter payload."""
    unrendered = sorted(
        signal.name for signal in SignalName if signal not in rendered_signals()
    )
    assert not unrendered, (
        f'these rules never rendered, so their templates are unverified: {unrendered}'
    )


def test_static_rules_declare_no_placeholders() -> None:
    static = {
        signal.name
        for signal, definition in rule_definitions().items()
        if not definition.placeholders
    }
    assert static == {'HS002', 'HS005', 'HS015', 'HS016', 'HS021'}


@pytest.mark.parametrize('signal', list(SignalName))
def test_every_template_renders_from_its_declared_placeholders(
    signal: SignalName,
) -> None:
    definition = rule_definitions()[signal]
    payload = dict.fromkeys(definition.placeholders, 7)
    assert definition.render(payload)
