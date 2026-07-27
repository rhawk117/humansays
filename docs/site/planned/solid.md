# SOLID rules

SOLID rules cover how responsibility and dependency are distributed across
types: a unit that accumulates several independent reasons to change, a
conditional that grows a branch every time the domain gains a variant, an
override that narrows what its base promised, or a dependency the signature
never declares.

The group is flat. Every rule carries a `SOLID###` identifier, and `SOLID` is
the only selector token, configuration key, and heading for the group.

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

Background reading:
[Robert C. Martin on the Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html),
[Extract Class](https://refactoring.com/catalog/extractClass.html) in Martin
Fowler's refactoring catalog, and Fowler's
[Reducing Coupling](https://martinfowler.com/ieeeSoftware/coupling.pdf).

| ID       | Rule                                             | Default | Concern  |
| -------- | ------------------------------------------------ | ------- | -------- |
| SOLID001 | Role conflict                                    | on      | review   |
| SOLID002 | Effect in domain type                            | on      | review   |
| SOLID003 | Mixed responsibilities                           | on      | review   |
| SOLID004 | Mixed abstraction levels                         | on      | review   |
| SOLID005 | Low field cohesion                               | on      | review   |
| SOLID006 | God constructor                                  | on      | review   |
| SOLID007 | Unclassifiable unit                              | on      | review   |
| SOLID008 | Incohesive class                                 | on      | review   |
| SOLID009 | Logging mixed with domain mutation               | on      | review   |
| SOLID010 | Configuration object drives unrelated workflows  | on      | review   |
| SOLID011 | Data object used as behavior switchboard         | on      | review   |
| SOLID012 | Boolean mode switch                              | on      | review   |
| SOLID013 | Repeated type or value dispatch                  | on      | review   |
| SOLID014 | Function signature encodes multiple workflows    | on      | review   |
| SOLID015 | Concrete factory return                          | on      | hazard   |
| SOLID016 | Name mangled shadow                              | on      | hazard   |
| SOLID017 | Undeclared dependency                            | on      | hazard   |
| SOLID018 | Env read in logic                                | on      | hazard   |
| SOLID019 | Clock read inline                                | on      | hazard   |
| SOLID020 | Randomness inline                                | on      | hazard   |
| SOLID021 | Settings singleton access                        | on      | review   |
| SOLID022 | Hidden dependency surface                        | on      | hazard   |
| SOLID023 | Untestable without environment                   | on      | hazard   |
| SOLID024 | Scattered variant dispatch                       | hint    | advisory |
| SOLID025 | Unsupported inherited operation                  | hint    | advisory |
| SOLID026 | Disjoint consumer usage                          | hint    | advisory |
| SOLID027 | Policy code constructing concrete infrastructure | hint    | advisory |
| SOLID028 | Substantial method detached from its class       | hint    | advisory |

## Rule details

### SOLID001 Role conflict { #SOLID001 }

Claim
:   design

Detection
:   Decides, performs I/O, and formats output in one body

Message
:   `{symbol}` decides policy, performs `{effects}`, and formats output in one body. Should these live apart?

### SOLID002 Effect in domain type { #SOLID002 }

Claim
:   design

Detection
:   I/O inside a value object, DTO or entity

Message
:   `{type}` is used as a domain value and performs `{effect}`. Should the effect move to a caller?

### SOLID003 Mixed responsibilities { #SOLID003 }

Claim
:   design

Detection
:   own + eff + (shp or cf)

Message
:   `{symbol}` combines `{responsibilities}`, on independent ownership, effect, and control-flow evidence. Should they be separated?

### SOLID004 Mixed abstraction levels { #SOLID004 }

Claim
:   design

Detection
:   Raw I/O construction alongside domain decisions

Message
:   `{symbol}` makes domain decisions and constructs low-level `{effect}` in the same body. Should the layers be separated?

### SOLID005 Low field cohesion { #SOLID005 }

Claim
:   design

Detection
:   Method/field graph splits into ≥2 components

Message
:   `{class}` splits into `{component_count}` disconnected method/field components. Should they be separate types?

### SOLID006 God constructor { #SOLID006 }

Claim
:   design

Detection
:   Constructor assigns > 8 fields

Message
:   `{class}.__init__` establishes `{actual}` fields. Should construction be this broad?

### SOLID007 Unclassifiable unit { #SOLID007 }

Claim
:   design

Detection
:   nam + shp + eff

Message
:   `{symbol}` has no dominant role across its name, data flow, effects, and return behavior. What is it for?

### SOLID008 Incohesive class { #SOLID008 }

Claim
:   design

Detection
:   own + shp

Message
:   `{class}` contains `{component_count}` independent method/field components with little shared state. Should they be separate types?

### SOLID009 Logging mixed with domain mutation { #SOLID009 }

Claim
:   design

Detection
:   A function mutates domain state and also owns log/report formatting policy.

Message
:   `{symbol}` mutates `{state}` and builds `{reporting}` output in one body. Should reporting move out?

### SOLID010 Configuration object drives unrelated workflows { #SOLID010 }

Claim
:   design

Detection
:   A configuration object is read by disjoint method/effect clusters that select separate workflows.

Message
:   `{type}` supplies `{workflow_count}` unrelated workflow clusters. Should each workflow declare what it needs?

### SOLID011 Data object used as behavior switchboard { #SOLID011 }

Claim
:   design

Detection
:   Many branches dispatch behavior from one data object's tag/type fields.

Message
:   `{symbol}` selects `{branch_count}` behaviors from `{object}.{field}`. Should the behavior sit with the data?

### SOLID012 Boolean mode switch { #SOLID012 }

Claim
:   design

Detection
:   Boolean selecting between two behaviors in the body

Message
:   Boolean `{parameter}` selects between `{mode_count}` workflows inside `{symbol}`. Should they be separate entry points?

### SOLID013 Repeated type or value dispatch { #SOLID013 }

Claim
:   design

Detection
:   Conditional chain selects behavior from one type, tag, enum or literal discriminator

Message
:   Eight branches differ only by the callable they select. Should the discriminator map to behavior directly?

### SOLID014 Function signature encodes multiple workflows { #SOLID014 }

Claim
:   design

Detection
:   Disjoint parameter subsets are used on mutually exclusive paths.

Message
:   `{symbol}` has `{workflow_count}` mutually exclusive parameter subsets. Should each workflow have its own signature?

### SOLID015 Concrete factory return { #SOLID015 }

Claim
:   risk

Detection
:   Non-final classmethod constructs `cls(...)` but returns the containing class type

Message
:   `Request.from_bytes()` constructs `cls` but returns `Request`. Should the return type be `Self`?

### SOLID016 Name mangled shadow { #SOLID016 }

Claim
:   risk

Detection
:   Base and subclass declare the same source-level mangled name

Message
:   `Child.__load` and `Base.__load` mangle to different names, so neither overrides the other. Was an override intended?

### SOLID017 Undeclared dependency { #SOLID017 }

Claim
:   risk

Detection
:   Body reaches a name absent from signature and instance state

Message
:   `{symbol}` depends on `{dependency}`, which arrives through neither its signature nor its instance state. Should the dependency be declared?

### SOLID018 Env read in logic { #SOLID018 }

Claim
:   risk

Detection
:   `os.environ`/`getenv` below module level

Message
:   `{symbol}` reads `{variable}` from the environment inside application logic. Should the value be passed in?

### SOLID019 Clock read inline { #SOLID019 }

Claim
:   risk

Detection
:   `datetime.now`, `time.time` in a decision path

Message
:   `{symbol}` reads the clock inside a decision path, so identical explicit inputs can produce different decisions. Should the time be supplied?

### SOLID020 Randomness inline { #SOLID020 }

Claim
:   risk

Detection
:   `random.*`, `uuid4`, `secrets.*` in a decision path

Message
:   `{symbol}` reads randomness inside a decision path with no injection point. Should the source be supplied?

### SOLID021 Settings singleton access { #SOLID021 }

Claim
:   design

Detection
:   Import-time-constructed config accessed deep in logic

Message
:   `{symbol}` reaches the process-wide settings singleton `{name}`. Should configuration be a declared dependency?

### SOLID022 Hidden dependency surface { #SOLID022 }

Claim
:   risk

Detection
:   eff + own

Message
:   `{symbol}` depends on `{dependencies}` through ambient state and effect access rather than its declared contract. Should the contract say so?

### SOLID023 Untestable without environment { #SOLID023 }

Claim
:   risk

Detection
:   eff + own + cg

Message
:   `{unit}` cannot be constructed or exercised without `{environment}`, on independent test, ownership, and effect evidence. Should it be reachable in isolation?

### SOLID024 Scattered variant dispatch { #SOLID024 }

Claim
:   design

Detection
:   The same set of variant values is branched on in more than one method or function

Message
:   `{unit}` branches on `{discriminator}` in `{site_count}` places. Should the variants own their own behavior?

### SOLID025 Unsupported inherited operation { #SOLID025 }

Claim
:   design

Detection
:   An override raises `NotImplementedError` or an equivalent refusal for an operation its base declares as supported

Message
:   `{subclass}.{method}` refuses an operation `{base}` declares as supported. Should the two share a base at all?

### SOLID026 Disjoint consumer usage { #SOLID026 }

Claim
:   design

Detection
:   No consumer of a type uses more than a disjoint subset of its public methods

Message
:   `{type}` has `{consumer_count}` consumers, and no two use overlapping methods. Should the contract be split?

### SOLID027 Policy code constructing concrete infrastructure { #SOLID027 }

Claim
:   design

Detection
:   A unit holding decision logic instantiates a concrete client, connection, session, or engine directly

Message
:   `{unit}` decides `{policy}` and constructs `{infrastructure}` itself. Should the collaborator be supplied by the caller?

### SOLID028 Substantial method detached from its class { #SOLID028 }

Claim
:   design

Detection
:   A method uses neither `self` nor any class attribute, exceeds `min_detached_method_characters` effective characters, and contains at least two executable statements. Effective characters exclude comments, docstrings, and whitespace, so a long docstring cannot trip it

Message
:   `{class}.{method}` is `{characters}` characters and touches no class state. Should it live at module scope?
