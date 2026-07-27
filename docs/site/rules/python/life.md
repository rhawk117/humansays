# LIFE rules

LIFE rules address construction, resource ownership, cleanup, and the implicit temporal dependencies that arise during object initialization and destruction.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| LIFE001 | Import time side effect | risk | hazard | on | HS-INPUT-07 | Module body performs I/O, network or filesystem work | Importing `{module}` performs `{effects}`, giving module loading an operational side effect. |
| LIFE002 | Constructor does work | design | review | on | HS-INPUT-08 | `__init__` performs I/O or non-trivial computation | `{class}.__init__` performs `{effects}`, so constructing the object has operational behavior. |
| LIFE003 | Post construction setup | design | review | on | HS-INIT-02 | ≥2 setup-style methods called before first use | `{class}` requires `{setup_count}` setup calls before first use, creating an implicit construction sequence. |
| LIFE004 | Traceback retention | risk | hazard | observe | HS-LEAK-03 | Instance holds an object with `__traceback__` | `{instance}` retains an exception traceback and therefore the frames and locals reachable from it. |
| LIFE005 | Finalizer dependent release | risk | hazard | observe | HS-LEAK-05 | File or socket closed by GC rather than explicitly | Resource `{resource}` was closed by garbage collection rather than an explicit owner. |
| LIFE006 | Unbounded cache | risk | hazard | observe | HS-LEAK-07 | `lru_cache(maxsize=None)` reaching N entries | Unbounded cache `{name}` reached `{entries}` entries during observation. |
| LIFE007 | Temporal coupling | design | review | on | HS-FIND-11 | cg + nam | `{type}` requires the ordered calls `{sequence}` before it becomes usable. |
| LIFE008 | Import time resource construction | risk | hazard | on | HS-INPUT-11 | Module-level construction of clients, connections, pools, executors, threads or processes | `Client()` is constructed during import, giving it process-wide lifetime without an explicit owner. |
| LIFE009 | Import time exit hook | risk | hazard | on | HS-INPUT-17 | `atexit.register()` executed during import | Importing this module registers process-global cleanup behavior through `atexit`. |
| LIFE010 | Application finalizer | risk | hazard | on | HS-STATE-24 | Application class defines `__del__` | `Connection.__del__` hides resource cleanup behind garbage-collection timing instead of an explicit owner. |
| LIFE011 | Overridable call during init | risk | hazard | on | HS-INIT-15 | Constructor calls an overridable instance method | `Base.__init__` calls overridable `configure()` before subclass state is guaranteed to exist. |
| LIFE012 | Callback during construction | risk | hazard | on | HS-INIT-16 | Constructor invokes a caller-provided callback with the object under construction | `Service.__init__` passes `self` to a callback before all fields are initialized. |
| LIFE013 | Self escapes before invariant | risk | hazard | on | HS-INIT-17 | `self` is registered, stored, scheduled or passed externally before construction completes | `self` escapes to `registry.register()` after only four of seven constructor fields are established. |
| LIFE014 | Constructor is an operation | risk | hazard | on | HS-FIND-16 | own + eff + (cf or shp) | Service.__init__ establishes 11 fields, performs two effect categories and contains five branches, so construction has become an operation. |
| LIFE015 | Construction bypasses invariant path | risk | hazard | on | Rewrite of HS-INIT-01. | Alternative construction assigns invariant-bearing fields without using the validated construction path. | `{factory}` constructs `{type}` without the invariant checks used by `{validated_path}`. |
| LIFE016 | Dataclass has a behavior-heavy lifecycle | design | review | on | Later combined catalog. | A dataclass owns several transitions, effects, or lifecycle hooks beyond value behavior. | `{class}` is declared as a dataclass but owns `{transition_count}` transitions and `{effect_count}` effects, so it no longer behaves as a simple data value. |
| LIFE017 | Manual resource management | risk | hazard | on | Later combined catalog. | A resource is acquired and released manually on paths that a context manager could own. | `{symbol}` manually acquires and releases `{resource}` across `{path_count}` paths, leaving cleanup dependent on control flow. |
