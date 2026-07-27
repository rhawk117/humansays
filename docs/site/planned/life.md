# LIFE rules

!!! warning "Not implemented"

    These rules are designed, not shipped. Nothing on this page runs in
    version `0.1.0a1`, which implements [19 rules](../rules/index.md).

LIFE rules address construction, resource ownership, cleanup, and the implicit temporal dependencies that arise during object initialization and destruction.

The domain rests on the idea that a resource should have an owner whose scope
decides when acquisition and release happen, rather than leaving release to
garbage collection or to whichever branch happens to run.
[PEP 343](https://peps.python.org/pep-0343/) introduced the `with` statement as
Python's mechanism for that, and the
[contextlib documentation](https://docs.python.org/3/library/contextlib.html)
covers the tools built on it.

| ID      | Rule                                     | Default | Concern |
| ------- | ---------------------------------------- | ------- | ------- |
| LIFE001 | Import time side effect                  | on      | hazard  |
| LIFE002 | Constructor does work                    | on      | review  |
| LIFE003 | Post construction setup                  | on      | review  |
| LIFE004 | Traceback retention                      | observe | hazard  |
| LIFE005 | Finalizer dependent release              | observe | hazard  |
| LIFE006 | Unbounded cache                          | observe | hazard  |
| LIFE007 | Temporal coupling                        | on      | review  |
| LIFE008 | Import time resource construction        | on      | hazard  |
| LIFE009 | Import time exit hook                    | on      | hazard  |
| LIFE010 | Application finalizer                    | on      | hazard  |
| LIFE011 | Overridable call during init             | on      | hazard  |
| LIFE012 | Callback during construction             | on      | hazard  |
| LIFE013 | Self escapes before invariant            | on      | hazard  |
| LIFE014 | Constructor is an operation              | on      | hazard  |
| LIFE015 | Construction bypasses invariant path     | on      | hazard  |
| LIFE016 | Dataclass has a behavior-heavy lifecycle | on      | review  |
| LIFE017 | Manual resource management               | on      | hazard  |

## Rule detail

### LIFE001 Import time side effect { #LIFE001 }

Claim
:   risk

Detection
:   Module body performs I/O, network or filesystem work

Message
:   Importing `{module}` performs `{effects}`, giving module loading an operational side effect.

### LIFE002 Constructor does work { #LIFE002 }

Claim
:   design

Detection
:   `__init__` performs I/O or non-trivial computation

Message
:   `{class}.__init__` performs `{effects}`, so constructing the object has operational behavior.

### LIFE003 Post construction setup { #LIFE003 }

Claim
:   design

Detection
:   ≥2 setup-style methods called before first use

Message
:   `{class}` requires `{setup_count}` setup calls before first use, creating an implicit construction sequence.

### LIFE004 Traceback retention { #LIFE004 }

Claim
:   risk

Detection
:   Instance holds an object with `__traceback__`

Message
:   `{instance}` retains an exception traceback and therefore the frames and locals reachable from it.

### LIFE005 Finalizer dependent release { #LIFE005 }

Claim
:   risk

Detection
:   File or socket closed by GC rather than explicitly

Message
:   Resource `{resource}` was closed by garbage collection rather than an explicit owner.

### LIFE006 Unbounded cache { #LIFE006 }

Claim
:   risk

Detection
:   `lru_cache(maxsize=None)` reaching N entries

Message
:   Unbounded cache `{name}` reached `{entries}` entries during observation.

### LIFE007 Temporal coupling { #LIFE007 }

Claim
:   design

Detection
:   cg + nam

Message
:   `{type}` requires the ordered calls `{sequence}` before it becomes usable.

### LIFE008 Import time resource construction { #LIFE008 }

Claim
:   risk

Detection
:   Module-level construction of clients, connections, pools, executors, threads or processes

Message
:   `Client()` is constructed during import, giving it process-wide lifetime without an explicit owner.

### LIFE009 Import time exit hook { #LIFE009 }

Claim
:   risk

Detection
:   `atexit.register()` executed during import

Message
:   Importing this module registers process-global cleanup behavior through `atexit`.

### LIFE010 Application finalizer { #LIFE010 }

Claim
:   risk

Detection
:   Application class defines `__del__`

Message
:   `Connection.__del__` hides resource cleanup behind garbage-collection timing instead of an explicit owner.

### LIFE011 Overridable call during init { #LIFE011 }

Claim
:   risk

Detection
:   Constructor calls an overridable instance method

Message
:   `Base.__init__` calls overridable `configure()` before subclass state is guaranteed to exist.

### LIFE012 Callback during construction { #LIFE012 }

Claim
:   risk

Detection
:   Constructor invokes a caller-provided callback with the object under construction

Message
:   `Service.__init__` passes `self` to a callback before all fields are initialized.

### LIFE013 Self escapes before invariant { #LIFE013 }

Claim
:   risk

Detection
:   `self` is registered, stored, scheduled or passed externally before construction completes

Message
:   `self` escapes to `registry.register()` after only four of seven constructor fields are established.

### LIFE014 Constructor is an operation { #LIFE014 }

Claim
:   risk

Detection
:   own + eff + (cf or shp)

Message
:   Service.__init__ establishes 11 fields, performs two effect categories and contains five branches, so construction has become an operation.

### LIFE015 Construction bypasses invariant path { #LIFE015 }

Claim
:   risk

Detection
:   Alternative construction assigns invariant-bearing fields without using the validated construction path.

Message
:   `{factory}` constructs `{type}` without the invariant checks used by `{validated_path}`.

### LIFE016 Dataclass has a behavior-heavy lifecycle { #LIFE016 }

Claim
:   design

Detection
:   A dataclass owns several transitions, effects, or lifecycle hooks beyond value behavior.

Message
:   `{class}` is declared as a dataclass but owns `{transition_count}` transitions and `{effect_count}` effects, so it no longer behaves as a simple data value.

### LIFE017 Manual resource management { #LIFE017 }

Claim
:   risk

Detection
:   A resource is acquired and released manually on paths that a context manager could own.

Message
:   `{symbol}` manually acquires and releases `{resource}` across `{path_count}` paths, leaving cleanup dependent on control flow.
