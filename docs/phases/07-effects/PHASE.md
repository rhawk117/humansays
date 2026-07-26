# Phase 5 — effect architecture

**Goal.** Make effect classification work on real code. Stop as early as
measurement allows.

**Read this file and `docs/design/03-effect-architecture.md`.**

---

## The problem, measured

The proof of concept classified effects by matching method-name patterns against
a hardcoded dictionary. `PY007 mixed-boundaries` fired **twice in 155,128 lines**
of Django. `PY006 multiple-mutation-owners` fired 47 times. Both are primary
evidence for the flagship findings.

Django reaches side effects through its own ORM, not through `sqlite3`. Every
real codebase reaches effects through project abstractions. Name patterns cannot
see through them.

---

## Four layers, in order, stopping when measurement permits

### Layer 1 — vocabulary from CPython audit events

Do not invent effect categories. Map PEP 578 audit events onto the five
categories once.

**Claim carefully.** Audit events are a maintained ground-truth vocabulary for
many observable runtime operations and should anchor classification where
coverage exists. They are **not** a complete semantic effect system: third-party
native extensions may expose different or no events, in-memory mutation is an
effect without being external I/O, some events (`compile`, `exec`) are not
ordinary outside-world interaction, and an event names an operation rather than
its architectural meaning.

### Layer 2 — import-edge classification

`import httpx` is statically resolvable and unambiguous. `*.save` is not.

`collect_aliases` already builds the alias table. The consumer is wrong, not the
extractor. This layer is small.

**Measure after this layer before continuing.** It may be sufficient.

### Layer 3 — dependency summarization over bytecode

Walk `site-packages`, compile each module to a code object (or read the existing
`.pyc` via `marshal`), extract per-symbol name-reference sets, run a fixed-point
propagation to Layer 1 primitives.

Verified in prototype: resolves `shutil.copy` to `open` and `tempfile.mkdtemp`
to `mkdir` with no dictionary.

**Two hard constraints.**

*Never import to analyze.* Compile from disk or read `.pyc`. Importing executes
module-level code — this project has a rule (`HS-INPUT-07`) explaining exactly
why that is dangerous, and analyzing untrusted dependencies makes it
disqualifying.

*Never on the scan path.* Batch job, seconds for a large environment, cached.

**Cache key is a composite environment fingerprint, not a lockfile hash:**

```json
{
  "lock_hash": "...",
  "python_version": "3.12.3",
  "platform": "linux-x86_64",
  "extras": ["terminal"],
  "wheel_vs_sdist": {"...": "wheel"},
  "analyzer_version": "0.3.0",
  "effect_vocabulary_version": 2,
  "summarizer_schema_version": 1
}
```

A lockfile hash alone is wrong: results also depend on Python version, platform
and environment markers, selected extras, wheel versus sdist, package build,
analyzer version, bytecode dialect, and both schema versions.

### Layer 4 — first-party call graph

Only if measurement demands it. Published results for this approach (PyCG,
ICSE 2021): ~99.2% precision, ~69.9% recall, **0.38 s per 1k LoC** — roughly 13x
slower than the current analyzer, about 60 seconds on Django.

Cannot live on the scan path. `--whole-project` mode with a content-hash cache,
or a separate `humansays graph` step whose output the per-file scan consumes.

---

## Acceptance gate — correctness, not volume

An earlier draft made the gate "fires in the hundreds rather than twice." That
measures output distribution, not correctness: a classifier labelling every ORM
call as every category would pass spectacularly. It is the exact error the
critique log records as rejected idea #7.

Three parts. All must hold.

**Recall — automatable.** Against checked-in effect-positive fixtures covering
each category and each resolution mechanism:

- [ ] at least 90% of known effect edges classified, with the correct category

**Precision — bounded manual labour.**

- [ ] 50 randomly sampled `HS-EFFECT-06` hits on Django reviewed by hand;
      at least 80% judged correct
- [ ] 25 negative controls (functions with one effect category, or none)
      reviewed; at most 10% false-positive rate

Fifty and twenty-five are deliberately small. The point is a bounded honest
number, not a study.

**Volume — smoke test only.** Firing in the hundreds rather than twice shows the
classifier is doing something. It is not an acceptance criterion.

If Layer 2 satisfies recall and precision, **stop.** Layers 3 and 4 are not
required, and stopping early is success.

If Layer 4 is reached and precision still fails, cut the effect-dependent
findings rather than shipping them inert or wrong.

## Then

`HS-EFFECT-*` signals, then the effect-dependent signals deferred from Phase 4,
then `HS-FIND-01`, `HS-FIND-02`, `HS-FIND-08`, `HS-FIND-09`, `HS-FIND-12`,
`HS-FIND-13`.

---

## Acceptance criteria

- [ ] Audit-event mapping checked in with a version number
- [ ] Effect-registry claim in docs and output matches the hedged wording above
- [ ] Layer 2 gate measured and recorded in `docs/evidence/effect-gate.md`
- [ ] No analysis path imports third-party code; a test asserts this
- [ ] Dependency summary cache key is the full composite fingerprint
- [ ] Scan-path wall-clock within an explicit budget: at most 5% regression on
      the Django corpus. "Unchanged" was unrealistic; import-edge
      classification has a real cost

---

## What a wrong implementation looks like

1. **The gate was passed on volume alone.** A classifier labelling everything as
   everything satisfies "fires in the hundreds."
2. **The audit-event list was described as complete.** It is not.
2. **`importlib` was used to resolve dependency symbols.** Executes code.
3. **Cache keyed on the lockfile alone.** Stale results across Python versions
   and platforms, silently.
4. **Layer 4 built without measuring after Layer 2.** 60 seconds of Django scan
   time that may have been unnecessary.
5. **The gate failed and the findings shipped anyway,** firing twice per
   codebase.
