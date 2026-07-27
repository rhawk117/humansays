# ENCAP rules

ENCAP rules are planned. None of them is implemented today, and nothing on this
page is available to run.

The ENCAP domain covers rules for managing state ownership, enforcing invariants, and ensuring representable state spaces remain manageable. These rules prevent shared mutable state, incomplete initialization, and state-space explosion from unconstrained field combinations.

The principle underneath the domain is encapsulation: mutable data should have
one owner, and reads and writes should pass through that owner rather than
reaching the binding directly. Martin Fowler's refactoring catalog entry
[Encapsulate Variable](https://refactoring.com/catalog/encapsulateVariable.html)
describes the mechanics, and
[Encapsulate Collection](https://refactoring.com/catalog/encapsulateCollection.html)
covers the aliasing case that several rules below concern themselves with.

| ID       | Rule                                    | Default | Concern |
| -------- | --------------------------------------- | ------- | ------- |
| ENCAP001 | Excessive representable state space     | on      | hazard  |
| ENCAP002 | Module global read                      | on      | hazard  |
| ENCAP003 | Module global write                     | on      | hazard  |
| ENCAP004 | Mutable class attribute                 | on      | hazard  |
| ENCAP005 | Leaked internal mutable                 | on      | hazard  |
| ENCAP006 | Shared mutable binding                  | on      | hazard  |
| ENCAP008 | Aliased collection store                | on      | hazard  |
| ENCAP009 | Partial init                            | on      | review  |
| ENCAP010 | Invariant bypass                        | on      | hazard  |
| ENCAP011 | Missing state owner                     | on      | review  |
| ENCAP012 | Unprotected invariant                   | on      | hazard  |
| ENCAP013 | Global declaration                      | on      | hazard  |
| ENCAP014 | Boolean state-space explosion           | on      | hazard  |
| ENCAP015 | Nullable state-space explosion          | on      | hazard  |
| ENCAP016 | Mutually dependent nullability          | on      | hazard  |
| ENCAP017 | Duplicated state representation         | on      | hazard  |
| ENCAP018 | Optional argument state product         | on      | hazard  |
| ENCAP019 | State transition without explicit model | on      | hazard  |
| ENCAP020 | Invariant spread across methods         | on      | hazard  |

## Rule detail

### ENCAP001 Excessive representable state space

**Claim.** risk

**Detection/default.** own + cf + shp

**Message template.** `{type}` permits `{representable_states}` structural states although its guards and transitions recognize only `{meaningful_states}` meaningful combinations.

### ENCAP002 Module global read

**Claim.** risk

**Detection/default.** Read of a mutable module-level binding

**Message template.** `{symbol}` reads mutable module binding `{name}`, making its behavior depend on ambient process state.

### ENCAP003 Module global write

**Claim.** risk

**Detection/default.** Write to a module-level binding

**Message template.** `{symbol}` writes module binding `{name}`, giving the function process-wide mutation authority.

### ENCAP004 Mutable class attribute

**Claim.** risk

**Detection/default.** Class-body `dict`/`list`/`set` literal, incl. `ClassVar[...]`

**Message template.** `{class}.{field}` is one mutable object shared by every instance of the class.

### ENCAP005 Leaked internal mutable

**Claim.** risk

**Detection/default.** `return self._x` where `_x` is a mutable collection

**Message template.** `{symbol}` returns internal mutable `{field}` directly, allowing callers to mutate owned state without the object's contract.

### ENCAP006 Shared mutable binding

**Claim.** risk

**Detection/default.** Module-level mutable bound and mutated from ≥2 scopes

**Message template.** Mutable module binding `{name}` is written from `{scope_count}` scopes, leaving no single owner for its transitions.

### ENCAP008 Aliased collection store

**Claim.** risk

**Detection/default.** Stores a parameter collection without copying

**Message template.** `{class}` stores caller-owned collection `{parameter}` directly, so later caller mutation can change internal state.

### ENCAP009 Partial init

**Claim.** design

**Detection/default.** Field assigned `None` in `__init__`, set elsewhere

**Message template.** `{class}.{field}` begins as `None` and is established later, so instances exist in a partially initialized state.

### ENCAP010 Invariant bypass

**Claim.** risk

**Detection/default.** Public attribute duplicating a validated private field

**Message template.** `{class}.{public_field}` can bypass validation enforced by `{private_field}`.

### ENCAP011 Missing state owner

**Claim.** design

**Detection/default.** own + shp

**Message template.** `{state}` is mutated from `{owners}` without one explicit lifecycle owner.

### ENCAP012 Unprotected invariant

**Claim.** risk

**Detection/default.** own + cf

**Message template.** `{invariant}` can be bypassed through `{paths}`, so valid state is not protected by one construction or transition boundary.

### ENCAP013 Global declaration

**Claim.** risk

**Detection/default.** Use of the `global` statement

**Message template.** `global client` gives this function write access to process-wide state with no explicit owner.

### ENCAP014 Boolean state-space explosion

**Claim.** risk

**Detection/default.** At least three related Boolean fields represent one lifecycle or responsibility

**Message template.** `{class}` has `{dimension_count}` related Boolean fields, allowing `{representable_states}` possible states although only `{meaningful_states}` appear meaningful.

### ENCAP015 Nullable state-space explosion

**Claim.** risk

**Detection/default.** At least three related nullable fields participate in one lifecycle

**Message template.** `{class}` has `{dimension_count}` related nullable fields, allowing `{representable_states}` presence states before lifecycle constraints are applied.

### ENCAP016 Mutually dependent nullability

**Claim.** risk

**Detection/default.** Validity of one nullable field depends on another field's presence or absence

**Message template.** `{fields}` permit `{representable_states}` presence combinations although the observed guards accept only `{valid_states}`.

### ENCAP017 Duplicated state representation

**Claim.** risk

**Detection/default.** The same state is represented by an enum or status field plus Boolean or nullable fields

**Message template.** `{class}` duplicates lifecycle state across `{fields}`, permitting `{representable_states}` combinations that can disagree.

### ENCAP018 Optional argument state product

**Claim.** risk

**Detection/default.** At least three optional parameters have constrained valid combinations

**Message template.** `{symbol}` permits `{representable_states}` optional-argument combinations although only `{valid_states}` appear valid.

### ENCAP019 State transition without explicit model

**Claim.** risk

**Detection/default.** The same state field is assigned several domain values from unrelated public methods with repeated guards.

**Message template.** `{class}.{field}` changes through `{transition_count}` ad hoc assignments and repeated guards instead of one explicit transition model.

### ENCAP020 Invariant spread across methods

**Claim.** risk

**Detection/default.** Related field constraints are checked and repaired in several methods rather than one boundary.

**Message template.** `{invariant}` is enforced across `{method_count}` methods, so no single path establishes or protects valid state.
