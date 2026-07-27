# Execution modes

## Three modes

| Mode | Runs | Cost | Produces |
|---|---|---|---|
| **static** | every scan | milliseconds | findings |
| **calibrate** | opt-in, dev-time | test-suite duration | an artifact that sharpens static analysis |
| **observe** | CI or on demand | test-suite duration | findings with no static counterpart |

## 1. Static

The only mode an agent loop invokes. Reads the calibration artifact when present
and fingerprint-valid.

## 2. Calibrate

```
humansays calibrate --run "pytest"
```

`sys.addaudithook` plus `sys.monitoring`. Output is data, not findings:
resolved effect edges, empirical role profiles, identity-stable parameters,
boolean value distributions, observed exception types per handler, per-call-site
line coverage.

The architectural point: you pay the dynamic cost once, cache the result, and
every subsequent millisecond-scale scan benefits.

### Storage

Default is a **local content-addressed cache**, not a committed file. The
artifact can carry absolute paths, module structure, test-only behavior,
exception types, coverage, execution counts, environment-specific branches,
private package names and test-data characteristics. Committing it by default is
an information-disclosure and merge-churn problem.

| Context | Policy |
|---|---|
| Local | `.humansays/cache/`, content-addressed |
| CI, pull request | Build artifact |
| Committed baseline | Opt-in, sanitized, version recorded |

### Fingerprint

Complete field list in
[the retired dynamic-analysis roadmap](../roadmap-retirement.md). Mismatch
produces a warning **and non-use**. Never silent use.

## 3. Observe

```
humansays observe --run "pytest"
```

Findings that cannot exist statically. Separate output channel. Never
contributes to any printed aggregate.

Every observed finding carries `run_id`, `coverage`, `executions` and
`call_sites_covered`. The last is not optional: "never taken in 12,000
executions" without it invites deleting a guard that only fires in production.

## Determinism

> Given the same source, configuration, tool version **and calibration artifact
> digest**, static output is byte-equivalent canonical JSON.

The fourth term is load-bearing. Static analysis reads the artifact when
present, so source plus config plus version is not a sufficient input set.
Canonical JSON carries an `inputs` block naming every digest that affected the
run.

Observed evidence is nondeterministic by construction and is excluded from every
aggregate.

## Platform

Audit hooks (PEP 578) are 3.8+ and work across the supported range.
`sys.monitoring` (PEP 669) is 3.12+; 3.11 needs a `sys.setprofile` fallback with
worse overhead, or observe mode is scoped to 3.12+ and documented as such.

Instrument only functions already carrying static signals. Bounds overhead and
scopes output to things already worth reporting.
