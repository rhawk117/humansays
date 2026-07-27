# IDIOM rules

Python-specific semantics whose equivalent rules differ by language.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

The conventions behind this domain come from
[PEP 20, the Zen of Python](https://peps.python.org/pep-0020/) and
[PEP 8, the style guide for Python code](https://peps.python.org/pep-0008/).

| ID       | Rule                                    | Default | Concern  |
| -------- | --------------------------------------- | ------- | -------- |
| IDIOM002 | Context variable created in local scope | on      | hazard   |
| IDIOM005 | Module attribute hook                   | on      | hazard   |
| IDIOM007 | Mutable nonlocal closure                | on      | hazard   |
| IDIOM008 | Numeric truthiness collapses absence    | hint    | review   |
| IDIOM010 | Frozen state bypass                     | on      | hazard   |
| IDIOM012 | Stdlib idiom reimplementation           | on      | review   |
| IDIOM013 | Protocol not runtime-checkable          | on      | hazard   |
| IDIOM014 | Custom metaclass                        | on      | hazard   |
| IDIOM016 | Import inside function or method        | hint    | advisory |

## Rule details

### IDIOM002 Context variable created in local scope { #IDIOM002 }

Claim
:   risk

Detection
:   `ContextVar` is created inside a function or closure

Message
:   `ContextVar("request_id")` is created inside a closure, giving each invocation a new variable retained by its contexts.

### IDIOM005 Module attribute hook { #IDIOM005 }

Claim
:   risk

Detection
:   Top-level `__getattr__` or `__dir__`

Message
:   Module-level `__getattr__` makes missing attributes execute dynamic lookup instead of failing normally.

### IDIOM007 Mutable nonlocal closure { #IDIOM007 }

Claim
:   risk

Detection
:   A nested function writes a `nonlocal` binding

Message
:   This returned closure mutates `failures` through `nonlocal`, hiding shared state inside lexical scope.

### IDIOM008 Numeric truthiness collapses absence { #IDIOM008 }

Claim
:   risk

Detection
:   A direct truthiness test is applied to a statically numeric optional value; bool is excluded.

Message
:   `if not {name}` sends both `0` and `None` through this branch; if zero is valid, compare with `None` explicitly.

### IDIOM010 Frozen state bypass { #IDIOM010 }

Claim
:   risk

Detection
:   Explicit `object.__setattr__` or `object.__delattr__`

Message
:   `object.__setattr__` bypasses the frozen object's declared construction and mutation contract.

### IDIOM012 Stdlib idiom reimplementation { #IDIOM012 }

Claim
:   design

Detection
:   Code matches a curated pattern implemented by the standard library

Message
:   This `try` and empty `except FileNotFoundError` reimplements `contextlib.suppress`.

### IDIOM013 Protocol not runtime-checkable { #IDIOM013 }

Claim
:   risk

Detection
:   `Protocol` declaration lacks `@runtime_checkable`

Message
:   Protocol `Repository` declares a program contract but cannot be checked with `isinstance()` at runtime.

### IDIOM014 Custom metaclass { #IDIOM014 }

Claim
:   risk

Detection
:   Application class declares or derives from a custom metaclass

Message
:   `Service` uses a custom metaclass even though no library-level class-construction requirement is evident.

### IDIOM016 Import inside function or method { #IDIOM016 }

Claim
:   design

Detection
:   An import occurs below module scope outside configured optional-dependency or cycle-breaking boundaries.

Message
:   `{symbol}` imports `{module}` lazily, hiding an import dependency and possible first-call cost inside execution.
