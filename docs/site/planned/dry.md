# DRY rules

These rules detect duplicated knowledge and drift risk. They are experimental and unweighted.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

The refactoring these rules point toward is described in Martin Fowler's
catalog entry [Extract Function](https://refactoring.com/catalog/extractFunction.html).

| ID     | Rule                        | Default | Concern  |
| ------ | --------------------------- | ------- | -------- |
| DRY001 | Uniform try wrapping        | off     | advisory |
| DRY003 | Symmetric boilerplate       | off     | advisory |
| DRY004 | Manual dataclass projection | off     | advisory |

## Rule details

### DRY001 Uniform try wrapping { #DRY001 }

Claim
:   risk

Detection
:   Every method wrapped in an identical broad try/except

Message
:   `{class}` wraps `{count}` methods in the same broad exception structure, duplicating one failure policy.

### DRY003 Symmetric boilerplate { #DRY003 }

Claim
:   design

Detection
:   ≥3 near-identical methods differing only by a literal

Message
:   `{scope}` contains `{count}` near-identical methods whose only observed variation is `{variation}`.

### DRY004 Manual dataclass projection { #DRY004 }

Claim
:   design

Detection
:   Dataclass is rebuilt as a dictionary with unchanged field names and values

Message
:   This dictionary manually copies every `User` field and can drift when the dataclass changes.
