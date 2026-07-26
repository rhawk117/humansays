# Phase 7 — performance

**Goal.** Exhaust pure-Python headroom. Then decide about Rust on evidence.

**Read this file and `.agent-specs/design/05-rust.md`.**

---

## What the measurements say

Rust is an optimization, not a rescue.

| Fact | Value |
|---|---|
| Analyzer versus Ruff, one core, same tree | ~15x slower |
| Startup share of a self-scan, before dependency removal | 74% |
| `ast.parse` share of scan time | ~25% |

The dominant cost was one dependency, not the analyzer.

---

## Order

1. **Measure first.** Re-run the baseline harness. Do not optimize from the
   figures in this document; they predate several phases.
2. **Single-traversal extraction.** The proof of concept walked the tree twice
   and tokenized once more. Two of the three passes belonged to deleted rules;
   confirm what remains.
3. **Evaluate only enabled rules.** Profile selection should prune work, not
   filter output.
4. **`ProcessPoolExecutor` over files.** File analysis has zero cross-file state.
   Deterministic ordering must be preserved by sorting results, not by relying
   on completion order.
5. **Content-hash cache.** Only after the fact schema has been stable for two
   releases.

---

## Rust decision

### Do not build

A PyO3 node-level extension. The hot path is `ast.walk` and node dispatch, so
the FFI boundary would land on the highest-frequency call site in the program.
You would cross it constantly or move extraction wholesale — which is a rewrite
with extra steps.

### First candidate, if any

**The dependency summarizer from Phase 5 Layer 3.** Batch rather than per-node,
comment-agnostic, embarrassingly parallel, purely CPU-bound, output is a cache
so failure means slow rather than wrong, and it is the slowest component users
wait on. Self-contained enough to be a genuine learning project without risking
the product.

### Endgame

A standalone binary shipped inside a thin wheel — the Ruff and uv model, not a
PyO3 module. That is also the only real answer to "a 3.11 process cannot parse
3.14 syntax," which is unsolvable in pure Python.

### Trigger criteria — all must hold

- [ ] Findings stable and unchanged for two releases
- [ ] Fact schema unchanged for two releases
- [ ] Golden corpus of ≥500 files with canonical fact output on disk as
      language-agnostic JSON
- [ ] Cross-runtime syntax fixtures for 3.11–3.14
- [ ] Items 1–5 above exhausted and measured

Latency is deliberately not on this list. You cannot reimplement a specification
that is still moving; the fixtures are the specification.

### Independent decision

Analyzing Rust code does not require being written in Rust. `syn` and
tree-sitter both have Python bindings. Do not conflate the two.

---

## Acceptance criteria

- [ ] Baseline re-measured and recorded before any change
- [ ] Each optimization has a before/after measurement in the commit message
- [ ] Parallel analysis produces byte-identical canonical JSON to serial
- [ ] No optimization changes any finding

---

## What a wrong implementation looks like

1. **Parallelism changed output ordering.** Determinism broken for speed.
2. **A cache was added before the schema froze.** Stale facts, silently.
3. **Rust started because the tool felt slow,** without the trigger criteria.
4. **PyO3 extension built.** See "do not build."
