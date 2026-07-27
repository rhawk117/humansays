# Testability and thresholds

Testability is the dimension that decides how expensive every later change will
be. Code that can only be exercised by starting the application, setting an
environment variable, or patching a module global has no seam in Michael
Feathers' sense, a place where behavior can be altered without editing the code
at that place, as summarized in Martin Fowler's
[Legacy Seam](https://martinfowler.com/bliki/LegacySeam.html). Without a seam a
reviewer cannot check a rule in isolation, so the only way to find out whether a
change is correct is to run the whole system and watch. That is why the criteria
below and the review thresholds that follow them sit together: the thresholds
describe shapes that quietly remove seams, and
[Self Testing Code](https://martinfowler.com/bliki/SelfTestingCode.html)
describes what a codebase that keeps them looks like from the outside.

## 13. Testability Criteria

Try to sketch a test before approving the design.

Good code usually allows:

```python
repository = InMemoryUserRepository()
identity_provider = FakeIdentityProvider()
clock = FixedClock(...)

use_case = RegisterUser(
    users=repository,
    identities=identity_provider,
    clock=clock,
)

result = use_case.execute(command)
```

### Good criteria

* Tests construct inputs and dependencies directly.
* Tests do not require application startup for domain behavior.
* Each test receives isolated mutable state.
* Pure decisions can be tested without I/O.
* External boundaries can be replaced with small in-memory or fake implementations.
* Protocols are introduced at real boundaries, not for every class.

### Warning signs

* Extensive monkeypatching of module globals.
* Environment variables required for unit tests.
* Tests must clear caches or registries between cases.
* A simple rule requires a real network, database, or filesystem.
* Tests assert implementation call sequences instead of outcomes.

## 14. Review Thresholds

These signals require inspection but do not mandate refactoring.

| Signal                                    | Question to ask                                          |
| ----------------------------------------- | -------------------------------------------------------- |
| Function exceeds roughly 30 to 50 lines   | Is it mixing workflow, decisions, and technical details? |
| More than 3 indentation levels            | Can guard clauses or extraction flatten it?              |
| More than 4 parameters                    | Do some parameters form one concept?                     |
| More than 5 constructor dependencies      | Does the class have multiple responsibilities?           |
| More than 7 to 10 public methods          | Is the public API cohesive?                              |
| Same arguments repeatedly travel together | Is there a missing value object or state owner?          |
| One-line helpers are spread across files  | Has extraction increased navigation cost?                |
| A method mutates multiple owners          | Is the transaction or authority unclear?                 |

Where the shipped defaults differ from the numbers quoted above, the shipped
default is what actually fires. Every key below is documented in
[Configuration](../configuration.md).

* **Roughly 30 to 50 lines.** `thresholds.functions.max_lines` defaults to `50`,
  so HS009 reports at 51 physical lines and never earlier. A second key,
  `thresholds.functions.max_code_lines`, defaults to `65` and drives HS022 over
  the same span with blanks, comments, and the docstring removed.
* **More than 3 indentation levels.** `thresholds.functions.max_nesting`
  defaults to `3`, which matches for a module-level function.
  `thresholds.functions.class_nesting_bonus` defaults to `1`, so a method
  reports only above depth 4.
* **More than 4 parameters.** `thresholds.functions.max_arguments` defaults to
  `3`, so HS001 reports at four operation parameters, one earlier than the
  signal above suggests.
* **More than 5 constructor dependencies.** No shipped key counts constructor
  dependencies. The nearest is `thresholds.classes.max_attributes`, default `6`,
  which counts the whole class state surface and reports at seven attributes.
* **More than 7 to 10 public methods.** No shipped key counts public methods.
* Two shipped defaults have no row in the table above:
  `thresholds.functions.max_branches`, default `5`, and
  `thresholds.modules.max_lines`, default `500`.

## 15. Review Scorecard

Score each category from 0 to 2.

| Category        | 0                      | 1                    | 2                    |
| --------------- | ---------------------- | -------------------- | -------------------- |
| Purpose         | Unclear                | Broad                | One clear job        |
| Inputs          | Mostly hidden          | Mixed                | Explicit             |
| State ownership | Shared or unclear      | Partially controlled | One clear owner      |
| Side effects    | Hidden or scattered    | Visible but mixed    | Explicit boundaries  |
| Invariants      | Unprotected            | Partially enforced   | Enforced by owner    |
| Failures        | Swallowed or ambiguous | Inconsistent         | Explicit semantics   |
| Dependencies    | Global or concrete     | Partially injected   | Explicit and focused |
| Testability     | Requires environment   | Requires patching    | Construct and call   |
| Naming          | Generic                | Understandable       | Domain-specific      |
| Abstraction     | Mixed levels           | Minor mixing         | Consistent level     |

Interpretation:

| Score | Interpretation                                             |
| ----: | ---------------------------------------------------------- |
| 17 to 20 | Strong design                                           |
| 13 to 16 | Generally sound; inspect weak areas                     |
|  9 to 12 | Significant design debt                                 |
|   0 to 8 | Responsibility and state ownership likely require redesign |

The score identifies reasoning difficulty. It must not be used as an automatic refactoring trigger.

## 16. Pull Request Checklist

### Responsibility

* [ ] Each changed function or class has one dominant responsibility.
* [ ] Names communicate domain intent.
* [ ] Related code remains together.
* [ ] Extracted code introduces a real abstraction rather than narration.

### Inputs and state

* [ ] Meaningful dependencies are explicit.
* [ ] Mutable state has one clear owner.
* [ ] Object lifetimes match state lifetimes.
* [ ] Mutable internals are not exposed.
* [ ] Mutable `ClassVar` or module state is deliberately justified.

### Behavior

* [ ] Business rules are owned by the appropriate entity or policy.
* [ ] Workflows coordinate rather than implement every dependency detail.
* [ ] External I/O is isolated behind clear boundaries.
* [ ] Commands and queries are not misleadingly combined.

### Construction and arguments

* [ ] Constructors produce valid objects.
* [ ] Functions with more than four parameters were reviewed for missing concepts.
* [ ] Constructors with more than five dependencies were reviewed for excessive responsibility.
* [ ] Parameter objects represent meaningful concepts.
* [ ] Optional and boolean parameters are keyword-only where useful.

### Failures and tests

* [ ] Failure behavior is explicit.
* [ ] Partial mutation and retry behavior were considered.
* [ ] Tests construct dependencies instead of repairing global state.
* [ ] Important decisions can be tested without external infrastructure.
* [ ] Tests assert behavior and outcomes rather than incidental implementation details.

## Final Decision Rule

When deciding whether to leave code inline, extract a function, or create a class:

1. **Leave it inline** when it is one readable part of a cohesive operation.
2. **Extract a function** when a block forms a named calculation, rule, or lower-level operation without needing persistent state.
3. **Extract a class** when behavior requires owned state, shared configuration, injected dependencies, identity, interchangeable implementations, or resource lifecycle.
4. **Create a boundary abstraction** when external technology should not define the application or domain API.

The final test is:

> Did the change make ownership, intent, and behavior easier to understand without forcing the reader to navigate more code than necessary?

## What enforces this

No shipped rule reads a test suite, and none of them can tell whether a seam
exists. What they mark is source structure that removes one.

For the section 13 warning signs:

| Code | Signal | What it observes | Page |
|---|---|---|---|
| HS004 | `shared-mutable-state` | A mutable object bound at module or class scope, the state a test has to clear between cases | [State and boundaries](../rules/state-and-boundaries.md#hs004-shared-mutable-state) |
| HS007 | `mixed-boundaries` | One function reaches three of the four standard-library boundary categories, so exercising it needs the real filesystem, network, database, or subprocess | [State and boundaries](../rules/state-and-boundaries.md#hs007-mixed-boundaries) |
| HS015 | `static-method` | A method that reaches neither instance nor class state, reachable in a test only through the class | [Class design](../rules/class-design.md#hs015-static-method) |
| HS016 | `lambda-expression` | An expression that cannot be imported, so it cannot be called from a test on its own | [Function shape](../rules/function-shape.md#hs016-lambda-expression) |

For the section 14 thresholds:

| Code | Signal | Threshold row | Page |
|---|---|---|---|
| HS009 | `long-function` | Function exceeds roughly 30 to 50 lines | [Function shape](../rules/function-shape.md#hs009-long-function) |
| HS022 | `dense-function` | The same row, counted with blanks, comments, and the docstring removed | [Function shape](../rules/function-shape.md#hs022-dense-function) |
| HS003 | `deep-nesting` | More than 3 indentation levels | [Function shape](../rules/function-shape.md#hs003-deep-nesting) |
| HS001 | `many-arguments` | More than 4 parameters | [Function shape](../rules/function-shape.md#hs001-many-arguments) |
| HS014 | `validated-argument-bundle` | Same arguments repeatedly travel together, detected as a wide signature whose parameters are validated in the body | [Function shape](../rules/function-shape.md#hs014-validated-argument-bundle) |
| HS012 | `many-class-attributes` | The nearest thing to more than 5 constructor dependencies, counting the class state surface rather than constructor parameters | [Class design](../rules/class-design.md#hs012-many-class-attributes) |
| HS006 | `multiple-mutation-owners` | A method mutates multiple owners | [State and boundaries](../rules/state-and-boundaries.md#hs006-multiple-mutation-owners) |

Three rows of the section 14 table have no shipped rule at all. Nothing counts
public methods, so "more than 7 to 10 public methods" is unenforced; HS008
`low-class-cohesion` measures which attributes the methods touch, not how many
methods there are. Nothing detects one-line helpers spread across files, which
would require reasoning about navigation cost across modules.

Sections 15, 16, and the final decision rule have no shipped rules and are not
candidates for any. A scorecard category, a checklist item, and the choice
between inline code, a function, and a class are all judgements about intent,
and intent is not a syntactic property.
