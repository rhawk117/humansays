# YAGNI rules

YAGNI rules observe abstraction whose capability is unused in the source as
written: a class that holds no state, a base class that varies only constants,
a helper whose parameters never differ between call sites.

These rules describe the snapshot in front of them. None of them infers future
need, and none of them claims the abstraction is wrong — an interface with one
implementation today may have three next quarter. The domain ships unweighted
for that reason.

None of the rules below are implemented yet. They are planned.

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

### YAGNI001 Zero state namespace

**Claim.** design

**Detection/default.** No state, ≤2 stateless methods

**Message template.** `{class}` has no state and `{method_count}` stateless methods. Should these be module-level functions?

### YAGNI002 Stateless single method

**Claim.** design

**Detection/default.** Class wrapping exactly one stateless method

**Message template.** `{class}` wraps one stateless method and adds no state, lifecycle, or polymorphic contract. Should the method stand alone?

### YAGNI003 Ceremonial abstraction

**Claim.** design

**Detection/default.** cg + shp

**Message template.** `{abstraction}` adds indirection with no observed state, variation, lifecycle, or reused behavior. Is the indirection carrying anything?

### YAGNI004 Abc as interface

**Claim.** design

**Detection/default.** ABC has no state, concrete behavior, construction invariant, registration behavior or lifecycle hooks

**Message template.** `Repository` is an ABC containing only abstract methods. Should the contract be structural?

### YAGNI005 Stateless method declared on a class

**Claim.** design

**Detection/default.** A static method does not use class identity and has no observed class-specific contract.

**Message template.** `{class}.{method}` uses neither instance nor class state. Should it live at module scope?

### YAGNI006 Inheritance used only for configuration

**Claim.** design

**Detection/default.** Subclasses vary only class constants or declarative fields and add no behavior.

**Message template.** `{subclass_count}` subclasses of `{base}` vary configuration values and add no behavior. Should the configuration be data?

### YAGNI007 Over parameterized helper

**Claim.** design

**Detection/default.** Helper taking parameters never varied across call sites

**Message template.** Helper `{helper}` accepts `{parameters}`, and every call site supplies the same values. Should the parameters be dropped?
