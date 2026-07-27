# State and effects

Code becomes hard to change when you cannot answer two questions by reading it:
what can write to this value, and what does calling this touch. Both questions
have answers that live outside the function you are looking at. A value bound at
module scope can be rewritten by any code that imported the module, so its
contents at the moment your function runs depend on the order in which unrelated
code happened to execute. A function that reaches the filesystem, a socket and a
subprocess has three failure modes and three setup costs that its signature does
not mention, so a caller cannot tell what a call commits them to and a test
cannot exercise one part without providing all three. Neither problem shows up as
a wrong answer. It shows up later, as a change that was supposed to be local and
was not, because ownership of the state and the reach of the effects were never
written down anywhere a reader could find them.

## 4. Trace State Ownership

For every mutable value, determine:

1. Who owns it?
2. How long should it live?
3. Who may mutate it?
4. How can other code observe it?

### Placement criteria

| State lifetime         | Recommended location                          |
| ---------------------- | --------------------------------------------- |
| One calculation        | Local variable                                |
| One request or job     | Explicit request/context object               |
| One value              | Immutable value object                        |
| One entity             | Entity instance                               |
| One stateful component | Component instance                            |
| Entire application     | Explicitly constructed application dependency |
| Beyond the process     | Repository or persistent storage              |

### Good criteria

- Mutable state has one clear owner.
- Mutation occurs through meaningful methods on that owner.
- Internal mutable collections are not returned directly.
- An object’s lifetime matches the lifetime required by its state.
- `ClassVar` is not used merely to disguise global mutable state.

```python
class CheckRegistry:
    def __init__(self) -> None:
        self._check_types: dict[str, type[Check]] = {}

    def register(self, check_type: type[Check]) -> None:
        ...

    def resolve(self, check_name: str) -> type[Check]:
        ...

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._check_types))
```

### Warning signs

- A method mutates several passed objects.
- Callers receive and modify an owner’s internal dictionary or list.
- Mutable `ClassVar` collections are shared unintentionally.
- State survives longer than the operation that needs it.
- Tests must reset global state between cases.

## 5. Trace Side Effects

Mark every interaction with:

- Database
- Network
- Filesystem
- Subprocess
- Cache
- Message broker
- Clock
- Random source
- Logging or audit sink

### Criteria

- Side effects are visible through named collaborators or boundary functions.
- Business decisions are separated from technical I/O where practical.
- A workflow makes effect ordering understandable.
- Partial-failure behavior is considered when multiple effects occur.
- Domain objects do not contain vendor-specific networking or persistence logic.

A readable flow normally resembles:

```text
Acquire input → make decisions → create result → persist or publish
```

## 6. Protect Invariants

Objects that own state should also own the rules governing that state.

### Good criteria

- Construction produces a valid, usable object.
- Invalid values are rejected during construction.
- Entities expose domain transitions rather than generic setters.
- Callers cannot bypass important transition rules.
- Failed operations preserve valid state.

Prefer:

```python
user.activate()
account.withdraw(amount)
```

Over:

```python
user.status = UserStatus.ACTIVE
account.balance -= amount
```

Avoid temporal coupling:

```python
client = ApiClient()
client.configure(settings)
client.authenticate()
client.connect()
```

Prefer construction that establishes validity:

```python
client = ApiClient(
    settings=settings,
    credentials=credentials,
)
```

## Further reading

The ownership questions above are the ones Martin Fowler's
[Encapsulate Variable](https://refactoring.com/catalog/encapsulateVariable.html)
refactoring exists to answer: the refactoring moves a widely reachable piece of
data behind functions precisely so that "who may mutate it" has a place to be
written down. The separation in section 5 between deciding something and doing
something is Bertrand Meyer's command-query separation, summarised with its
caveats in Fowler's
[CommandQuerySeparation](https://martinfowler.com/bliki/CommandQuerySeparation.html).
For the `ClassVar` criterion specifically,
[PEP 526](https://peps.python.org/pep-0526/) defines what the annotation does and
what it does not do, and
[`typing.ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar)
is the reference entry: it marks a name as class scoped for a type checker and
has no effect on whether the object it names is shared or mutable at runtime.

## What enforces this

Four shipped rules detect shapes described on this page. Each is a review lead
read off the syntax tree, not a verdict, and none of them executes the code being
scanned.

Section 4, state ownership:

- [`HS004 shared-mutable-state`](../rules/state-and-boundaries.md#hs004-shared-mutable-state)
    fires on a mutable value assigned in a module body or a class body. This is the
    "state survives longer than the operation that needs it" warning sign, and it
    is the only rule that reaches the `ClassVar` criterion, since a mutable
    collection assigned in a class body is flagged whether or not it carries a
    `ClassVar` annotation.
- [`HS006 multiple-mutation-owners`](../rules/state-and-boundaries.md#hs006-multiple-mutation-owners)
    fires when one function body writes to three or more distinct owners, where an
    owner is `self`, a parameter, or a module-level name. This is the "a method
    mutates several passed objects" warning sign, and it is also where the
    partial-failure criterion in section 5 becomes visible.

Section 5, side effects:

- [`HS007 mixed-boundaries`](../rules/state-and-boundaries.md#hs007-mixed-boundaries)
    fires when one function body names three or more of four categories of
    standard-library boundary module: `database`, `filesystem`, `network`,
    `process`. The match is on resolved import aliases, so it reports that three
    kinds of outside world are *named* in one body. A resolved reference to
    `subprocess.run` is evidence that the function may start a process; the scanner
    never runs the code, so it cannot say whether the call is taken, guarded, or
    unreachable. Only standard-library modules are listed, so a database reached
    through a third-party driver contributes nothing.
- [`HS021 lazy-import`](../rules/failure-and-imports.md#hs021-lazy-import)
    fires on any import statement inside a function body. A deferred import moves
    the cost and the failure mode of loading a module from load time to call time,
    which makes it an effect of calling the function rather than of importing the
    module. The rule cannot tell a deliberate cycle break or optional dependency
    from an import added in place, which is why it is an advisory.

Section 6, invariants, has no rule of its own. Nothing in the shipped set detects
temporal coupling, generic setters standing in for domain transitions, or state
left invalid after a failed operation. The closest signal is
[`HS014 validated-argument-bundle`](../rules/function-shape.md#hs014-validated-argument-bundle),
which fires when a function already over the argument threshold validates one of
those arguments in its body. That points at a bundle of values whose invariants
have no owning type yet, which is the "invalid values are rejected during
construction" criterion approached from the calling side rather than from the
object.
