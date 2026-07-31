# Where Rust fits, and when

## Rust is an optimization, not a rescue

Measured: the analyzer is ~15x slower than Ruff on one core while doing more
semantic work per node. The dominant cost was startup — one dependency, 204 ms —
not analysis.

Pure-Python headroom, in order: zero dependencies, single-traversal extraction,
evaluate only enabled rules, process pool over files, content-hash cache. On
eight cores that plausibly lands Django near 0.7–0.9 s, within 4x of Ruff, from
Python.

## Do not build a PyO3 node-level extension

The hot path is `ast.walk` and node dispatch. A PyO3 boundary would land on the
highest-frequency call site in the program. You would cross it constantly, or
move extraction wholesale into Rust — which is not a split, it is a rewrite with
extra steps.

## First candidate: the dependency summarizer

The dependency summarizer, not the AST analyzer:

- Batch, not per-node — one crossing per package
- Comment-agnostic, so source-versus-bytecode parity is easy
- Embarrassingly parallel, purely CPU-bound
- Output is a cache, so failure means slow, not wrong
- The slowest component in the design and the one users wait on
- Self-contained enough to be a genuine learning project without risking the
  product

## Endgame

A standalone binary shipped inside a thin wheel — the Ruff and uv distribution
model, not a PyO3 module. That is also the only real answer to "a 3.11 process
cannot parse 3.14 syntax," which is unsolvable in pure Python.

## Trigger criteria

All must hold. Latency is deliberately absent.

- [ ] Findings stable and unchanged for two releases
- [ ] Fact schema unchanged for two releases
- [ ] Golden corpus of at least 500 files with canonical fact output as
      parser-independent, language-pack-specific JSON
- [ ] Cross-runtime syntax fixtures for 3.11–3.14
- [ ] Pure-Python optimizations exhausted and measured

You cannot reimplement a specification that is still moving. The fixtures are
the specification.

## Analyzing Rust is a separate decision

Analyzing Rust code does not require being written in Rust. `syn` and
tree-sitter both have Python bindings. Do not conflate the two decisions.

What cross-language support actually requires is the contract in
[`06-cross-language.md`](06-cross-language.md), not a language choice.
