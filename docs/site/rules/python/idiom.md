# IDIOM rules

Python-specific semantics whose equivalent rules differ by language.

| ID | Rule | Claim | Concern | Default | Source | Detection/default | Message template |
|---|---|---|---|---|---|---|---|
| IDIOM001 | Process hash as identity | risk | hazard | on | HS-PURPOSE-16 | `hash()` output crosses a process boundary or enters persistent storage | `hash(value)` is persisted even though Python hashes may change between processes. |
| IDIOM002 | Context variable created in local scope | risk | hazard | on | HS-CONC-09 | `ContextVar` is created inside a function or closure | `ContextVar("request_id")` is created inside a closure, giving each invocation a new variable retained by its contexts. |
| IDIOM003 | Import path mutation | risk | hazard | on | HS-INPUT-13 | Mutation of `sys.path`, `sys.meta_path`, `sys.path_hooks` or related import machinery | `sys.path.insert()` changes process-global import resolution instead of using the package structure. |
| IDIOM004 | Dynamic namespace access | risk | hazard | on | HS-INPUT-14 | Calls to `locals()` or `globals()` | `locals()` converts implementation-local names into an implicit runtime data contract. |
| IDIOM005 | Module attribute hook | risk | hazard | on | HS-INPUT-15 | Top-level `__getattr__` or `__dir__` | Module-level `__getattr__` makes missing attributes execute dynamic lookup instead of failing normally. |
| IDIOM006 | Module object customization | risk | hazard | on | HS-INPUT-16 | Replacement or class mutation of the current module through `sys.modules` | This module replaces or mutates its own module object, making runtime behavior differ from its source namespace. |
| IDIOM007 | Mutable nonlocal closure | risk | hazard | on | HS-STATE-14 | A nested function writes a `nonlocal` binding | This returned closure mutates `failures` through `nonlocal`, hiding shared state inside lexical scope. |
| IDIOM008 | Numeric truthiness collapses absence | risk | review | hint | Replacement for HS-NARRATION-08; explicit user requirement. | A direct truthiness test is applied to a statically numeric optional value; bool is excluded. | `if not {name}` sends both `0` and `None` through this branch; if zero is valid, compare with `None` explicitly. |
| IDIOM009 | Dynamic attribute mutation | risk | hazard | on | HS-STATE-23 | Dynamic `setattr`, `delattr` or `__dict__.update()` changes object state | `setattr(target, name, value)` mutates an attribute whose existence and type are unavailable to static review. |
| IDIOM010 | Frozen state bypass | risk | hazard | on | HS-INIT-10 | Explicit `object.__setattr__` or `object.__delattr__` | `object.__setattr__` bypasses the frozen object's declared construction and mutation contract. |
| IDIOM011 | Concrete factory return | risk | hazard | on | HS-INIT-13 | Non-final classmethod constructs `cls(...)` but returns the containing class type | `Request.from_bytes()` constructs `cls` but returns `Request`, discarding the subclass-preserving contract of `Self`. |
| IDIOM012 | Stdlib idiom reimplementation | design | review | on | HS-SHAPE-17 | Code matches a curated pattern implemented by the standard library | This `try` and empty `except FileNotFoundError` reimplements `contextlib.suppress`. |
| IDIOM013 | Protocol not runtime-checkable | risk | hazard | on | HS-CLASS-12 | `Protocol` declaration lacks `@runtime_checkable` | Protocol `Repository` declares a program contract but cannot be checked with `isinstance()` at runtime. |
| IDIOM014 | Custom metaclass | risk | hazard | on | HS-CLASS-15 | Application class declares or derives from a custom metaclass | `Service` uses a custom metaclass even though no library-level class-construction requirement is evident. |
| IDIOM015 | Name mangled shadow | risk | hazard | on | HS-CLASS-19 | Base and subclass declare the same source-level mangled name | `Child.__load` does not override `Base.__load` because the two methods are mangled into different names. |
| IDIOM016 | Import inside function or method | design | advisory | hint | Prototype PY021. | An import occurs below module scope outside configured optional-dependency or cycle-breaking boundaries. | `{symbol}` imports `{module}` lazily, hiding an import dependency and possible first-call cost inside execution. |
