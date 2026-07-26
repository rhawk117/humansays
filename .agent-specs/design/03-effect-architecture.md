# Effect architecture

## The problem

The proof of concept matched method-name patterns against a hardcoded
dictionary. Measured result on Django: `mixed-boundaries` fired **twice in
155,128 lines**.

Django reaches side effects through its own ORM, not through `sqlite3`. Every
real codebase reaches effects through project abstractions. Name patterns cannot
see through them, and no amount of dictionary maintenance fixes that.

## Four layers

### Layer 1 — vocabulary from CPython audit events

PEP 578 audit events are a maintained, versioned enumeration of many observable
runtime operations: `open`, `socket.connect`, `subprocess.Popen`,
`sqlite3.connect`, `os.remove`, `exec`, `compile`, `marshal.loads` and roughly a
hundred more. Verified to fire at the C level.

Map them onto the effect categories once, with a version number.

**Stated precisely, because the earlier draft overclaimed:**

> CPython audit events provide a maintained ground-truth vocabulary for many
> observable runtime operations and should anchor effect classification where
> coverage exists.

They are not a complete semantic effect system. Third-party native extensions
may expose different or no events. In-memory mutation is an effect without being
external I/O. Some events — `compile`, `exec` — are not ordinary outside-world
interaction. An event names an operation, not its architectural meaning.

### Layer 2 — import-edge classification

`import httpx` is statically resolvable and unambiguous. `*.save` is not.
Classify at the import, not the call site.

`collect_aliases` already builds the right table. The consumer is wrong.

There are far fewer effectful *libraries* than effectful *method names*, so a
distribution-keyed registry of roughly 200 entries covers most of the ecosystem
surface.

### Layer 3 — dependency summarization over bytecode

Walk `site-packages`, compile each module (or read the existing `.pyc` via
`marshal`), extract per-symbol name-reference sets, propagate to Layer 1
primitives by fixed point.

Prototype-verified: resolves `shutil.copy` to `open`, `tempfile.mkdtemp` to
`mkdir`, with no dictionary.

**Never import to analyze.** Compile from disk. Importing executes module-level
code, which is disqualifying for untrusted dependencies and which this project
has a rule about.

**Never on the scan path.** Batch, cached, keyed on the composite fingerprint in
[`../phases/07-effects/PHASE.md`](../phases/07-effects/PHASE.md) — not on the
lockfile hash alone.

### Layer 4 — first-party call graph

Resolve `user_repo.save()` by resolving to `UserRepository.save` and propagating,
rather than matching its name. Type annotations are the resolution bridge, and
generated code is unusually well annotated.

Published results for this approach (PyCG, ICSE 2021): ~99.2% precision, ~69.9%
recall, **0.38 s per 1k LoC**. That is ~13x slower than the current analyzer,
about 60 seconds on Django. Cannot live on the scan path.

The precision/recall shape is right: under-report effects rather than invent
them.

## Why bytecode here and only here

| Bytecode wins | Bytecode loses |
|---|---|
| Exception tables (3.11+): exact handler ranges with depth | **Comments are gone** — verified. Kills `HS-NARRATION` |
| Real CFG from jump targets | Version-unstable across 3.10→3.11→3.12; four dialects for 3.11–3.14 |
| Uniform IR for code you did not write | Coarser source spans for some constructs |

Bytecode does **not** give you syscalls. `LOAD_GLOBAL open` is still a name.
Grounding comes from Layer 1 regardless.

**AST is the IR for first-party code; bytecode is the IR for dependency
summarization.** Version instability largely evaporates in the second case
because you compile with the interpreter that runs the analysis.

## Stopping rule

After Layer 2, measure. If `HS-EFFECT-06` fires in the hundreds on Django with a
Django-aware configuration, stop. Layers 3 and 4 may be unnecessary.
