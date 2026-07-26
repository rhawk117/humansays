# Overview

`humansays` is a deterministic structural review engine for Python, optimized for
code written or modified by coding agents.

## The unit of value

Not a rule firing. A correlated finding backed by independent evidence.

```
Facts:      78-line span, 3 mutation owners, 2 effect categories,
            2 broad handlers, 3 method field clusters
Signals:    long function, several mutation owners, mixed boundaries,
            broad exception handling
Finding:    This function likely coordinates several unrelated
            responsibilities and has an unclear partial-failure boundary.
```

## What differentiates it

1. **Correlated findings** — several independent evidence dimensions must agree
   before a design-level claim is made
2. **Agent-actionable output** — exact evidence, constraints, boundaries,
   verification steps
3. **Deterministic local execution** — no model call, no remote service, no
   source upload
4. **Calibrated restraint** — fewer, better-supported findings; accuracy is
   measured, not asserted
5. **Parser independence** — a future backend swap is a substitution, not a
   rewrite

## What it does not claim

Do not state, in documentation or output, that `humansays` is faster than Ruff,
more comprehensive than Pylint, a replacement for type checking or security
scanning, able to prove runtime effects from syntax, an AI reviewer, an objective
definition of clean code, or safe to auto-fix.

The defensible claim:

> `humansays` turns deterministic structural evidence into review findings and
> bounded repair instructions for coding agents.

## Source of the rules

The rules are an attempt to programmatically enforce two authored documents:
*Python Code Design and Review Criteria* and *Rust Code Design and Review
Criteria*. Every rule cites a section. CI reports sections with zero coverage —
that number, not the rule count, measures how much of the document the tool
enforces.

Rules are per-language by design. The two criteria documents demonstrate why:
Rust's ownership, trait, RAII and unsafe criteria have no Python analogue;
Python's hidden-input, `ClassVar` and monkeypatching criteria have no Rust
analogue. See [`06-cross-language.md`](06-cross-language.md).

## Roadmap

| Phase | Goal |
|---|---|
| 1 | Migration — behavior-preserving port |
| 2 | Fact-model correctness — argument kinds, claim/evidence, immutability |
| 3 | Measurement — four corpora, paired repairs, the narration study |
| 4 | MVP rule set — ~30 signals, 6 findings |
| 5 | Effects — four layers, stop when measurement allows |
| 6 | Calibration and observation |
| 7 | Performance, then the Rust decision |
