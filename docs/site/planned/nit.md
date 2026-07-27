# NIT rules

NIT rules are deliberately opinionated reviewer hints that surface design patterns worth examining. They are unweighted by default.

These rules are planned. None of them is available in a release yet.

The naming and layout conventions this domain leans on are set out in
[PEP 8, the style guide for Python code](https://peps.python.org/pep-0008/).

| ID | Rule | Default | Concern |
|---|---|---|---|
| NIT001 | Frozen candidate | hint | advisory |
| NIT002 | Zero state namespace | hint | advisory |
| NIT003 | Stateless single method | hint | advisory |
| NIT004 | Explicit deletion | hint | review |
| NIT005 | Exception as control flow | hint | advisory |
| NIT006 | Handler over broad observed | hint | advisory |
| NIT007 | Sectioning comment | hint | advisory |
| NIT008 | Restating comment | hint | advisory |
| NIT009 | Comment density high | hint | advisory |
| NIT010 | Docstring restates signature | hint | advisory |
| NIT011 | Todo marker | hint | advisory |
| NIT012 | Placeholder implementation | hint | advisory |
| NIT013 | Ceremonial abstraction | hint | advisory |
| NIT014 | Compensating commentary | hint | advisory |
| NIT015 | Application contract typed as object | hint | advisory |
| NIT016 | Direct environ index | hint | advisory |
| NIT017 | Cached singleton factory | hint | advisory |
| NIT018 | Missing dataclass slots | hint | advisory |
| NIT019 | Nested context managers | hint | advisory |
| NIT020 | Abc as interface | hint | advisory |
| NIT021 | Name mangled member | hint | advisory |
| NIT022 | Stateless method declared on a class | hint | advisory |
| NIT023 | Named behavior expressed as lambda | hint | advisory |
| NIT024 | Inheritance used only for configuration | hint | advisory |

## Rule details

### NIT001 Frozen candidate

- **Claim:** design
- **Detection/default:** No writes after construction, not frozen
- **Message template:** `{class}` has no observed post-construction writes, making mutability an unused capability.

### NIT002 Zero state namespace

- **Claim:** design
- **Detection/default:** No state, ≤2 stateless methods
- **Message template:** `{class}` has no state and only `{method_count}` stateless methods, so the class may be a namespace rather than an object.

### NIT003 Stateless single method

- **Claim:** design
- **Detection/default:** Class wrapping exactly one stateless method
- **Message template:** `{class}` wraps one stateless method and adds no state, lifecycle, or polymorphic contract.

### NIT004 Explicit deletion

- **Claim:** design
- **Detection/default:** Any `del` statement targeting a name, attribute, item or slice
- **Message template:** `del {target}` changes state or object shape explicitly; review whether an owned transition or replacement value would make the lifecycle clearer.

### NIT005 Exception as control flow

- **Claim:** design
- **Detection/default:** Raise/catch pair inside the same function
- **Message template:** This exception appears to select an expected branch; review whether an explicit condition would communicate the normal control flow more clearly.

### NIT006 Handler over broad observed

- **Claim:** risk
- **Detection/default:** Handler caught only one concrete type across N executions
- **Message template:** This handler catches `{declared_type}`, while `{execution_count}` observed executions produced only `{observed_types}`; review whether the broader boundary is intentional.

### NIT007 Sectioning comment

- **Claim:** design
- **Detection/default:** Comment acting as a step header inside a body
- **Message template:** Comment `{comment}` sections a function at a point where responsibility may change; review whether the boundary should be executable.

### NIT008 Restating comment

- **Claim:** design
- **Detection/default:** Comment tokens substantially overlap the statement below
- **Message template:** Comment `{comment}` substantially repeats the following statement and adds little explanatory context.

### NIT009 Comment density high

- **Claim:** design
- **Detection/default:** Comment-to-code ratio above threshold within one function
- **Message template:** `{symbol}` has a comment-to-code ratio of `{ratio}`; density is evidence only.

### NIT010 Docstring restates signature

- **Claim:** design
- **Detection/default:** Docstring naming only parameters and types
- **Message template:** The docstring for `{symbol}` restates parameter names and types without describing behavior or constraints.

### NIT011 Todo marker

- **Claim:** design
- **Detection/default:** `TODO`, `FIXME`, `XXX`, `HACK`
- **Message template:** `{scope}` contains `{count}` TODO/FIXME/HACK markers; density is project-health evidence only.

### NIT012 Placeholder implementation

- **Claim:** risk
- **Detection/default:** `pass`, `...`, `NotImplementedError` in non-abstract context
- **Message template:** `{symbol}` contains placeholder implementation `{placeholder}` outside an abstract or stub context.

### NIT013 Ceremonial abstraction

- **Claim:** design
- **Detection/default:** cg + shp
- **Message template:** `{abstraction}` adds indirection without observed state, variation, lifecycle, or reused behavior.

### NIT014 Compensating commentary

- **Claim:** design
- **Detection/default:** nam + (shp or cf)
- **Message template:** `{symbol}` uses `{comment_count}` comments to mark responsibility changes that also appear in control-flow and shape evidence.

### NIT015 Application contract typed as object

- **Claim:** design
- **Detection/default:** `object` used as an application-level parameter, return, variable, attribute or generic annotation
- **Message template:** `value` is annotated as `object`, which communicates no useful application-level type contract.

### NIT016 Direct environ index

- **Claim:** design
- **Detection/default:** `os.environ[...]` outside tests or the configured configuration boundary
- **Message template:** `DATABASE_URL` is read directly inside application logic instead of entering through the configuration boundary.

### NIT017 Cached singleton factory

- **Claim:** design
- **Detection/default:** Zero-argument cached function returns one process-lifetime object
- **Message template:** `{factory}` is a cached zero-argument factory whose mutable result behaves as a process singleton.

### NIT018 Missing dataclass slots

- **Claim:** design
- **Detection/default:** Closed-shape value dataclass does not use `slots=True`
- **Message template:** `Coordinate` has a fixed field set but retains a dynamic instance dictionary without an observed use.

### NIT019 Nested context managers

- **Claim:** design
- **Detection/default:** A `with` statement directly contains another compatible `with` statement
- **Message template:** These context managers can share one `with` statement without changing their lifetime or exception scope.

### NIT020 Abc as interface

- **Claim:** design
- **Detection/default:** ABC has no state, concrete behavior, construction invariant, registration behavior or lifecycle hooks
- **Message template:** `Repository` is an ABC containing only abstract methods, so structural typing could express the contract without inheritance.

### NIT021 Name mangled member

- **Claim:** design
- **Detection/default:** Class declares a non-dunder member with two leading underscores
- **Message template:** `__connect` is name-mangled to `_Service__connect`, preventing ordinary subclass overriding without providing real privacy.

### NIT022 Stateless method declared on a class

- **Claim:** design
- **Detection/default:** A static method does not use class identity and has no observed class-specific contract.
- **Message template:** `{class}.{method}` uses neither instance nor class state; review whether module scope communicates ownership more clearly.

### NIT023 Named behavior expressed as lambda

- **Claim:** design
- **Detection/default:** A non-trivial lambda is assigned, stored, or passed as durable behavior.
- **Message template:** This lambda contains `{operation_count}` operations and durable behavior; a named function may communicate its contract more clearly.

### NIT024 Inheritance used only for configuration

- **Claim:** design
- **Detection/default:** Subclasses vary only class constants or declarative fields and add no behavior.
- **Message template:** `{subclass_count}` subclasses of `{base}` vary configuration values without adding behavior, making inheritance a configuration mechanism.
