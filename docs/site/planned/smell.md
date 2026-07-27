# SMELL rules

SMELL rules are deliberately opinionated reviewer hints that surface design patterns worth examining. They are unweighted by default.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

The naming and layout conventions this domain leans on are set out in
[PEP 8, the style guide for Python code](https://peps.python.org/pep-0008/).

| ID       | Rule                                 | Default | Concern  |
| -------- | ------------------------------------ | ------- | -------- |
| SMELL001 | Frozen candidate                     | hint    | advisory |
| SMELL004 | Explicit deletion                    | hint    | review   |
| SMELL005 | Exception as control flow            | hint    | advisory |
| SMELL006 | Handler over broad observed          | hint    | advisory |
| SMELL007 | Sectioning comment                   | hint    | advisory |
| SMELL008 | Restating comment                    | hint    | advisory |
| SMELL009 | Comment density high                 | hint    | advisory |
| SMELL010 | Docstring restates signature         | hint    | advisory |
| SMELL011 | Todo marker                          | hint    | advisory |
| SMELL012 | Placeholder implementation           | hint    | advisory |
| SMELL014 | Compensating commentary              | hint    | advisory |
| SMELL015 | Application contract typed as object | hint    | advisory |
| SMELL016 | Direct environ index                 | hint    | advisory |
| SMELL017 | Cached singleton factory             | hint    | advisory |
| SMELL018 | Missing dataclass slots              | hint    | advisory |
| SMELL019 | Nested context managers              | hint    | advisory |
| SMELL021 | Name mangled member                  | hint    | advisory |
| SMELL023 | Named behavior expressed as lambda   | hint    | advisory |

## Rule details

### SMELL001 Frozen candidate { #SMELL001 }

Claim
:   design

Detection
:   No writes after construction, not frozen

Message
:   `{class}` has no observed post-construction writes, making mutability an unused capability.

### SMELL004 Explicit deletion { #SMELL004 }

Claim
:   design

Detection
:   Any `del` statement targeting a name, attribute, item or slice

Message
:   `del {target}` changes state or object shape explicitly; review whether an owned transition or replacement value would make the lifecycle clearer.

### SMELL005 Exception as control flow { #SMELL005 }

Claim
:   design

Detection
:   Raise/catch pair inside the same function

Message
:   This exception appears to select an expected branch; review whether an explicit condition would communicate the normal control flow more clearly.

### SMELL006 Handler over broad observed { #SMELL006 }

Claim
:   risk

Detection
:   Handler caught only one concrete type across N executions

Message
:   This handler catches `{declared_type}`, while `{execution_count}` observed executions produced only `{observed_types}`; review whether the broader boundary is intentional.

### SMELL007 Sectioning comment { #SMELL007 }

Claim
:   design

Detection
:   Comment acting as a step header inside a body

Message
:   Comment `{comment}` sections a function at a point where responsibility may change; review whether the boundary should be executable.

### SMELL008 Restating comment { #SMELL008 }

Claim
:   design

Detection
:   Comment tokens substantially overlap the statement below

Message
:   Comment `{comment}` substantially repeats the following statement and adds little explanatory context.

### SMELL009 Comment density high { #SMELL009 }

Claim
:   design

Detection
:   Comment-to-code ratio above threshold within one function

Message
:   `{symbol}` has a comment-to-code ratio of `{ratio}`; density is evidence only.

### SMELL010 Docstring restates signature { #SMELL010 }

Claim
:   design

Detection
:   Docstring naming only parameters and types

Message
:   The docstring for `{symbol}` restates parameter names and types without describing behavior or constraints.

### SMELL011 Todo marker { #SMELL011 }

Claim
:   design

Detection
:   `TODO`, `FIXME`, `XXX`, `HACK`

Message
:   `{scope}` contains `{count}` TODO/FIXME/HACK markers; density is project-health evidence only.

### SMELL012 Placeholder implementation { #SMELL012 }

Claim
:   risk

Detection
:   `pass`, `...`, `NotImplementedError` in non-abstract context

Message
:   `{symbol}` contains placeholder implementation `{placeholder}` outside an abstract or stub context.

### SMELL014 Compensating commentary { #SMELL014 }

Claim
:   design

Detection
:   nam + (shp or cf)

Message
:   `{symbol}` uses `{comment_count}` comments to mark responsibility changes that also appear in control-flow and shape evidence.

### SMELL015 Application contract typed as object { #SMELL015 }

Claim
:   design

Detection
:   `object` used as an application-level parameter, return, variable, attribute or generic annotation

Message
:   `value` is annotated as `object`, which communicates no useful application-level type contract.

### SMELL016 Direct environ index { #SMELL016 }

Claim
:   design

Detection
:   `os.environ[...]` outside tests or the configured configuration boundary

Message
:   `DATABASE_URL` is read directly inside application logic instead of entering through the configuration boundary.

### SMELL017 Cached singleton factory { #SMELL017 }

Claim
:   design

Detection
:   Zero-argument cached function returns one process-lifetime object

Message
:   `{factory}` is a cached zero-argument factory whose mutable result behaves as a process singleton.

### SMELL018 Missing dataclass slots { #SMELL018 }

Claim
:   design

Detection
:   Closed-shape value dataclass does not use `slots=True`

Message
:   `Coordinate` has a fixed field set but retains a dynamic instance dictionary without an observed use.

### SMELL019 Nested context managers { #SMELL019 }

Claim
:   design

Detection
:   A `with` statement directly contains another compatible `with` statement

Message
:   These context managers can share one `with` statement without changing their lifetime or exception scope.

### SMELL021 Name mangled member { #SMELL021 }

Claim
:   design

Detection
:   Class declares a non-dunder member with two leading underscores

Message
:   `__connect` is name-mangled to `_Service__connect`, preventing ordinary subclass overriding without providing real privacy.

### SMELL023 Named behavior expressed as lambda { #SMELL023 }

Claim
:   design

Detection
:   A non-trivial lambda is assigned, stored, or passed as durable behavior.

Message
:   This lambda contains `{operation_count}` operations and durable behavior; a named function may communicate its contract more clearly.
