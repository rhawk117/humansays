# Rules

![The humansays mascot](../assets/human-says-clipart.png){ align=right width="150" }

!!! warning "Early development"

    This is `0.1.0a1`. The `HS###` identifiers on this page are not stable and
    will change before `0.1.0`. Do not pin automation to them yet.

Version `0.1.0a1` ships 19 rules. Every one of them is a structural
observation about Python source, read off the standard-library AST. None of
them executes the code being scanned, and none of them is a verdict.

## What a rule is

A rule is a named condition plus the metadata needed to weigh it. The
metadata is data, not code: each rule group owns a
`src/humansays/rules/<group>/rules.toml`, and each entry there carries seven
keys. Six of them become a `RuleSpec`:

`id`
:   The `HS###` code, which becomes the rule's `signal`. The name printed in
    text output is that signal's readable form, for example `many-arguments`
    — that is what you see on a target line, not the code itself.

`severity`
:   `WARNING` or `ADVISORY`. There are exactly two. There is no error level and
    no bug level.

`disposition`
:   `on`, `hint`, `evidence` or `off`. Severity says how much a finding counts
    once it counts at all; disposition says whether it counts and whether it is
    shown. Only `on` contributes to the score. See
    [Disposition](../output.md#disposition).

`confidence`
:   How reliably the syntactic condition indicates the thing the rule is
    actually about. `HS015` sits at `0.99` because a `staticmethod` decorator
    either is or is not present. `HS009` sits at `0.55` because a long function
    is sometimes just a long function.

`weight`
:   `3.0` for a `WARNING`, `1.0` for an `ADVISORY`. Written out in each
    `rules.toml`. There is no third weight.

`review_question`
:   The question a reviewer should be asking at that location. This is the
    payload of the rule. The tool cannot answer it, which is the point.

The seventh key is `message`: the observation text, written as a template whose
`{placeholders}` are filled with what the rule measured. No key may carry a
condition or a threshold — thresholds are yours to set in `humansays.toml`, and
the loader rejects any key outside those seven.

## How a finding becomes a score

Each **scored** finding contributes a penalty of `weight * confidence`. So one
`HS018` costs `3.0 * 0.78 = 2.34`, and one `HS009` costs `1.0 * 0.55 = 0.55`.

A finding is scored when its rule's disposition is `on`. Three of the 19 are
`hint` — `HS015`, `HS016` and `HS021` — and cost nothing however often they
fire. They are still reported: a hint is a lead for a reviewer, not a defect
the score should punish.

Penalties are summed across the scan, expressed per 100 source lines as a
density, and turned into a score:

```text
density = penalty * 100 / lines
score   = 100 / (1 + density / 7.5)
```

`SCORE_TOLERANCE` is `7.5`, calibrated so roughly one warning per 100 lines
lands in the mid seventies. The curve decays smoothly and never leaves the 0
to 100 range, so a file with no weighted findings scores exactly 100.

Using density rather than a raw count means a large clean module is not
punished for its size, and a small module full of warnings cannot hide behind
a low total. [Output and scoring](../output.md) covers the grade bands and the
JSON shape.

## The 19 shipped rules

| Code  | Signal                      | Severity | Disposition | Confidence | Weight | Page                                            |
| ----- | --------------------------- | -------- | ----------- | ---------- | ------ | ----------------------------------------------- |
| HS001 | `many-arguments`            | WARNING  | `on`        | 0.80       | 3.0    | [Function shape](function-shape.md)             |
| HS002 | `boolean-modes`             | ADVISORY | `on`        | 0.82       | 1.0    | [Function shape](function-shape.md)             |
| HS003 | `deep-nesting`              | WARNING  | `on`        | 0.76       | 3.0    | [Function shape](function-shape.md)             |
| HS004 | `shared-mutable-state`      | WARNING  | `on`        | 0.95       | 3.0    | [State and boundaries](state-and-boundaries.md) |
| HS005 | `broad-exception`           | WARNING  | `on`        | 0.96       | 3.0    | [Failure and imports](failure-and-imports.md)   |
| HS006 | `multiple-mutation-owners`  | WARNING  | `on`        | 0.70       | 3.0    | [State and boundaries](state-and-boundaries.md) |
| HS007 | `mixed-boundaries`          | WARNING  | `on`        | 0.65       | 3.0    | [State and boundaries](state-and-boundaries.md) |
| HS008 | `low-class-cohesion`        | ADVISORY | `on`        | 0.65       | 1.0    | [Class design](class-design.md)                 |
| HS009 | `long-function`             | ADVISORY | `on`        | 0.55       | 1.0    | [Function shape](function-shape.md)             |
| HS012 | `many-class-attributes`     | ADVISORY | `on`        | 0.72       | 1.0    | [Class design](class-design.md)                 |
| HS013 | `attribute-prefix-cluster`  | WARNING  | `on`        | 0.84       | 3.0    | [Class design](class-design.md)                 |
| HS014 | `validated-argument-bundle` | WARNING  | `on`        | 0.88       | 3.0    | [Function shape](function-shape.md)             |
| HS015 | `static-method`             | WARNING  | `hint`      | 0.99       | 3.0    | [Class design](class-design.md)                 |
| HS016 | `lambda-expression`         | WARNING  | `hint`      | 0.99       | 3.0    | [Function shape](function-shape.md)             |
| HS017 | `long-file`                 | WARNING  | `on`        | 0.60       | 3.0    | [State and boundaries](state-and-boundaries.md) |
| HS018 | `many-base-classes`         | WARNING  | `on`        | 0.78       | 3.0    | [Class design](class-design.md)                 |
| HS019 | `many-branches`             | WARNING  | `on`        | 0.74       | 3.0    | [Function shape](function-shape.md)             |
| HS021 | `lazy-import`               | ADVISORY | `hint`      | 0.85       | 1.0    | [Failure and imports](failure-and-imports.md)   |
| HS022 | `dense-function`            | WARNING  | `on`        | 0.72       | 3.0    | [Function shape](function-shape.md)             |

## The gaps at HS010, HS011, and HS020

The numbering runs from `HS001` to `HS022` with three codes missing. Each gap
is a prototype check that was deliberately dropped rather than an
implementation that is still owed:

- `HS010`, comment counting. The raw count was noisy and duplicated evidence
    the narration signals already carried.
- `HS011`, docstring counting. A raw docstring count did not establish a
    structural problem on its own.
- `HS020`, `from __future__ import annotations`. Version-dependent
    modernization belongs to a general linter and loses value on newer Python.

The codes were retired rather than reused, so an `HS###` code means the same
thing across versions. `tests/unit/test_deleted_rules.py` holds the three
in a `DELETED_IDS` set and asserts none of them can be emitted.
[Reconciliation](../planned/reconciliation.md) has the full mapping.

## Why these 19

The shipped set is small on purpose. Every rule here has a condition that can
be read off the syntax tree without guessing, a matched positive and negative
fixture, and a review question worth asking. The much larger catalog of rules
that are designed but not implemented lives under
[Planned rules](../planned/index.md), and nothing in it runs today.

The reasoning behind the rules, as opposed to their mechanics, is in
[Design philosophy](../philosophy/index.md).
