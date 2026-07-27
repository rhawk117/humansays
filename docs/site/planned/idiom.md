# IDIOM rules

Python-specific semantics whose equivalent rules differ by language.

These rules are planned. None of them is available in a release yet.

The conventions behind this domain come from
[PEP 20, the Zen of Python](https://peps.python.org/pep-0020/) and
[PEP 8, the style guide for Python code](https://peps.python.org/pep-0008/).

| ID | Rule | Default | Concern |
|---|---|---|---|
| IDIOM001 | Process hash as identity | on | hazard |
| IDIOM002 | Context variable created in local scope | on | hazard |
| IDIOM003 | Import path mutation | on | hazard |
| IDIOM004 | Dynamic namespace access | on | hazard |
| IDIOM005 | Module attribute hook | on | hazard |
| IDIOM006 | Module object customization | on | hazard |
| IDIOM007 | Mutable nonlocal closure | on | hazard |
| IDIOM008 | Numeric truthiness collapses absence | hint | review |
| IDIOM009 | Dynamic attribute mutation | on | hazard |
| IDIOM010 | Frozen state bypass | on | hazard |
| IDIOM011 | Concrete factory return | on | hazard |
| IDIOM012 | Stdlib idiom reimplementation | on | review |
| IDIOM013 | Protocol not runtime-checkable | on | hazard |
| IDIOM014 | Custom metaclass | on | hazard |
| IDIOM015 | Name mangled shadow | on | hazard |
| IDIOM016 | Import inside function or method | hint | advisory |

## Rule details

### IDIOM001 Process hash as identity

- **Claim:** risk
- **Detection/default:** `hash()` output crosses a process boundary or enters persistent storage
- **Message template:** `hash(value)` is persisted even though Python hashes may change between processes.

### IDIOM002 Context variable created in local scope

- **Claim:** risk
- **Detection/default:** `ContextVar` is created inside a function or closure
- **Message template:** `ContextVar("request_id")` is created inside a closure, giving each invocation a new variable retained by its contexts.

### IDIOM003 Import path mutation

- **Claim:** risk
- **Detection/default:** Mutation of `sys.path`, `sys.meta_path`, `sys.path_hooks` or related import machinery
- **Message template:** `sys.path.insert()` changes process-global import resolution instead of using the package structure.

### IDIOM004 Dynamic namespace access

- **Claim:** risk
- **Detection/default:** Calls to `locals()` or `globals()`
- **Message template:** `locals()` converts implementation-local names into an implicit runtime data contract.

### IDIOM005 Module attribute hook

- **Claim:** risk
- **Detection/default:** Top-level `__getattr__` or `__dir__`
- **Message template:** Module-level `__getattr__` makes missing attributes execute dynamic lookup instead of failing normally.

### IDIOM006 Module object customization

- **Claim:** risk
- **Detection/default:** Replacement or class mutation of the current module through `sys.modules`
- **Message template:** This module replaces or mutates its own module object, making runtime behavior differ from its source namespace.

### IDIOM007 Mutable nonlocal closure

- **Claim:** risk
- **Detection/default:** A nested function writes a `nonlocal` binding
- **Message template:** This returned closure mutates `failures` through `nonlocal`, hiding shared state inside lexical scope.

### IDIOM008 Numeric truthiness collapses absence

- **Claim:** risk
- **Detection/default:** A direct truthiness test is applied to a statically numeric optional value; bool is excluded.
- **Message template:** `if not {name}` sends both `0` and `None` through this branch; if zero is valid, compare with `None` explicitly.

### IDIOM009 Dynamic attribute mutation

- **Claim:** risk
- **Detection/default:** Dynamic `setattr`, `delattr` or `__dict__.update()` changes object state
- **Message template:** `setattr(target, name, value)` mutates an attribute whose existence and type are unavailable to static review.

### IDIOM010 Frozen state bypass

- **Claim:** risk
- **Detection/default:** Explicit `object.__setattr__` or `object.__delattr__`
- **Message template:** `object.__setattr__` bypasses the frozen object's declared construction and mutation contract.

### IDIOM011 Concrete factory return

- **Claim:** risk
- **Detection/default:** Non-final classmethod constructs `cls(...)` but returns the containing class type
- **Message template:** `Request.from_bytes()` constructs `cls` but returns `Request`, discarding the subclass-preserving contract of `Self`.

### IDIOM012 Stdlib idiom reimplementation

- **Claim:** design
- **Detection/default:** Code matches a curated pattern implemented by the standard library
- **Message template:** This `try` and empty `except FileNotFoundError` reimplements `contextlib.suppress`.

### IDIOM013 Protocol not runtime-checkable

- **Claim:** risk
- **Detection/default:** `Protocol` declaration lacks `@runtime_checkable`
- **Message template:** Protocol `Repository` declares a program contract but cannot be checked with `isinstance()` at runtime.

### IDIOM014 Custom metaclass

- **Claim:** risk
- **Detection/default:** Application class declares or derives from a custom metaclass
- **Message template:** `Service` uses a custom metaclass even though no library-level class-construction requirement is evident.

### IDIOM015 Name mangled shadow

- **Claim:** risk
- **Detection/default:** Base and subclass declare the same source-level mangled name
- **Message template:** `Child.__load` does not override `Base.__load` because the two methods are mangled into different names.

### IDIOM016 Import inside function or method

- **Claim:** design
- **Detection/default:** An import occurs below module scope outside configured optional-dependency or cycle-breaking boundaries.
- **Message template:** `{symbol}` imports `{module}` lazily, hiding an import dependency and possible first-call cost inside execution.
