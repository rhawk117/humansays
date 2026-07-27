# DRY rules

These rules detect duplicated knowledge and drift risk. They are experimental and unweighted.

These rules are planned. None of them is available in a release yet.

The refactoring these rules point toward is described in Martin Fowler's
catalog entry [Extract Function](https://refactoring.com/catalog/extractFunction.html).

| ID     | Rule                        | Default | Concern  |
| ------ | --------------------------- | ------- | -------- |
| DRY001 | Uniform try wrapping        | off     | advisory |
| DRY003 | Symmetric boilerplate       | off     | advisory |
| DRY004 | Manual dataclass projection | off     | advisory |

## Rule details

### DRY001 Uniform try wrapping

- **Claim:** risk
- **Detection/default:** Every method wrapped in an identical broad try/except
- **Message template:** `{class}` wraps `{count}` methods in the same broad exception structure, duplicating one failure policy.

### DRY003 Symmetric boilerplate

- **Claim:** design
- **Detection/default:** ≥3 near-identical methods differing only by a literal
- **Message template:** `{scope}` contains `{count}` near-identical methods whose only observed variation is `{variation}`.

### DRY004 Manual dataclass projection

- **Claim:** design
- **Detection/default:** Dataclass is rebuilt as a dictionary with unchanged field names and values
- **Message template:** This dictionary manually copies every `User` field and can drift when the dataclass changes.
