# DRY rules

These rules detect duplicated knowledge and drift risk. They are experimental and unweighted.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| DRY001 | Uniform try wrapping | risk | advisory | off | HS-NARRATION-09 | Every method wrapped in an identical broad try/except | `{class}` wraps `{count}` methods in the same broad exception structure, duplicating one failure policy. |
| DRY002 | Over parameterized helper | design | advisory | off | HS-NARRATION-10 | Helper taking parameters never varied across call sites | Helper `{helper}` accepts `{parameters}` even though every call site supplies the same values. |
| DRY003 | Symmetric boilerplate | design | advisory | off | HS-NARRATION-11 | ≥3 near-identical methods differing only by a literal | `{scope}` contains `{count}` near-identical methods whose only observed variation is `{variation}`. |
| DRY004 | Manual dataclass projection | design | advisory | off | HS-SHAPE-12 | Dataclass is rebuilt as a dictionary with unchanged field names and values | This dictionary manually copies every `User` field and can drift when the dataclass changes. |
