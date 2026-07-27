# Arguments and failure

A signature and a failure path are the two places where a function states its
contract to the rest of the program. When a signature grows past the point
where its values have a name, every caller has to reassemble the same grouping
by hand, and changing the grouping means editing every one of them. When a
failure path is left implicit, the same thing happens in reverse: callers guess
at what can go wrong, and each guess becomes a behavior somebody later depends
on. Both make code hard to change for the same reason. The knowledge that
should live in one place, an object or an exception type, is instead spread
across every site that touches the function.

## 9. Function Argument Criteria

Argument counts are review thresholds, not correctness rules.

|  Count | Review interpretation                                   |
| -----: | ------------------------------------------------------- |
| 0 to 3 | Usually clear                                           |
|      4 | Inspect whether values form a concept                   |
| 5 to 6 | Strong design smell                                     |
|     7+ | Usually missing an object or combining responsibilities |

### Evaluate the argument kinds

Distinguish:

- Operation input
- Optional configuration
- Long-lived dependency
- Repeated data group
- Boolean mode switch

### Criteria

- Parameters that form a real concept become a value or request object.
- Long-lived dependencies move to a constructor.
- Optional settings are keyword-only.
- Positional booleans are avoided.
- Parameter objects are not meaningless bags created only to lower the count.
- Several repeated dependencies do not automatically justify one broad service class.

```python
@dataclass(frozen=True, slots=True)
class ScanRequest:
    repository: str
    revision: str
    path: Path
    minimum_severity: Severity
    include_ignored: bool = False
```

```python
def run_scan(request: ScanRequest) -> ScanResult:
    ...
```

For secondary options:

```python
def run_scan(
    target: ScanTarget,
    *,
    minimum_severity: Severity = Severity.MEDIUM,
    include_ignored: bool = False,
) -> ScanResult:
    ...
```

## 12. Failure Criteria

For every branch and external call, determine:

- What can fail?
- What exception or result represents that failure?
- Can state be partially mutated?
- May the caller retry safely?
- Is ordinary absence distinct from infrastructure failure?

### Good criteria

- Expected absence is represented explicitly, such as `User | None`.
- Domain failures use meaningful exceptions or result types.
- Infrastructure errors are not silently converted into unrelated outcomes.
- Broad `except Exception` blocks do not swallow programming errors.
- Multi-step effects have explicit transaction, compensation, or idempotency behavior where required.

## Where these criteria come from

The argument criteria restate long-standing refactoring advice. Martin Fowler's
catalog entries for
[Introduce Parameter Object](https://refactoring.com/catalog/introduceParameterObject.html)
and [Remove Flag Argument](https://refactoring.com/catalog/removeFlagArgument.html)
cover the first and fourth criteria directly. The keyword-only criterion rests
on the syntax added by
[PEP 3102](https://peps.python.org/pep-3102/), which introduced parameters that
can only be supplied by name.

## What enforces this

Four shipped rules detect structures that these criteria describe. Each one
raises a review lead, not a verdict.

| Code  | Signal                      | Criterion it touches                                                   | Page                                                                         |
| ----- | --------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| HS001 | `many-arguments`            | The count thresholds in section 9                                      | [Function shape](../rules/function-shape.md#hs001-many-arguments)            |
| HS002 | `boolean-modes`             | "Positional booleans are avoided"                                      | [Function shape](../rules/function-shape.md#hs002-boolean-modes)             |
| HS014 | `validated-argument-bundle` | "Parameters that form a real concept become a value or request object" | [Function shape](../rules/function-shape.md#hs014-validated-argument-bundle) |
| HS005 | `broad-exception`           | "Broad `except Exception` blocks do not swallow programming errors"    | [Failure and imports](../rules/failure-and-imports.md#hs005-broad-exception) |

The remaining criteria on this page have no shipped rule, and nothing in the
tool checks them:

- Long-lived dependencies moving to a constructor.
- Optional settings being keyword-only.
- Parameter objects not being meaningless bags.
- Repeated dependencies not justifying one broad service class.
- Expected absence being represented explicitly.
- Domain failures using meaningful exceptions or result types.
- Infrastructure errors not being converted into unrelated outcomes.
- Multi-step effects having explicit transaction, compensation, or idempotency behavior.

These are review questions for a human. Several of them turn on intent that is
not present in the syntax tree, so they are stated here as criteria rather than
as anything the scan can observe.
