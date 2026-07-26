# Phase 2 — fact-model correctness

**Goal.** Make the fact model capable of expressing what the criteria document
actually says. No new rules until this lands.

**Read this file and `docs/site/rules/README.md`. Nothing else.**

---

## Preconditions

- [ ] Phase 1 complete; parity fixtures green
- [ ] `analysis/rules.py` carries its contract-debt docstring

---

## Task 1 — the argument-kind split (highest value in the roadmap)

`build_signature` currently flattens `posonlyargs + args + kwonlyargs + vararg +
kwarg` into one tuple. The criteria document states that argument **kinds**
matter more than raw count. The fact model keeps only the count.

Measured consequence: the tool cannot distinguish the criteria document's
*preferred* signature from its *discouraged* one. Both emitted the same two
findings, and a file containing only the document's recommended code scored
28.4 (F).

Replace `Signature.parameters` with:

```python
@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    kind: ParameterKind      # POSITIONAL_ONLY | POSITIONAL_OR_KEYWORD
                             # | KEYWORD_ONLY | VAR_POSITIONAL | VAR_KEYWORD
    has_default: bool
    annotated_bool: bool
```

Operation inputs are positional-only plus positional-or-keyword without
defaults. Keyword-only parameters with defaults are configuration and are
counted separately.

### Acceptance test (write this before implementing)

`tests/criteria/test_preferred_examples.py`, using the criteria document's own
§9 examples verbatim:

- `run_scan_preferred(target, *, minimum_severity=..., include_ignored=False,
  follow_links=False)` emits **nothing**
- `run_scan_discouraged(repository, revision, path, minimum_severity,
  include_ignored, follow_links)` emits `HS-ARGS-01` at `moderate` and
  `HS-ARGS-02`

This test failing is the definition of the bug. This test passing is the
definition of done for Task 1.

---

## Task 2 — claim and evidence attributes

Replace the proof of concept's `WARNING`/`ADVISORY` severity with the two
independent attributes in `.agent-specs/design/02-evaluation-model.md` §1.

- `claim: bug | risk | design`
- `certainty: observed | derived | heuristic`
- `impact: unassigned` — derived in Phase 5, never hand-assigned
- `report: standalone | evidence`

Magnitude does **not** change certainty. Carry magnitude as a numeric field on
the finding; it will feed `impact` once that is measured.

Migrate existing rules per the Claim, Cert and Report columns in
`docs/site/rules/python.md`. `Impact` stays empty — it is derived in Phase 5.
**Do not invent assignments** — if a rule is missing from that table, stop and
ask.

## Task 3 — fact immutability

Extracted facts are frozen after construction. Transformations create derived
views. Rule evaluation cannot mutate shared facts.

The specific existing violation: class-cohesion preparation mutates method
field-use sets while filtering method names out of attribute sets.

## Task 4 — path-scoped rule activation

Config gains the ability to enable, disable or reweight rules by path glob. This
is a prerequisite for `HS-TEST`, which is meaningless outside test files, and
the schema has no notion of it today.

```toml
[[paths]]
match = "tests/**"
include_family = ["HS-TEST"]
exclude_family = ["HS-NARRATION"]
```

## Task 5 — parse-error strictness

- Summary exposes `analyzed`, `skipped`, `failed` counts
- `--strict` exits non-zero on any parse or analysis error
- Canonical JSON distinguishes the three states

## Task 6 — canonical fact serialization

Facts serialize to **parser-independent, language-pack-specific** canonical JSON
containing no parser-native representations.

The distinction matters: a future Rust implementation of the *Python* extractor
must reproduce Python facts exactly. Those facts are not, and should not be,
universal across Python and Rust source. "Language-agnostic" was the wrong word
and contradicted `.agent-specs/design/06-cross-language.md`. Golden fact fixtures are stored under
`tests/golden/facts/` per Python version.

These fixtures are the specification a future reimplementation would satisfy.
They are the single most important artifact this phase produces.

---

## Acceptance criteria

- [ ] `tests/criteria/test_preferred_examples.py` passes
- [ ] No rule carries a severity attribute; all carry claim + certainty + report
- [ ] `impact` exists in the schema and is empty for every rule
- [ ] Every rule in `docs/site/rules/python.md` has matching catalog metadata; a test
      asserts the doc and the catalog agree
- [ ] Facts are frozen; a test asserts mutation raises
- [ ] Golden fact fixtures exist for 3.11–3.14 and contain no `ast` repr strings
- [ ] `--strict` fails on a deliberately malformed fixture
- [ ] Parity fixtures from Phase 1 still pass, with documented exceptions for
      the argument-kind change only

---

## Non-goals

- New rules of any kind
- Correlation or findings
- Effect architecture
- Any dynamic analysis
- Scoring or aggregation

---

## What a wrong implementation looks like

1. **`HS-ARGS-01` still counts keyword-only parameters as operation inputs.**
   The preferred example fires. This is the original bug, unfixed.
2. **Claim assignments were invented** rather than taken from
   `docs/site/rules/python.md`. Check every row.
3. **`bug` was applied generously.** Three rules carry it today —
   `HS-STATE-02`, `HS-CLASS-09`, `HS-FAIL-10`. A fourth requires a cited language
   reference or a reproducible incorrect-behavior fixture, not a judgement call.
4. **Facts are "frozen" by convention** rather than by `frozen=True` plus a test.
5. **Golden fact fixtures contain `<ast.Module object at 0x...>`.** The
   serialization is not canonical.
