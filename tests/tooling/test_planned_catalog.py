"""The planned catalog is markdown, so its accounting has to be checked as text.

`docs/site/planned/` documents 175 designed-but-unshipped rules. Nothing in
`src/` knows those identifiers exist, so no import can confirm the catalog is
whole. These read the pages and `migration.md` and assert the two agree: every
rule that ever had an identifier still has exactly one, and the retired domain
prefixes are gone everywhere except the two pages that record history.
"""

from __future__ import annotations

import re
from pathlib import Path

PLANNED = Path(__file__).resolve().parents[2] / 'docs' / 'site' / 'planned'

DOMAIN_TOTALS = {
    'SOLID': 28,
    'ENCAP': 19,
    'SMELL': 18,
    'LIFE': 17,
    'SBD': 16,
    'ERR': 15,
    'CONC': 12,
    'CONTRACT': 9,
    'IDIOM': 9,
    'CQS': 7,
    'KISS': 7,
    'YAGNI': 7,
    'POLA': 5,
    'DRY': 3,
    'LOD': 3,
}

BASELINE_TOTAL = 158
NEW_RULES = {
    'SOLID024',
    'SOLID025',
    'SOLID026',
    'SOLID027',
    'SOLID028',
    'LOD003',
    *(f'SBD{n:03d}' for n in range(1, 12)),
}

RETIRED_PREFIXES = ('SRP', 'COUP', 'STATE', 'FAIL', 'NIT')
HISTORICAL_PAGES = frozenset({'migration.md', 'reconciliation.md'})
PRINCIPLE_TOKENS = ('OCP', 'LSP', 'ISP', 'DIP')

RULE_ID = re.compile(rf'\b(?:{"|".join(DOMAIN_TOTALS)})[0-9]{{3}}\b')
RETIRED_ID = re.compile(rf'\b(?:{"|".join(RETIRED_PREFIXES)})[0-9]{{3}}\b')
MAPPING_ROW = re.compile(
    r'^\|\s*`([A-Z]+[0-9]{3})`\s*\|\s*`([A-Z]+[0-9]{3})`\s*\|[^|]*\|\s*(\w+)\s*\|$'
)


def domain_pages() -> dict[str, Path]:
    return {domain: PLANNED / f'{domain.lower()}.md' for domain in DOMAIN_TOTALS}


def catalog_ids() -> set[str]:
    return {
        rule_id
        for page in domain_pages().values()
        for rule_id in RULE_ID.findall(page.read_text())
    }


def mapping_rows() -> list[tuple[str, str, str]]:
    text = (PLANNED / 'migration.md').read_text()
    return [
        match.groups()  # type: ignore[misc]
        for line in text.splitlines()
        if (match := MAPPING_ROW.match(line))
    ]


def test_every_domain_page_exists() -> None:
    missing = sorted(name for name, page in domain_pages().items() if not page.is_file())

    assert missing == []


def test_each_domain_holds_the_rules_it_is_supposed_to() -> None:
    counts = {
        domain: len(set(RULE_ID.findall(page.read_text())))
        for domain, page in domain_pages().items()
    }

    assert counts == DOMAIN_TOTALS


def test_the_catalog_holds_175_rules() -> None:
    assert len(catalog_ids()) == sum(DOMAIN_TOTALS.values()) == 175


def test_no_rule_is_documented_on_another_domains_page() -> None:
    strays = {
        page.name: sorted(
            rule_id
            for rule_id in set(RULE_ID.findall(page.read_text()))
            if not rule_id.startswith(domain)
        )
        for domain, page in domain_pages().items()
    }

    assert {name: found for name, found in strays.items() if found} == {}


def test_every_old_identifier_appears_once_in_the_mapping() -> None:
    old_ids = [old for old, _, _ in mapping_rows()]

    assert len(old_ids) == len(set(old_ids)) == 93


def test_every_new_identifier_in_the_mapping_is_in_the_catalog() -> None:
    catalog = catalog_ids()
    unresolved = sorted({new for _, new, _ in mapping_rows()} - catalog)

    assert unresolved == []


def test_no_two_old_identifiers_resolve_to_the_same_rule() -> None:
    new_ids = [new for _, new, _ in mapping_rows()]

    assert len(new_ids) == len(set(new_ids))


def test_the_mapping_splits_into_41_migrated_and_52_renamed() -> None:
    changes = [change for _, _, change in mapping_rows()]

    assert changes.count('migrated') == 41
    assert changes.count('renamed') == 52


def test_the_changed_and_unchanged_rules_cover_the_158_baseline() -> None:
    changed = {new for _, new, _ in mapping_rows()}
    unchanged = catalog_ids() - changed - NEW_RULES

    assert len(unchanged) == 65
    assert len(changed) + len(unchanged) == BASELINE_TOTAL


def test_the_new_rules_are_exactly_the_ones_that_were_enumerated() -> None:
    changed = {new for _, new, _ in mapping_rows()}
    unchanged_prefixes = {
        'CQS',
        'KISS',
        'POLA',
        'CONTRACT',
        'LIFE',
        'CONC',
        'IDIOM',
        'DRY',
    }
    added = {
        rule_id
        for rule_id in catalog_ids() - changed
        if not any(rule_id.startswith(prefix) for prefix in unchanged_prefixes)
    }

    assert added == NEW_RULES


def test_the_vacated_numbers_are_not_reused() -> None:
    vacated = {
        'ENCAP007',
        'SMELL002',
        'SMELL003',
        'SMELL013',
        'SMELL020',
        'SMELL022',
        'SMELL024',
    }

    assert catalog_ids() & vacated == set()


def test_no_retired_prefix_survives_outside_the_historical_pages() -> None:
    survivors = {
        page.name: sorted(set(RETIRED_ID.findall(page.read_text())))
        for page in PLANNED.glob('*.md')
        if page.name not in HISTORICAL_PAGES
    }

    assert {name: found for name, found in survivors.items() if found} == {}


def test_no_solid_sub_principle_is_named_anywhere_in_the_catalog() -> None:
    token = re.compile(rf'\b(?:{"|".join(PRINCIPLE_TOKENS)})\b')
    named = {
        page.name: sorted(set(token.findall(page.read_text())))
        for page in PLANNED.glob('*.md')
    }

    assert {name: found for name, found in named.items() if found} == {}
