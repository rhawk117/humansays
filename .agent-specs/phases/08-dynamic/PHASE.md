# Phase 6 — calibration and observation

**Goal.** Add runtime evidence without breaking determinism or the scan budget.

**Read this file and `.agent-specs/design/04-execution-modes.md`.**

---

## Two distinct things

**Calibration** produces an artifact that sharpens static analysis. Its output is
data, not findings.

**Observation** produces findings that have no static counterpart. Its output is
nondeterministic and never contributes to any aggregate.

Do not merge these. They have different lifecycles, different outputs and
different trust properties.

---

## Task 1 — calibration artifact

```
humansays calibrate --run "pytest"
```

Installs a `sys.addaudithook` hook plus `sys.monitoring` instrumentation, runs
the project's test suite, records what happened.

### Instrumentation boundary — settle this before writing code

Instrumentation installed in the `humansays` process does **not** propagate to
processes it launches. `pytest` is typically a separate process; `pytest-xdist`
spawns workers; application code spawns subprocesses and `multiprocessing`
children.

| Mechanism | Covers | Cost |
|---|---|---|
| Generated `sitecustomize.py` on `PYTHONPATH` | every child interpreter | global to the run; needs cleanup |
| `pytest` plugin via `-p` | pytest and xdist workers | test-runner specific |
| Interpreter wrapper | direct children only | misses `multiprocessing` spawn |

Recommended: generated `sitecustomize` plus an explicit propagation policy that
**records which child processes were instrumented and which were not**, and
reports uninstrumented children in the artifact rather than silently omitting
their effects.

- [ ] Bootstrap mechanism chosen and documented
- [ ] Subprocess propagation policy stated
- [ ] Artifact records instrumented and uninstrumented process counts
- [ ] A test under `pytest-xdist -n 2` confirms worker coverage

Until this is settled, the feasibility rating for calibration is optimistic.

### Artifact fingerprint (required, complete)

```json
{
  "source_tree_hash": "...",
  "dependency_lock_hash": "...",
  "python_version": "3.12.3",
  "platform": "linux-x86_64",
  "test_command_hash": "...",
  "humansays_version": "...",
  "fact_schema_version": 2,
  "sanitization_version": 1,
  "coverage": 0.71
}
```

**`generated_at` is not in the fingerprint.** The artifact is content-addressed;
a timestamp inside the digest means identical observations produce different
addresses. Descriptive metadata lives in a sibling block excluded from the hash:

```json
{"content_digest": "sha256:...",
 "metadata": {"generated_at": "...", "duration_s": 41.2, "host": "..."}}
```

### Storage policy

Default is a **local content-addressed cache**, not a committed file. A runtime
artifact can carry absolute paths, module structure, test-only behavior,
exception types, call-site coverage, execution counts, environment-specific
branches, private package names and test-data characteristics.

| Context | Policy |
|---|---|
| Local | Content-addressed cache under `.humansays/cache/` |
| CI, pull request | Build artifact, not committed |
| Committed baseline | Opt-in, sanitized, `sanitization_version` recorded |

Sanitization strips absolute paths, normalizes to repo-relative, and drops
test-data-derived values.

### Staleness

Fingerprint mismatch produces a **warning and non-use**, never silent use.
`humansays calibrate --check` reports staleness without running.

### Determinism

The artifact digest enters the canonical JSON `inputs` block. Static output is
byte-equivalent given source, config, version **and artifact digest** — the last
term is not optional. Without it the determinism claim is false, because static
analysis reads the artifact when present.

---

## Task 2 — observation

```
humansays observe --run "pytest"
```

Build order by value:

1. **Per-call-site coverage partitioning** — feeds `HS-SHAPE-05`. If call site A
   never reaches lines 40–70 and site B never reaches 12–38, the function is two
   functions with two audiences. Strongest available evidence for
   `HS-FIND-01`.
2. **`HS-NARRATION-12` branch-never-taken** — dead defensive structure with
   execution counts.
3. **`HS-ARGS-05` identity-stable parameters** — a parameter holding the same
   object across all calls is a dependency, not an input. Directly implements
   criteria §3 with proof.
4. **`HS-FAIL-11` / `HS-FAIL-12`** — observed handler behavior.
5. **`HS-LEAK-*`** — separate subsystem, needs `gc` and `tracemalloc`.

Items 1–4 fall out of one `sys.monitoring` instrumentation pass.

### Required provenance on every observed finding

```json
{
  "evidence_source": "observed",
  "run_id": "...",
  "coverage": 0.71,
  "executions": 12000,
  "call_sites_covered": "4/60"
}
```

`call_sites_covered` is not optional. "Never taken in 12,000 executions" without
it invites deleting a guard that only fires in production.

### Platform

`sys.monitoring` is 3.12+. Python 3.11 gets a `sys.setprofile` fallback with
worse overhead, or observe mode is scoped to 3.12+ and documented.

Instrument only functions already carrying static signals. Bounds overhead and
scopes output to things already worth reporting.

---

## Acceptance criteria

- [ ] Artifact carries the complete fingerprint; a test asserts every field
- [ ] Fingerprint mismatch warns and does not use the artifact
- [ ] Canonical JSON `inputs` block includes the artifact digest
- [ ] Default storage is the local cache; committing requires an explicit flag
- [ ] Sanitization is tested against a fixture containing absolute paths
- [ ] No observed finding contributes to any printed aggregate; a test asserts
- [ ] Every observed finding carries full provenance including
      `call_sites_covered`
- [ ] Scan-path wall-clock unchanged when no artifact is present

---

## What a wrong implementation looks like

1. **`.humansays/observed.json` committed by default.** Leaks environment
   detail, churns on merge, goes stale silently.
2. **Stale artifact used with a warning.** Warn *and refuse*.
3. **Observed findings enter a total.** Flaky test changes the output.
4. **`branch-never-taken` reported without call-site coverage.** Someone deletes
   a production-only guard.
5. **Calibration and observation share one command.** Different lifecycles.
