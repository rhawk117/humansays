# Future Additions

A running list of post-mvp rules to add, some more opinnionated than others



- Rules for detecting code that does something a stdlib module does (e.g `contextlib.supress`)
- A notice for reference cycles
- Using `object` over `typing.Any`, type checkers prefer any much more.
- Factory method using class name return type instead of `Self`; misleading type checker eval for inheritance
- Not using `enum.auto()` when it makes more sense and it's semantically the the same.
- Not using `dataclasses(kw_only=True)` when attribute count >3 or share a similar type signature or not `slots=True` when it makes sense.
- The use of literals or expressions as the thing iterate on in a for loop (e.g `for i in (1, 2, 3)`)
- A function accepts a class or object and only one attribute is accessed of it; coupling
- The use of a complicated tuple return type instead of NamedTuple which is a more readable type alias which is functionally the same
- The use of global reference types which populate the global namespace, have import side effects which can be moved to functions to create on demand for the duration they are needed and are easier to test than a constant
- The use of the `global` keyword as a warning, especially in contexts of module state management where a value starts out as one
- Dynamic analysis of potential race conditions & concurrency related bugs for async code and code with locks, threadpools, multi-processing etc.
- The use of `os.environ` outside of testing contexts over `os.getenv`, opinnonated one
- The use of `abc` over a protocol or a protocol missing the `@runtime_checkable` decorator
- A class with more than 2 generics
- A class with more than 6 private methods
- Not using with (context1 as context, context2 as context2) and instead double nesting
- A try except block with more than 6 different exception blocks, consider moving to a context manager
- The use of `object.__setattr__` in a frozen dataclass and other "hacks"
- A for/while loop block with more than 10 lines of code, body could be extracted to a function and condensed to comprehension or map function (for loop related).
- Weird and opinnionated one, groups of related constants should be extracted to a dataclass with the defaults being those values and then dependants use DI for it so it's not an "undeclared" dependency.
- Function silent mutates a reference type the caller passed and does not own, semantics for this one are a little fuzzy.
- Any use of metaclasses outside of library code
- Opinnonated one; decorators should be "classes" with __call__ instead of functions so they can expose easier testing overrides and to reduce heavy nesting. Closure garbage collection is harder to reason about than class related garbage collection
- Code which has a dataclass and turns the object into a `dict` essentially and doesn't use `asdict`
- The use of `properties` incorrectly can make the caller incorrectly assume that invocation is cheap and access it multiple times without storing a local instead.
- Opinnionated: doing a loop after an if check, 3 layers of nesting for one branch of code and exceptionally hard to read
- An if statement with more than 3 boolean expressions not being a function, easier to test
- ANY use of the `locals` or `globals` function
- Using `sys.path.insert()` as a hack instead of running the file as a module.
- Not using `@final` in an abstract class for methods which child classes should not override
- 