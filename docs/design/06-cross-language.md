# Cross-language contract

## A language-neutral fact schema is the wrong abstraction

The two criteria documents demonstrate why. Rust's ownership, `Arc`/`Mutex`,
trait, RAII and unsafe criteria have no Python analogue. Python's hidden-input,
mutable `ClassVar` and monkeypatching criteria have no Rust analogue.

A schema general enough to hold both is `{lines, params, nesting}` — the
threshold-counting layer both documents describe as the least interesting part.

Facts are where language semantics live. `&mut self` versus `self`, `ClassVar`
versus `static mut`, `Drop` versus `__exit__` are not one fact wearing different
names.

## What is shared is one level up

Both criteria documents end with the same ten-category scorecard and the same
final decision rule. That convergence is the real cross-language invariant.

```
humansays/lang/python/     facts, extractors, signals    (owns ast)
humansays/lang/rust/       facts, extractors, signals    (owns tree-sitter or syn)
humansays/review/          categories, correlation, confidence, reporting
humansays/reporting/       renderers
```

A `LanguagePack` provides claimed file extensions, a rule-book manifest, an
extractor, and a signal set. It emits findings carrying a review category and an
evidence dimension. The review layer never learns which language produced a
finding.

## Validate before Rust exists

Write a deliberately minimal second pack — a toy one is sufficient — and assert
the review layer needs zero changes. If it needs changes, the contract is wrong,
and you found out for the price of a stub instead of a full implementation.

## Rule books

Each language ships a machine-readable rule book. Every rule cites the section
of its language's criteria document that it enforces.

Two CI checks follow:

1. No rule may exist without a citation.
2. Report criteria sections with zero rule coverage.

Before this work, six of sixteen Python sections had no representation at all.
That number, not the rule count, is the honest measure of how much of the
document the tool enforces.
