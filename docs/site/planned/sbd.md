# SBD rules

SBD rules cover trust boundaries, unbounded resources, unverified assumptions
about input, and constructs that defeat static auditability.

This is not a security scanner. It does not duplicate `bandit`: a rule belongs
here only when a conventional scanner would stay quiet and the finding still
concerns one of those four things. The admission test that decides membership,
and the list of things this domain deliberately does not do, are published on
this page alongside the rules.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

## Admission test

!!! abstract "Both halves must hold"

    1. `bandit` and `semgrep` community rules would not fire on the code.
    2. The finding concerns a trust boundary, an unbounded resource, an
        unverified assumption about input, or a construct that defeats static
        auditability.

A candidate that fails either half does not belong here, however
security-relevant it looks.

??? info "Non-goals: what this domain leaves to `bandit`"

    No hardcoded-secret detection. No `shell=True`. No weak-crypto
    identification. No `eval`/`exec`/`pickle` pattern matching. No dependency
    CVE checking. No taint tracking. No `assert`-stripping detection. No
    predictable-tempfile detection.

    Each of these is already covered by `bandit`, and duplicating them is the
    failure mode this domain exists to avoid.

## Rules

| ID     | Rule                                                        | Default | Concern |
| ------ | ----------------------------------------------------------- | ------- | ------- |
| SBD001 | Unbounded stream consumption                                | on      | hazard  |
| SBD002 | Exact-read assumption                                       | on      | hazard  |
| SBD003 | Ignored transfer count                                      | on      | hazard  |
| SBD004 | Borrowed stream closed                                      | on      | review  |
| SBD005 | Unbounded decompression                                     | on      | hazard  |
| SBD006 | Unbounded collection growth from external input             | on      | hazard  |
| SBD007 | Catastrophic-backtracking pattern on external input         | on      | hazard  |
| SBD008 | Secret compared without constant-time comparison            | on      | hazard  |
| SBD009 | Secret-named value reaches a log or exception message       | on      | hazard  |
| SBD010 | Internal exception detail crosses an external boundary      | on      | review  |
| SBD011 | Non-cryptographic randomness bound to a secret-named target | on      | hazard  |
| SBD012 | Process hash as identity                                    | on      | hazard  |
| SBD013 | Import path mutation                                        | on      | hazard  |
| SBD014 | Dynamic namespace access                                    | on      | hazard  |
| SBD015 | Module object customization                                 | on      | hazard  |
| SBD016 | Dynamic attribute mutation                                  | on      | hazard  |

## Rule details

### SBD001 Unbounded stream consumption { #SBD001 }

Claim
:   risk

Detection
:   A read call with no size argument on a stream the function did not create and whose length it does not control

Message
:   `{symbol}` reads `{stream}` with no size limit. Should the read be bounded?

### SBD002 Exact-read assumption { #SBD002 }

Claim
:   defect

Detection
:   The result of a sized read is used without comparing its length to the size requested

Message
:   `{symbol}` requests `{size}` bytes from `{stream}` and uses the result without checking how many arrived. Should a short read be handled?

### SBD003 Ignored transfer count { #SBD003 }

Claim
:   defect

Detection
:   The return value of a write or send call is discarded

Message
:   `{symbol}` discards the count returned by `{call}`, so a partial transfer is indistinguishable from a complete one. Should the remainder be sent?

### SBD004 Borrowed stream closed { #SBD004 }

Claim
:   defect

Detection
:   A function closes a stream it received as a parameter rather than one it opened

Message
:   `{symbol}` closes `{stream}`, which it received rather than opened. Should closing stay with the caller that owns it?

### SBD005 Unbounded decompression { #SBD005 }

Claim
:   risk

Detection
:   A decompression call (`zipfile`, `gzip`, `tarfile`, `zlib`) whose output is read or extracted without a size, ratio, or member-count bound

Message
:   `{symbol}` extracts `{archive}` with no size, ratio, or member-count bound. Should the expansion be capped?

### SBD006 Unbounded collection growth from external input { #SBD006 }

Claim
:   risk

Detection
:   A collection accumulated inside a loop over an external source (socket, request body, file handle, subprocess stream) with no length or byte cap on the loop

Message
:   `{symbol}` accumulates `{collection}` from `{source}` with no cap on the loop. Should the input size be bounded?

### SBD007 Catastrophic-backtracking pattern on external input { #SBD007 }

Claim
:   risk

Detection
:   A regex containing nested quantifiers or overlapping alternation applied to a value reaching the function from a parameter or external read. Pattern shape only; no taint tracking

Message
:   `{pattern}` contains nested quantifiers and is applied to `{value}`, which arrives from outside `{symbol}`. Should the pattern be rewritten?

### SBD008 Secret compared without constant-time comparison { #SBD008 }

Claim
:   risk

Detection
:   `==` or `!=` comparing a binding whose name matches the configured secret lexicon (token, secret, password, signature, hmac, key, digest) against another value, without `hmac.compare_digest`

Message
:   `{symbol}` compares `{binding}` with `{operator}`. Should this use a constant-time comparison?

### SBD009 Secret-named value reaches a log or exception message { #SBD009 }

Claim
:   risk

Detection
:   A secret-lexicon binding passed to a logging call, `print`, or an exception constructor

Message
:   `{symbol}` passes `{binding}` to `{sink}`. Should the value be redacted before it is recorded?

### SBD010 Internal exception detail crosses an external boundary { #SBD010 }

Claim
:   risk

Detection
:   `str(exc)`, `repr(exc)`, `exc.args`, or a traceback formatted into a return value or response object at a function that also reaches an external boundary

Message
:   `{symbol}` places `{detail}` into `{response}` and reaches `{boundary}`. Should callers outside the process see the internal detail?

### SBD011 Non-cryptographic randomness bound to a secret-named target { #SBD011 }

Claim
:   risk

Detection
:   A value derived from `random.*` (not `secrets.*`) assigned to a secret-lexicon binding or returned from a function with a secret-lexicon name

Message
:   `{symbol}` derives `{binding}` from `random`. Should this come from `secrets`?

### SBD012 Process hash as identity { #SBD012 }

Claim
:   risk

Detection
:   `hash()` output crosses a process boundary or enters persistent storage

Message
:   `hash(value)` is persisted, and Python hashes may change between processes. Should the identity be stable across runs?

### SBD013 Import path mutation { #SBD013 }

Claim
:   risk

Detection
:   Mutation of `sys.path`, `sys.meta_path`, `sys.path_hooks` or related import machinery

Message
:   `sys.path.insert()` changes process-global import resolution. Should the package structure carry this?

### SBD014 Dynamic namespace access { #SBD014 }

Claim
:   risk

Detection
:   Calls to `locals()` or `globals()`

Message
:   `locals()` exposes implementation-local names as a runtime data contract. Should the names be passed explicitly?

### SBD015 Module object customization { #SBD015 }

Claim
:   risk

Detection
:   Replacement or class mutation of the current module through `sys.modules`

Message
:   This module replaces or mutates its own module object, so runtime behavior differs from its source namespace. Should the indirection be explicit?

### SBD016 Dynamic attribute mutation { #SBD016 }

Claim
:   risk

Detection
:   Dynamic `setattr`, `delattr` or `__dict__.update()` changes object state

Message
:   `setattr(target, name, value)` mutates an attribute whose existence and type are unavailable to static review. Should the attribute be declared?
