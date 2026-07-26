# Proof-of-concept baseline

All figures measured against `pysignals` 0.3.0: its own source (14 modules,
2,215 lines) and Django 5.1.4 (879 files, 155,128 lines), single core.

**These are measurements. Do not re-derive them from assumptions. If you believe
one is wrong, re-run it and report the delta.**

## Startup

| Item | Time |
|---|---|
| `import pysignals` | 242 ms |
| `pydantic_settings` | 204 ms |
| `pydantic` (nested in the above) | 87 ms |
| `rich` | 20 ms |
| `argparse` | 10 ms |
| `tokenize` | 9 ms |

74% of a self-scan was spent before a byte of source was read.

## Analysis

| Item | Time |
|---|---|
| Self-scan, 2,215 lines | 85 ms |
| `ast.parse` share | ~20 ms (25%) |
| `ast.parse` with `type_comments=True` | 28 ms (+40%, no consumer) |
| Django, all 22 rules | 4.18 s |
| Django, minus `PY010`+`PY011` — **Phase 1's actual deletion set** | 3.24 s (−22.5%) |
| Django, minus `PY016` only | 3.66 s (−12.7%) |
| Django, minus `PY010`+`PY011`+`PY016` | 2.82 s (−32.5%) |
| Ruff `check --select E,F`, same tree, 1 core | 0.238 s |

Approximately 15x slower than Ruff single-threaded, doing more semantic work per
node.

## Django output distribution

| Rule | Firings | Share |
|---|---:|---:|
| `PY011` docstring | 3,858 | 37.3% |
| `PY010` comments | 2,427 | 23.5% |
| `PY001` many-arguments | 702 | 6.8% |
| `PY004` shared-mutable-state | 593 | 5.7% |
| `PY002` boolean-modes | 518 | 5.0% |
| `PY009` long-function | 350 | 3.4% |
| ... | | |
| `PY007` mixed-boundaries | **2** | 0.0% |
| **Total** | **10,330** | |

Score: 60.5, grade C. Deleting `PY010` and `PY011` removed 60.8% of output
volume and **22.5%** of scan time with no score change.

**Correction.** An earlier draft claimed 26% and cited 3.22 s. Both were wrong.
The 26% mixed two measurement runs (5.05 s from the instrumented harness against
4.60 s from a clean run), and 3.22 s belongs to a set including `PY016`, which
Phase 1 does not delete. Figures above are best-of-3 on one machine.

`PY020` (future-annotations) fires **zero times** on Django and contributes no
measurable delta. It is deleted for correctness — no identified compatibility or
introspection hazard — not for speed.

Absolute wall-clock drifts 4.18–5.05 s run to run on this hardware. Report
percentages, not absolutes, and always state the baseline they are against.

## Calibration gap

| Rule | Firings | At threshold edge | Criteria doc says |
|---|---:|---:|---|
| `PY001` | 702 | 406 at exactly 4 args (58%) | 4 args = "inspect whether values form a concept" |
| `PY009` | 350 | 224 in the 50–79 band (64%) | "roughly 30–50 lines" is a question, not a verdict |

## The specification disagreement

A file containing only the criteria document's §9 **preferred** examples scored
**28.4, grade F**. The tool emitted identical findings for the preferred and the
discouraged form.

Cause: `build_signature` flattened `posonlyargs + args + kwonlyargs + vararg +
kwarg` into one tuple, discarding argument kind — the distinction the criteria
document says matters most.

## Profile hot spots

| Item | Cumulative (profiler-inflated) |
|---|---|
| `_lambda_signals` (full extra `ast.walk`, 804k calls) | 2.37 s |
| `_comment_lines` (full `tokenize` pass per file) | 1.56 s |

37% of analysis time in three rules being deleted or demoted.

## Verified mechanisms

| Mechanism | Status |
|---|---|
| CPython audit events fire for real I/O | verified |
| `WeakSet` instance-growth tracking | verified |
| `gc.DEBUG_SAVEALL` cycle attribution to project types | verified |
| `sys.monitoring` has `BRANCH`, `EXCEPTION_HANDLED`, `PY_UNWIND` | verified, 3.12+ |
| Code objects expose `co_posonlyargcount` / `co_kwonlyargcount` | verified |
| Bytecode loses comments entirely | verified |
| Bytecode transitive effect propagation (`shutil.copy` → `open`) | verified in prototype |
| PyPI name `humansays` available; `pysignals` taken | verified |
