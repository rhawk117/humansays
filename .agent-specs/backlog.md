# Backlog

A future planning session draws from this list, and only the next piece of work gets planned at a time. The order here carries no meaning: entries are sorted alphabetically so the absence of sequence is structural. Do not read a phase or a dependency chain into them.

- A calibration command that produces a content-addressed artifact with a complete environment fingerprint, excludes timestamps from the digest, and warns and refuses rather than silently using a stale artifact.
- A canonical, parser-independent fact serialization, specific to each language pack, with golden fixtures per Python version so a future reimplementation has an exact specification to satisfy.
- A content-hash scan cache, added only once the fact schema has been stable across two releases.
- A corpus of at least fifty before/after repair pairs drawn from real accepted fixes, collected by an extraction script and committed as data.
- A correctness gate for effect classification that checks recall against fixtures and a bounded manual precision sample, and stops at the earliest layer that passes.
- A microfixture harness that asserts fire and no-fire for each rule against a positive fixture and a matched negative fixture, with a CI check that fails when a rule ships without both.
- A narration-prevalence study using matched human and model context with several generations per task, recorded even when the result is null, that changes no claim or certainty value and never outputs a claim that code was generated.
- A profile inspection command that prints both a profile's selection flags and its emittable rule-ID set.
- A repair-correspondence study that measures, per rule and against the production detectors, how often a rule's findings coincide with accepted before/after repairs.
- A repair-direction harness that is runnable with a passing self-test on synthetic input, kept separate from any study run.
- A rule preferring `object` over `typing.Any` where the stricter checker behavior is wanted; the current catalog flags unsafe use of `Any` and flags uninformative `object` annotations but does not encode this preference.
- A rule treating decorators written as classes with `__call__` as preferable to closure-based decorators, for easier test overrides and simpler lifetime reasoning; opinionated and not currently covered.
- A subprocess-instrumentation policy that records which child processes were and were not instrumented and reports the uninstrumented ones.
- A CI check that fails when a rule page under `docs/site/rules/` does not link a `docs/site/philosophy/` page, or when that page does not link back from its "What enforces this" section. The 19 shipped rules satisfy the pairing today and `CLAUDE.md` rule 9 states it as convention, because nothing verifies it. The 158 planned rules under `docs/site/planned/` have no criteria citation at all: they carried `HS-` source-provenance slugs such as `HS-PURPOSE-10`, and those were dropped when the catalog moved, so each planned rule still needs a philosophy section named for it before it ships.
- An argument-kind model that distinguishes positional, keyword-only, and variadic parameters so operation-input rules separate inputs from configuration rather than counting both.
- An effect-classification vocabulary derived once from CPython audit events, versioned, and documented as incomplete rather than as a full semantic effect system.
- An evidence-gated decision on a Rust component, triggered only by stable findings and schema, a golden fact corpus, and cross-runtime syntax fixtures, with each optimization carrying a before/after measurement.
- An observation mode whose findings carry full provenance, including call-site coverage, and never contribute to any printed aggregate.
- Correlated findings that declare their required-independent dimensions and prove by test that they do not fire when all supporting signals trace to one dimension.
- Dependency summarization over compiled bytecode that never imports third-party code, runs off the scan path, and is cached under a composite environment fingerprint rather than a lockfile hash.
- Frozen extracted facts, enforced by construction and by a test that asserts mutation raises, so rule evaluation cannot alter shared state.
- Import-edge effect classification built on the existing alias table, measured on its own before anything heavier is built.
- Large-repository corpora pinned by revision, carrying output-volume and rule-concentration guards rather than a minimum-score assertion.
- Output that labels any uncalibrated number as uncalibrated.
- Parallel per-file analysis that produces byte-identical canonical output to the serial path, with deterministic ordering restored by sorting results.
- Parse-error strictness: separate analyzed, skipped, and failed counts in the summary, and a strict mode that exits non-zero on any parse or analysis error.
- Path-scoped rule activation that can enable, disable, or reweight rules by path glob.
- Profiles defined as an expected set of emittable rule IDs with a snapshot test, where the selection flags are written afterward and asserted to reproduce the set.
- Rule evaluation that runs only the enabled rules, so profile selection prunes work rather than only filtering output.
- Single-traversal fact extraction that replaces the multiple tree walks of the proof of concept.
- Supporting signals reported as evidence beneath the finding that cites them rather than as separate findings.
