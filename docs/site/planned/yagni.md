# YAGNI rules

YAGNI rules observe abstraction whose capability is unused in the source as
written: a class that holds no state, a base class that varies only constants,
a helper whose parameters never differ between call sites.

These rules describe the snapshot in front of them. None of them infers future
need, and none of them claims the abstraction is wrong — an interface with one
implementation today may have three next quarter. The domain ships unweighted
for that reason.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

Background reading:
[Martin Fowler on Yagni](https://martinfowler.com/bliki/Yagni.html) and
[Speculative Generality](https://refactoring.guru/smells/speculative-generality).

| ID       | Rule                                    | Default | Concern  |
| -------- | --------------------------------------- | ------- | -------- |
| YAGNI001 | Zero state namespace                    | hint    | advisory |
| YAGNI002 | Stateless single method                 | hint    | advisory |
| YAGNI003 | Ceremonial abstraction                  | hint    | advisory |
| YAGNI004 | Abc as interface                        | hint    | advisory |
| YAGNI005 | Stateless method declared on a class    | hint    | advisory |
| YAGNI006 | Inheritance used only for configuration | hint    | advisory |
| YAGNI007 | Over parameterized helper               | off     | advisory |

## Rule details

### YAGNI001 Zero state namespace { #YAGNI001 }

Claim
:   design

Detection
:   No state, ≤2 stateless methods

Message
:   `{class}` has no state and `{method_count}` stateless methods. Should these be module-level functions?

### YAGNI002 Stateless single method { #YAGNI002 }

Claim
:   design

Detection
:   Class wrapping exactly one stateless method

Message
:   `{class}` wraps one stateless method and adds no state, lifecycle, or polymorphic contract. Should the method stand alone?

### YAGNI003 Ceremonial abstraction { #YAGNI003 }

Claim
:   design

Detection
:   cg + shp

Message
:   `{abstraction}` adds indirection with no observed state, variation, lifecycle, or reused behavior. Is the indirection carrying anything?

### YAGNI004 Abc as interface { #YAGNI004 }

Claim
:   design

Detection
:   ABC has no state, concrete behavior, construction invariant, registration behavior or lifecycle hooks

Message
:   `Repository` is an ABC containing only abstract methods. Should the contract be structural?

### YAGNI005 Stateless method declared on a class { #YAGNI005 }

Claim
:   design

Detection
:   A static method does not use class identity and has no observed class-specific contract.

Message
:   `{class}.{method}` uses neither instance nor class state. Should it live at module scope?

### YAGNI006 Inheritance used only for configuration { #YAGNI006 }

Claim
:   design

Detection
:   Subclasses vary only class constants or declarative fields and add no behavior.

Message
:   `{subclass_count}` subclasses of `{base}` vary configuration values and add no behavior. Should the configuration be data?

### YAGNI007 Over parameterized helper { #YAGNI007 }

Claim
:   design

Detection
:   Helper taking parameters never varied across call sites

Message
:   Helper `{helper}` accepts `{parameters}`, and every call site supplies the same values. Should the parameters be dropped?
