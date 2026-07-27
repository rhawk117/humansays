# SMELL rules

SMELL rules are deliberately opinionated reviewer hints that surface design patterns worth examining. They are unweighted by default.

These rules are planned. None of them is available in a release yet.

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

### SMELL001 Frozen candidate

- **Claim:** design
- **Detection/default:** No writes after construction, not frozen
- **Message template:** `{class}` has no observed post-construction writes, making mutability an unused capability.

### SMELL004 Explicit deletion

- **Claim:** design
- **Detection/default:** Any `del` statement targeting a name, attribute, item or slice
- **Message template:** `del {target}` changes state or object shape explicitly; review whether an owned transition or replacement value would make the lifecycle clearer.

### SMELL005 Exception as control flow

- **Claim:** design
- **Detection/default:** Raise/catch pair inside the same function
- **Message template:** This exception appears to select an expected branch; review whether an explicit condition would communicate the normal control flow more clearly.

### SMELL006 Handler over broad observed

- **Claim:** risk
- **Detection/default:** Handler caught only one concrete type across N executions
- **Message template:** This handler catches `{declared_type}`, while `{execution_count}` observed executions produced only `{observed_types}`; review whether the broader boundary is intentional.

### SMELL007 Sectioning comment

- **Claim:** design
- **Detection/default:** Comment acting as a step header inside a body
- **Message template:** Comment `{comment}` sections a function at a point where responsibility may change; review whether the boundary should be executable.

### SMELL008 Restating comment

- **Claim:** design
- **Detection/default:** Comment tokens substantially overlap the statement below
- **Message template:** Comment `{comment}` substantially repeats the following statement and adds little explanatory context.

### SMELL009 Comment density high

- **Claim:** design
- **Detection/default:** Comment-to-code ratio above threshold within one function
- **Message template:** `{symbol}` has a comment-to-code ratio of `{ratio}`; density is evidence only.

### SMELL010 Docstring restates signature

- **Claim:** design
- **Detection/default:** Docstring naming only parameters and types
- **Message template:** The docstring for `{symbol}` restates parameter names and types without describing behavior or constraints.

### SMELL011 Todo marker

- **Claim:** design
- **Detection/default:** `TODO`, `FIXME`, `XXX`, `HACK`
- **Message template:** `{scope}` contains `{count}` TODO/FIXME/HACK markers; density is project-health evidence only.

### SMELL012 Placeholder implementation

- **Claim:** risk
- **Detection/default:** `pass`, `...`, `NotImplementedError` in non-abstract context
- **Message template:** `{symbol}` contains placeholder implementation `{placeholder}` outside an abstract or stub context.

### SMELL014 Compensating commentary

- **Claim:** design
- **Detection/default:** nam + (shp or cf)
- **Message template:** `{symbol}` uses `{comment_count}` comments to mark responsibility changes that also appear in control-flow and shape evidence.

### SMELL015 Application contract typed as object

- **Claim:** design
- **Detection/default:** `object` used as an application-level parameter, return, variable, attribute or generic annotation
- **Message template:** `value` is annotated as `object`, which communicates no useful application-level type contract.

### SMELL016 Direct environ index

- **Claim:** design
- **Detection/default:** `os.environ[...]` outside tests or the configured configuration boundary
- **Message template:** `DATABASE_URL` is read directly inside application logic instead of entering through the configuration boundary.

### SMELL017 Cached singleton factory

- **Claim:** design
- **Detection/default:** Zero-argument cached function returns one process-lifetime object
- **Message template:** `{factory}` is a cached zero-argument factory whose mutable result behaves as a process singleton.

### SMELL018 Missing dataclass slots

- **Claim:** design
- **Detection/default:** Closed-shape value dataclass does not use `slots=True`
- **Message template:** `Coordinate` has a fixed field set but retains a dynamic instance dictionary without an observed use.

### SMELL019 Nested context managers

- **Claim:** design
- **Detection/default:** A `with` statement directly contains another compatible `with` statement
- **Message template:** These context managers can share one `with` statement without changing their lifetime or exception scope.

### SMELL021 Name mangled member

- **Claim:** design
- **Detection/default:** Class declares a non-dunder member with two leading underscores
- **Message template:** `__connect` is name-mangled to `_Service__connect`, preventing ordinary subclass overriding without providing real privacy.

### SMELL023 Named behavior expressed as lambda

- **Claim:** design
- **Detection/default:** A non-trivial lambda is assigned, stored, or passed as durable behavior.
- **Message template:** This lambda contains `{operation_count}` operations and durable behavior; a named function may communicate its contract more clearly.
